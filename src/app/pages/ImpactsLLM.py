# Environment Setting
from openai import OpenAI
import pandas as pd
from pathlib import Path
import re
import streamlit as st
import sys
import time
import markdown

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import configuration.StreamlitConfiguration as Configuration
import app.ui.Layout                        as UI

# Logic
def BuildLlmModelSequence(defaultModel, fallbackModels):
    'Builds a sequence of LLM models to try, starting with a cached model if available, followed by the default model and any fallback models, ensuring uniqueness and preserving order.'
    cachedModel   = st.session_state.get('_llm_last_successful_model')
    modelSequence = [cachedModel, defaultModel, *(fallbackModels or [])]

    uniqueModels = []
    for currentModel in modelSequence:
        if currentModel and currentModel not in uniqueModels: uniqueModels.append(currentModel)

    return uniqueModels

def IsRetryableLlmError(error):
    'Determines if an error from the LLM provider is retryable based on its message content, checking for common indicators of rate limiting or temporary issues.'
    errorText = str(error).lower()
    return any(token in errorText for token in ['429', 'rate limit', 'rate-limit', 'rate_limited', 'temporarily rate-limited', 'temporarily rate limited', 'too many requests', 'connection error', 'timed out', 'timeout'])

def BuildFriendlyLlmError(error):
    'Builds a user-friendly error message based on the type of error encountered when interacting with the LLM provider, providing specific guidance for retryable errors and a general message for other types of errors.'
    if IsRetryableLlmError(error): return '⚠️ The AI Provider is temporarily busy. Please try again in a few seconds.'
    return f'⚠️ Error generating recommendations: {str(error)}'

def EscapeMarkdownCell(value):
    'Escapes markdown-sensitive table cell content to keep deterministic rendering.'
    if pd.isna(value): return ''
    text = str(value)
    text = text.replace('|', '\\|')
    text = text.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')
    return text

def BuildSummaryMarkdownTable(summaryDf):
    'Builds a deterministic markdown table from the summary dataframe.'
    if summaryDf is None or summaryDf.empty: return '| No data |\n|---|\n| No rows available |'

    safeDf   = summaryDf.copy()
    columns  = [str(column) for column in safeDf.columns]
    header   = '| ' + ' | '.join(columns) + ' |'
    divider  = '| ' + ' | '.join(['---'] * len(columns)) + ' |'

    rows = []
    for _, row in safeDf.iterrows():
        cells = [EscapeMarkdownCell(row[column]) for column in safeDf.columns]
        rows.append('| ' + ' | '.join(cells) + ' |')

    return '\n'.join([header, divider] + rows)

def EnsureMarkdownFromStart(markdownText):
    'Ensures response starts from the first character with a markdown heading.'
    content = (markdownText or '').lstrip()
    if not content.startswith('#'): content = '### Recommendations\n\n' + content
    return content

def EnsureTablePresent(markdownText, summaryMarkdownTable):
    'Removes any LLM-generated tables and ensures deterministic static sections are present.'
    content              = EnsureMarkdownFromStart(markdownText)
    tablePattern         = r'\|[^\n]*\|(?:\n\|[-:\s|]*\|)*(?:\n\|[^\n]*\|)*'
    contentWithoutTables = re.sub(tablePattern, '', content)
    contentWithoutTables = re.sub(r'\n\n+', '\n\n', contentWithoutTables).strip() 
    
    staticDimensionsBlock = (Configuration.LLMDimensionsGlossary or '').strip()
    staticRankingBlock    = '### Multi-dimensional Ranking (Top 7)\n' + summaryMarkdownTable
    staticPrelude         = staticDimensionsBlock + '\n\n' + staticRankingBlock
    
    headingEnd = contentWithoutTables.find('\n')
    if headingEnd == -1: return contentWithoutTables + '\n\n' + staticPrelude
    
    firstLine = contentWithoutTables[:headingEnd].strip()
    rest      = contentWithoutTables[headingEnd + 1:].lstrip('\n')
    return firstLine + '\n\n' + staticPrelude + ('\n\n' + rest if rest else '')

