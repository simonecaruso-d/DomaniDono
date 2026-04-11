# Environment Setting
import base64
import random
import streamlit as st

import app.ui.AdaptiveUI as AdaptiveUI
import configuration.StreamlitConfiguration as Configuration

# Helpers
def GetBase64Logo(logoPath = Configuration.LogoPath):
    'Load the logo image and return it as a base64-encoded string for embedding in HTML.'
    with open(logoPath, "rb") as logoFile: return base64.b64encode(logoFile.read()).decode()

def ScalePx(value, minimum=1):
    'Scale pixel values using the responsive scale configured for the app.'
    return AdaptiveUI.ScalePx(value, Configuration.ResponsiveScale, minimum=minimum)

def GetTargetLoadSeconds(minSeconds=10, maxSeconds=20):
    'Return a random target loading duration in seconds for the first app load.'
    return random.randint(minSeconds, maxSeconds)

# CSS
def HideRunningIndicatorCss():
    'Return CSS to hide Streamlit\'s default running indicator and style the custom loader.'
    loaderMessageMaxWidth = ScalePx(760)
    loaderBarWidth        = ScalePx(320)
    loaderBarHeight       = ScalePx(8)
    spacing2Px            = f'{Configuration.Spacing2}px'
    spacing3Px            = f'{Configuration.Spacing3}px'
    spacing4Px            = f'{Configuration.Spacing4}px'
    fontSizeTitle         = getattr(Configuration, 'FontSize125', '1.25rem')
    fontSizeSubtitle      = getattr(Configuration, 'FontSize95', '0.95rem')
    fontSizeMessage       = getattr(Configuration, 'FontSize110', '1.1rem')
    fontSizeCountdown     = getattr(Configuration, 'FontSize120', '1.2rem')
    fontSizeLabel         = getattr(Configuration, 'FontSize90', '0.9rem')
    glowOpacity           = '0.45'

    return f"""<style>
        [data-testid="stStatusWidget"] {{ display: none !important; }}
        .loader-container {{display: flex; flex-direction: column; align-items: center; justify-content: center; height: 70vh; gap: {spacing4Px}; padding: {spacing3Px}; background: linear-gradient(135deg, {Configuration.Palette1A} 0%, {Configuration.Palette2B} 50%, {Configuration.Palette3E} 100%); border-radius: {Configuration.RadiusCard}px; box-shadow: 0 {spacing2Px} {spacing4Px} rgba(0,0,0,0.24);}}
        .loader-title {{
            font-size: {fontSizeTitle} !important; font-weight: {Configuration.FontWeight6} !important;
            font-family: {Configuration.FontFamily} !important; color: {Configuration.WhiteColor} !important; text-shadow: 0 2px 12px rgba(0,0,0,0.4);
            letter-spacing: {Configuration.LetterSpacing2} !important; line-height: {Configuration.LineHeight3} !important;
            animation: glow 2.5s ease-in-out infinite alternate;}}
        .loader-subtitle {{
            font-size: {fontSizeSubtitle} !important; font-weight: {Configuration.FontWeight4} !important;
            font-family: {Configuration.FontFamily} !important; color: {Configuration.WhiteColor} !important; opacity: 0.92;
            letter-spacing: {Configuration.LetterSpacing1} !important; text-transform: uppercase;}}
        .loader-countdown {{
            display: flex; align-items: baseline; justify-content: center; gap: {spacing2Px};
            color: {Configuration.WhiteColor} !important; margin-top: -{spacing2Px};}}
        .loader-countdown-value {{
            position: relative; display: grid; min-width: {ScalePx(84)}px; height: {ScalePx(44)}px;
            font-size: {fontSizeCountdown} !important; font-weight: {Configuration.FontWeight6} !important;
            line-height: 1; text-align: center;}}
        .loader-countdown-item {{ grid-area: 1 / 1; opacity: 0; }}
        .loader-countdown-label {{
            font-size: {fontSizeLabel} !important; font-weight: {Configuration.FontWeight4} !important;
            opacity: 0.92; }}
        @keyframes glow {{ 0% {{ text-shadow: 0 0 12px rgba(255,255,255,{glowOpacity}); }} 100% {{ text-shadow: 0 4px 24px rgba(255,255,255,1); }} }}
        .loader-message {{
            font-size: {fontSizeMessage} !important; font-weight: {Configuration.FontWeight4} !important; line-height: {Configuration.LineHeight4} !important;
            font-family: {Configuration.FontFamily} !important; color: {Configuration.WhiteColor} !important; text-align: center; max-width: {loaderMessageMaxWidth}px; width: 100%;
            display: flex; align-items: center; justify-content: center;
            animation: fadeInUp 1s ease-out; padding: {spacing2Px}; background: rgba(255,255,255,0.12); backdrop-filter: blur(16px); border-radius: {Configuration.RadiusInput}px; border: 1px solid rgba(255,255,255,0.24);}}
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(24px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .loader-bar-track {{width: {loaderBarWidth}px; height: {loaderBarHeight}px; background: rgba(255,255,255,0.24); border-radius: {Configuration.RadiusInput}px; overflow: hidden; margin-top: {spacing3Px}; box-shadow: inset 0 2px 8px rgba(0,0,0,0.1); position: relative;}}
        .loader-bar-fill {{position: absolute; top: 0; left: -35%; width: 35%; height: 100%; border-radius: {Configuration.RadiusInput}px; background: linear-gradient(90deg, {Configuration.Palette2D} 0%, {Configuration.Palette2F} 50%, {Configuration.Palette1F} 100%); box-shadow: 0 0 24px rgba(255,255,255,0.45); animation: loaderSweep 1.6s ease-in-out infinite;}}
        .weather-emoji {{ font-size: 4em; animation: weatherFloat 3s ease-in-out infinite; margin-bottom: {spacing2Px}; filter: drop-shadow(0 4px 12px rgba(0,0,0,0.3)); }}
        @keyframes weatherFloat {{ 0%, 100% {{ transform: translateY(0) rotate(0deg); }} 50% {{ transform: translateY(-12px) rotate(5deg); }} }}
        @keyframes loaderSweep {{ 0% {{ left: -35%; }} 100% {{ left: 100%; }} }}
    </style>"""

