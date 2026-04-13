# Environment Setting
import base64
from pathlib import Path
import streamlit as st
import sys

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import configuration.StreamlitConfiguration as Configuration
import app.ui.Layout                        as UI

# CSS
def HomePageCss(radiusCard=Configuration.RadiusCard + 15):
	'Returns scoped CSS for Home content containers and logo carousel.'
	return f"""<style>
		.home-content-card {{border-radius: {radiusCard}px; background: {Configuration.WhiteColor}; border: 1px solid rgba(72, 90, 115, 0.18); box-shadow: 0 14px 32px rgba(47, 72, 88, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.82); padding: {Configuration.Spacing3}px {Configuration.Spacing2}px; overflow: hidden;}}

		.home-how-list {{margin: 0; padding-left: 22px; color: {Configuration.Palette1B}; font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize75}; line-height: {Configuration.LineHeight4};}}
		.home-how-list li {{margin: 0 0 8px 0; font-weight: {Configuration.FontWeight3};}}
		.home-how-list li:last-child {{margin-bottom: 0;}}
		.home-how-list strong {{color: {Configuration.Palette1A}; font-weight: {Configuration.FontWeight6};}}
		.home-how-story {{margin: 0; color: {Configuration.Palette1B}; font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize75}; line-height: {Configuration.LineHeight4}; font-weight: {Configuration.FontWeight3};}}
		.home-how-story + .home-how-story {{margin-top: 8px;}}
		.home-how-story strong {{color: {Configuration.Palette1A}; font-weight: {Configuration.FontWeight6};}}
		.home-how-inner {{max-width: 92%; margin: 0 auto; padding-top: {Configuration.Spacing2}px; padding-right: {Configuration.Spacing2}px; padding-bottom: {Configuration.Spacing3}px; padding-left: {Configuration.Spacing2}px; border-radius: {Configuration.Border3}px; background: {Configuration.WhiteColor}; border: none;}}
		.home-how-guide-title {{display: none;}}
		.home-bottom-spacer {{display: block; width: 100%; height: 1.25em;}}
	
		.home-data-source {{display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 16px; text-align: center;}}
		.home-data-source-logo {{width: 120px; height: 80px; display: flex; align-items: center; justify-content: center; background: {Configuration.WhiteColor}; border-radius: {Configuration.Border3}px;}}
		.home-data-source-logo img {{max-width: 100%; max-height: 100%; object-fit: contain;}}
		.home-data-source-text {{font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize105}; color: {Configuration.Palette1B}; font-weight: {Configuration.FontWeight5}; margin: 0;}}
		.home-data-source-text strong {{color: {Configuration.Palette1A}; font-weight: {Configuration.FontWeight7};}}
		.home-data-source-note {{font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize105}; color: {Configuration.Palette1B} !important; font-weight: {Configuration.FontWeight4}; line-height: {Configuration.LineHeight4}; margin: 0;}}
		.home-data-source-note * {{color: {Configuration.Palette1B} !important;}}

		.home-logos-viewport {{position: relative; width: 100%; overflow: hidden; background: {Configuration.WhiteColor}; mask-image: linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%); -webkit-mask-image: linear-gradient(to right, transparent 0%, black 5%, black 95%, transparent 100%);}}
		.home-logos-track {{display: flex; align-items: center; gap: {getattr(Configuration, 'HomeLogoGapPx', Configuration.Spacing2)}px; width: max-content; animation: home-logos-marquee {Configuration.HomeLogosAutoplaySec}s linear infinite; padding: {Configuration.Spacing1}px 0;}}
		.home-logo-card {{min-width: {Configuration.HomeLogoCardMinWidth}px; height: {Configuration.HomeLogoCardHeight}px; border-radius: {radiusCard - 6}px; background: {Configuration.WhiteColor}; border: none; display: flex; align-items: center; justify-content: center; padding: 6px 10px; box-shadow: none;}}
		.home-logo-card img {{max-height: 64px; width: auto; max-width: 100%; object-fit: contain; filter: saturate(102%);}}

		@keyframes home-logos-marquee {{
			0% {{transform: translateX(0);}}
			100% {{transform: translateX(-50%);}}}}

		@media (max-width: 900px) {{
			.home-content-card {{padding: 14px;}}
			.home-how-inner {{max-width: 96%; padding: {Configuration.Spacing1}px;}}
			.home-logo-card {{min-width: 136px; height: 78px;}}
			.home-logo-card img {{max-height: 52px;}}}}
	</style>"""

# Slideshow
def ReadImageAsBase64(imagePath):
	'Encodes an image as base64 for HTML embedding.'
	with open(imagePath, 'rb') as imageFile: return base64.b64encode(imageFile.read()).decode('utf-8')