def GenerateLLMComment(summaryDf, systemPrompt=Configuration.LLMPrompt,
                       orApiKey=Configuration.ORApiKey, 
                       model=Configuration.WinnerModel, fallbackModels=Configuration.LlmFallbackModels, 
                       maxRetries=Configuration.LlmMaxRetries, retryDelaySeconds=Configuration.LlmRetryDelaySeconds,
                       maxTokens=Configuration.MaxTokens, temperature=Configuration.Temperature, topP=Configuration.TopP):
    'Generates donation guidance from the LLM using all chart tables and multi-dimensional heuristics.'
    try:
        generationStart      = time.perf_counter()
        payloadStart         = time.perf_counter()
        summaryMarkdownTable = BuildSummaryMarkdownTable(summaryDf)
        print(f'[LLM] Payload build completed in {(time.perf_counter() - payloadStart):.2f}s')
        filledPrompt         = systemPrompt.format(summaryMarkdownTable=summaryMarkdownTable)
        print(f'[LLM] Prompt size: {len(filledPrompt)} chars')

        client       = OpenAI(base_url='https://openrouter.ai/api/v1', api_key=orApiKey)
        lastError    = None

        for currentModel in BuildLlmModelSequence(model, fallbackModels):
            for attempt in range(1, maxRetries + 1):
                requestStart = time.perf_counter()
                firstChunkLogged = False
                modelResponse = ''
                print(f'[LLM] Request start | model={currentModel} | attempt={attempt}')

                try:
                    stream = client.chat.completions.create(model=currentModel, max_tokens=maxTokens, temperature=temperature, top_p=topP, stream=True, messages=[{'role': 'system', 'content': 'You are a data-driven philanthropic advisor. Respond only in strict markdown, starting at first character with a heading, and preserve the provided ranking table exactly.'}, {'role': 'user', 'content': filledPrompt}])
                    for chunk in stream:
                        delta = chunk.choices[0].delta.content
                        if delta:
                            modelResponse += delta
                            if not firstChunkLogged:
                                print(f'[LLM] TTFT {time.perf_counter() - requestStart:.2f}s | model={currentModel} | attempt={attempt}')
                                firstChunkLogged = True

                    finalResponse = EnsureTablePresent(modelResponse, summaryMarkdownTable)
                    yield finalResponse

                    st.session_state['_llm_last_successful_model'] = currentModel
                    print(f'[LLM] Request completed in {time.perf_counter() - requestStart:.2f}s | total generation {(time.perf_counter() - generationStart):.2f}s | model={currentModel} | attempt={attempt}')
                    return
                except Exception as currentError:
                    lastError = currentError
                    print(f'[LLM] Model {currentModel} failed on attempt {attempt} after {(time.perf_counter() - requestStart):.2f}s: {currentError}')

                    if IsRetryableLlmError(currentError) and attempt < maxRetries:
                        time.sleep(retryDelaySeconds * attempt)
                        continue

                    break

        if lastError is not None:
            yield BuildFriendlyLlmError(lastError)
            return

    except Exception as e: yield BuildFriendlyLlmError(e)