def LoaderRotationCss(totalDuration, visibleUntil, fadeUntil):
    'Return CSS to rotate loader messages without rerunning Streamlit.'
    return f"""<style>
        .loader-message-rotating {{position: relative; display: grid; width: 100%; min-height: {ScalePx(120)}px; overflow: hidden; animation: none; place-items: center;}}
        .loader-message-item {{grid-area: 1 / 1; width: 100%; opacity: 0; text-align: center; display: flex; align-items: center; justify-content: center; animation: loaderMessageRotate {totalDuration}s infinite;}}
        @keyframes loaderMessageRotate {{
            0%, {visibleUntil}% {{ opacity: 1; transform: translateY(0); }}
            {fadeUntil}%, 100% {{ opacity: 0; transform: translateY(10px); }}}}
    </style>"""

def LoaderCountdownCss(stepDuration):
    'Return CSS to animate a countdown without rerunning Streamlit.'
    return f"""<style>
        .loader-countdown-item {{animation: loaderCountdownStep {stepDuration}s ease-in-out both;}}
        @keyframes loaderCountdownStep {{
            0% {{ opacity: 0; transform: translateY(10px) scale(0.985); filter: blur(1.5px); }}
            18% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
            78% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
            100% {{ opacity: 0; transform: translateY(-10px) scale(1.015); filter: blur(1.5px); }}
        }}
        .loader-countdown-item-last {{animation: loaderCountdownLast 0.9s ease-out both;}}
        @keyframes loaderCountdownLast {{
            0% {{ opacity: 0; transform: translateY(10px) scale(0.985); filter: blur(1.5px); }}
            100% {{ opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }}
        }}
    </style>"""

# Loader
def RenderLoader(message = None, targetDurationSeconds = 15):
    'Render a custom loading screen once and return its placeholder so the caller can clear it after loading.'
    st.markdown(HideRunningIndicatorCss(), unsafe_allow_html=True)

    logoBase64        = GetBase64Logo()
    slot              = st.empty()
    messagesPool      = list(Configuration.LoadingMessages)
    random.shuffle(messagesPool)
    messages          = [message] if message else messagesPool
    messageCount      = len(messages)
    messageDuration   = max(3, round(float(targetDurationSeconds) / max(1, messageCount), 2))
    totalDuration     = round(messageCount * messageDuration, 2)
    visibleUntil      = round(80 / messageCount, 4)
    fadeUntil         = round(100 / messageCount, 4)
    countdownDuration = max(1, int(round(float(targetDurationSeconds))))
    countdownStep     = round(float(targetDurationSeconds) / countdownDuration, 3)
    st.markdown(LoaderCountdownCss(countdownStep), unsafe_allow_html=True)

    countdownItems = ''.join(
        f"<div class='loader-countdown-item' style='animation-delay: {round(index * countdownStep, 3)}s;'>{(countdownDuration - index) // 60:02d}:{(countdownDuration - index) % 60:02d}</div>"
        for index in range(countdownDuration)) + f"<div class='loader-countdown-item loader-countdown-item-last' style='animation-delay: {round(float(targetDurationSeconds), 3)}s;'>00:00</div>"
    if messageCount == 1: messageHtml = f"<div class='loader-message'>{messages[0]}</div>"
    else:
        st.markdown(LoaderRotationCss(totalDuration, visibleUntil, fadeUntil), unsafe_allow_html=True)
        messageItems = ''.join(f"<div class='loader-message-item' style='animation-delay: -{round(index * messageDuration, 3)}s;'>{currentMessage}</div>" for index, currentMessage in enumerate(messages))
        messageHtml = f"<div class='loader-message loader-message-rotating'>{messageItems}</div>"

    slot.markdown(f"""
            <div class='loader-container'><div class='weather-emoji'><img src="data:image/png;base64,{logoBase64}" width="{ScalePx(80)}"></div>
            <div class='loader-title'>Domani Dono</div>
            <div class='loader-subtitle'>Attesa stimata</div>
            <div class='loader-countdown'><div class='loader-countdown-value'>{countdownItems}</div><div class='loader-countdown-label'>min:sec</div></div>
            {messageHtml}
            <div class='loader-bar-track'><div class='loader-bar-fill'></div></div></div>""", unsafe_allow_html=True)

    return slot