def LoadLogoFiles(logosFolder=Configuration.LogosFolderPath, extensions=Configuration.HomeLogosExtensions):
	'Loads logos from the configured folder and returns sorted matching paths.'
	folderPath        = Path(logosFolder)
	allowedExtensions = {ext.lower() for ext in extensions}
	return [filePath for filePath in sorted(folderPath.iterdir()) if filePath.is_file() and filePath.suffix.lower() in allowedExtensions]

def RenderLogosSection():
	'Renders Home partner logos title/subtitle and content container.'
	UI.ObjectTitleCss(Configuration.Palette1A, classSuffix='home-logos')
	UI.ObjectSubtitleCss(Configuration.Palette1B, classSuffix='home-logos')
	st.markdown(f"<div class='object-title-wrap-home-logos'><div class='object-title-home-logos'>Organizations in the spotlight</div>", unsafe_allow_html=True)
	st.markdown(f"<p class='object-subtitle-home-logos'>Some of the organizations featured on Domani Dono: more to come!</p></div>", unsafe_allow_html=True)
	st.markdown('<br>', unsafe_allow_html=True)

	logoPaths     = LoadLogoFiles()
	logoCardsHtml = ''.join(f"<div class='home-logo-card'><img src='data:image/{path.suffix.lstrip('.').lower()};base64,{ReadImageAsBase64(path)}' alt='{path.stem}'></div>" for path in logoPaths)
	st.markdown(f"<div class='home-content-card'><div class='home-logos-viewport'><div class='home-logos-track'>{logoCardsHtml}{logoCardsHtml}</div></div></div>", unsafe_allow_html=True)

# How It Works
def RenderHowItWorksSection():
	'Renders Home How it works title/subtitle and content container.'
	UI.ObjectTitleCss(Configuration.Palette1A, classSuffix='home-how')
	UI.ObjectSubtitleCss(Configuration.Palette1B, classSuffix='home-how')
	st.markdown(f"<div class='object-title-wrap-home-how'><div class='object-title-home-how'>How does it work?</div>", unsafe_allow_html=True)
	st.markdown(f"<p class='object-subtitle-home-how'>Discover where organizations create impact and how to donate with intention.</p></div>", unsafe_allow_html=True)
	st.markdown('<br>', unsafe_allow_html=True)

	storyHtml = ''.join(f"<p class='home-how-story'>{paragraph}</p>" for paragraph in Configuration.HomeHowItWorksStoryParagraphs)
	guideHtml = ''.join(f'<li>{step}</li>' for step in Configuration.HomeHowItWorksGuideSteps)
	st.markdown("<div class='home-content-card'>" + "<div class='home-how-inner'>" + storyHtml
			+ f"<p style='margin: 12px 0; font-style: italic; text-decoration: underline; color: {Configuration.Palette1A};'>{Configuration.HomeHowItWorksGuideTitle}</p>"
			+ f"<ul class='home-how-list'>{guideHtml}</ul>"
			+ "<div class='home-bottom-spacer' aria-hidden='true'></div>" + "</div>" + "</div>", unsafe_allow_html=True)

# Data Source
def RenderDataSourceSection(logoPath=None):
	'Renders data source information with logo in same container as HowItWorks.'
	UI.ObjectTitleCss(Configuration.Palette1A, classSuffix='home-source')
	UI.ObjectSubtitleCss(Configuration.Palette1B, classSuffix='home-source')
	st.markdown("<div class='object-title-wrap-home-source'><div class='object-title-home-source'>Where does the information come from?</div>", unsafe_allow_html=True)
	st.markdown("<p class='object-subtitle-home-source'>Data sources.</p></div>", unsafe_allow_html=True)
	st.markdown('<br>', unsafe_allow_html=True)
	dataSourceText = Configuration.DataSourceText.strip().replace('\n', '<br>')
	updateLabel    = UI.FormatUpdateLabel()
	logoHtml       = f"<div class='home-data-source-logo'><img src='data:image/png;base64,{ReadImageAsBase64(logoPath)}' alt='OpenCooperazione'></div>"
	dataSourceHtml = f"""
		<div class='home-data-source'>
			{logoHtml}
			<p class='home-data-source-text'>Data from <strong>OpenCooperazione</strong></p>
			<div class='home-data-source-note' style='color: {Configuration.Palette1B} !important;'>{dataSourceText}<br><br><strong>{updateLabel}</strong></div>
			<div class='home-bottom-spacer' aria-hidden='true'></div>
		</div>"""
	st.markdown(f"<div class='home-content-card'><div class='home-how-inner'>{dataSourceHtml}</div></div>", unsafe_allow_html=True)

# Wrapper
def RenderHomeContent():
    'Renders Home sections using title/subtitle blocks.'
    st.markdown(HomePageCss(), unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1], gap='small')
    with col1: RenderHowItWorksSection()
    with col2: RenderDataSourceSection(logoPath='files/images/OpenCooperazione.png')
    
    st.markdown('<br>', unsafe_allow_html=True)
    RenderLogosSection()