# Rendering
def DonationInsightsCss(radiusCard=Configuration.RadiusCard + 15):
    'Returns CSS styles for the AI donation insights section.'
    return f"""<style>
        .llm-insights-shell {{border-radius: {radiusCard}px; background: linear-gradient(150deg, rgba(255,255,255,0.97) 0%, rgba(246,251,250,0.98) 100%); border: 1px solid rgba(75, 188, 142, 0.28); box-shadow: 0 14px 32px rgba(28, 110, 125, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78); padding: {Configuration.Spacing2}px; margin-top: {Configuration.Spacing1}px; box-sizing: border-box; overflow: hidden;}}

        /* Streamlit renders widgets outside markdown wrappers, so keep selectors global and specific */
        div[data-testid="stSpinner"] p,
        div[data-testid="stSpinner"] span,
        div[data-testid="stSpinner"] div,
        div[data-testid="stSpinner"] svg {{color: {Configuration.Palette2B} !important; fill: {Configuration.Palette2B} !important;}}
        div[data-testid="stButton"] > button[kind="primary"] {{background: {Configuration.Palette2B} !important; color: {Configuration.WhiteColor} !important; border: 1px solid {Configuration.Palette2B} !important; border-radius: 999px !important; font-family: {Configuration.FontFamily} !important; font-weight: {Configuration.FontWeight5} !important; transition: all 150ms ease !important; margin-top: {Configuration.Spacing2}px !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stButton"] > button[kind="primary"]:hover,
        div[data-testid="stButton"] > button[kind="primary"]:focus,
        div[data-testid="stButton"] > button[kind="primary"]:active,
        div[data-testid="stButton"] > button[kind="primary"]:focus-visible,
        div[data-testid="stButton"] > button[kind="primary"]:focus:not(:active) {{background: {Configuration.Palette2C} !important; border-color: {Configuration.Palette2C} !important; color: {Configuration.WhiteColor} !important; box-shadow: none !important; outline: none !important;}}
        .llm-response-card {{border-radius: {radiusCard - 10}px; background: linear-gradient(145deg, rgba(255,255,255,0.99) 0%, rgba(248,253,251,0.99) 100%); border: 1px solid rgba(75, 188, 142, 0.22); box-shadow: 0 12px 28px rgba(28, 110, 125, 0.12), inset 0 1px 0 rgba(255, 255, 255, 0.78); padding: {Configuration.Spacing2}px; margin-top: {Configuration.Spacing2}px; box-sizing: border-box; overflow: hidden;}}
        .llm-response-inner {{width: 100%; max-width: 100%; margin: 0; padding: 10px 12px; box-sizing: border-box;}}
        .llm-response-inner,
        .llm-response-inner p,
        .llm-response-inner li,
        .llm-response-inner span,
        .llm-response-inner strong,
        .llm-response-inner em,
        .llm-response-inner code,
        .llm-response-inner td,
        .llm-response-inner th {{color: {Configuration.Palette2B} !important; font-family: {Configuration.FontFamily} !important; font-size: {Configuration.FontSize85} !important; line-height: {Configuration.LineHeight4} !important;}}
        .llm-response-inner h1,
        .llm-response-inner h2,
        .llm-response-inner h3,
        .llm-response-inner h4,
        .llm-response-inner h5,
        .llm-response-inner h6 {{color: {Configuration.Palette2B} !important; font-family: {Configuration.FontFamily} !important; font-weight: {Configuration.FontWeight6} !important; letter-spacing: {Configuration.LetterSpacing1} !important; line-height: {Configuration.LineHeight3} !important; margin-top: 0.4rem !important; margin-bottom: 0.45rem !important;}}
        .llm-response-inner h1,
        .llm-response-inner h2 {{font-size: {Configuration.FontSize100} !important;}}
        .llm-response-inner h3,
        .llm-response-inner h4 {{font-size: {Configuration.FontSize95} !important;}}
        .llm-response-inner h5,
        .llm-response-inner h6 {{font-size: {Configuration.FontSize90} !important;}}
        .llm-response-inner table {{border-collapse: collapse; width: max-content; min-width: 100%; max-width: none; margin-top: {Configuration.Spacing1}px; border-radius: {Configuration.Border2}; overflow: hidden;}}
        .llm-response-inner th {{background: {Configuration.Palette2B}; color: {Configuration.WhiteColor} !important; padding: 8px 10px; font-weight: {Configuration.FontWeight5};}}
        .llm-response-inner td {{background: rgba(255,255,255,0.62); padding: 8px 10px; border-bottom: 1px solid rgba(47, 72, 88, 0.08); white-space: nowrap;}}
    </style>"""

def BuildLlmResponseHtml(responseText):
    'Wraps the LLM response in a full-width card with a narrower inner text container.'
    return f"<div class='llm-response-card'><div class='llm-response-inner'><div class='llm-insights-body'>{responseText}</div></div></div>"

@st.fragment
def RenderDonationInsights(summaryDf):
    'Renders the full AI donation insights block and handles generation.'
    st.markdown(DonationInsightsCss(), unsafe_allow_html=True)
    UI.ObjectTitleCss(Configuration.Palette2B, classSuffix='donation-insights')
    UI.ObjectSubtitleCss(Configuration.Palette2C, classSuffix='donation-insights')
    st.markdown("<div class='object-title-wrap-donation-insights'><div class='object-title-donation-insights'>Who should I donate to?</div>", unsafe_allow_html=True)
    st.markdown("<p class='object-subtitle-donation-insights'>AI-powered donation recommendations</p></div>", unsafe_allow_html=True)

    st.markdown("<div class='llm-insights-shell'>", unsafe_allow_html=True)
    generatedNow = False
    st.markdown('<br>', unsafe_allow_html=True)

    if st.button('Generate Donation Recommendations', width='stretch', type='primary', key='impacts_llm_generate'):
        generatedNow = True
        placeholder = st.empty()
        accumulatedResponse = ''

        with st.spinner('Analyzing data from the charts...'):
            for chunk in GenerateLLMComment(summaryDf):
                accumulatedResponse += chunk
                htmlContent = markdown.markdown(EnsureMarkdownFromStart(accumulatedResponse), extensions=['tables'])
                fullHtml    = f"<div class='llm-response-card'><div class='llm-response-inner'>{htmlContent}</div></div>"
                placeholder.markdown(fullHtml, unsafe_allow_html=True)

            st.session_state['impacts_llm_response'] = accumulatedResponse

    if st.session_state.get('impacts_llm_response') and not generatedNow:
        htmlContent = markdown.markdown(EnsureMarkdownFromStart(st.session_state['impacts_llm_response']), extensions=['tables'])
        fullHtml    = f"<div class='llm-response-card'><div class='llm-response-inner'>{htmlContent}</div></div>"
        st.markdown(fullHtml, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)