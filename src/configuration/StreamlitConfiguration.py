# Environment Setting
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / '.env')

import app.ui.AdaptiveUI as AdaptiveUI

# Streamlit Page
PageTitle           = 'Domani Dono'
PageIcon            = '😇'
Layout              = 'wide'
InitialSidebarState = 'collapsed'
AppVersion          = '1.0.0'

# Assets
LogoPath               = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'logo.png'
EmailIconPath          = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'Email.png'
CopyrightIconPath      = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'Copyright.png'
HomeIconPath           = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'Home.png'
ImpactsIconPath        = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'Impacts.png'
RegistryIconPath       = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'Registry.png'
LogosFolderPath        = Path(__file__).resolve().parents[2] / 'files' / 'images' / 'logos'

WorldGeoJsonUrl       = 'https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json'

# Pages & Icons
Pages           = ['Home', 'Impacts', 'Registry']
PageIconPaths   = {'Home': HomeIconPath, 'Impacts': ImpactsIconPath, 'Registry': RegistryIconPath}
FooterIconPaths = {'Email': EmailIconPath, 'Copyright': CopyrightIconPath}

# Loader
LoadingMessages = [
    'You may say I\'m a dreamer, but I\'m not the only on. 🌍✨ \n Imagine - John Lennon',
    'We are the ones who make a brighter day, so let\'s start giving! 🌟💖 \n We Are The World - Michael Jackson',
    'And how many years can some people exist before they\'re allowed to be free? 🌈🕊️ \n Blowin in the Wind - Bob Dylan',
    'Heal the world, make it a better place, for you and for me and the entire human race 🌎💚 \n Heal The World - Michael Jackson',
    'Did you ever stop to notice this crying Earth, these weeping shores? 🌊😭 \n Earth Song - Michael Jackson',
    'Won\'t you help to sing, another song of freedom? 🌟🎶 \n Redemption Song - Bob Marley',
    'People help the people, and if you\'re homesick give me your hand and I\'ll hold it 🌍🤝 \n People Help The People - Birdy',
    'If you wanna make the world a better place, take a look at yourself and then make a change 🌎 \n Man in the Mirror - Michael Jackson'
]

# Home
HomeHowItWorksStoryParagraphs = [
        '<br>Imagine opening a list of possibilities where every choice can become a concrete act of care. That is where Domani Dono stems from: the desire to transform your <strong>generosity into measurable impact</strong>. 🫶🏻',
        'Behind every organization there is a story: people, communities, and futures being rebuilt. On our platform, every story is connected to real data you can trust: navigating through the pages you can discover the organizations, how they create impact and understand where your contribution can make a difference. 🎁',
        'Our promise is simple: help you donate with both heart and clarity, so each euro feels <strong>intentional, informed, and deeply meaningful</strong>. 💞<br>']
HomeHowItWorksGuideTitle = 'Your journey in 4 steps'
HomeHowItWorksGuideSteps = [
        '<strong>Start in Home:</strong> get oriented and discover the organizations in the ecosystem.',
        '<strong>Dive into Impacts:</strong> compare organizations through maps, trends, and get an AI-powered donation insights.',
        '<strong>Validate in Registry:</strong> review structured records and key information before deciding.',
        '<strong>Make the difference:</strong> take action and contribute to the causes that matter most to you. <br>']
HomeLogosExtensions    = ['.png', '.jpg', '.jpeg', '.webp']
HomeLogosAutoplaySec   = 150
HomeLogoGapPx          = 30
HomeLogoCardMinWidth   = 150
HomeLogoCardHeight     = 90
DataSourceText         = """Data is retrieved from open-cooperazione.it, and harmonized in Domani Dono to support clearer and more informed giving decisions.
                                \n\n We plan to expand data sources in the future, while maintaining a strong focus on data quality and reliability."""

# Parameter
Parameters = ['Category', 'Organization']

# Donor Types
DonorTypes = ['5x1000', 'Aziende', 'Chiese', 'Fondazioni', 'Istituzioni', 'Privati']

# LLM
ORApiKey             = os.getenv('OPENROUTER_API_KEY')
ModelB               = 'liquid/lfm-2.5-1.2b-thinking:free'
ModelC               = 'nvidia/nemotron-3-nano-30b-a3b:free' 
ModelH               = 'z-ai/glm-4.5-air:free'
ModelI               = 'stepfun/step-3.5-flash:free'
ModelJ               = 'nvidia/nemotron-3-super-120b-a12b:free'
ModelK               = 'arcee-ai/trinity-mini:free'
WinnerModel          = ModelB
LlmFallbackModels    = [ModelH, ModelC, ModelJ]
LlmMaxRetries        = 3
LlmRetryDelaySeconds = 1.5
Temperature          = 0.25
TopP                 = 0.75
MaxTokens            = 5000

LLMDimensionsGlossary = """
**Dimensions Glossary**

* <strong>Impact</strong> | Projected social impact based on People/Projects positioning (High Impact > Efficient Reach > Scale to Unlock > Under Development).
* <strong>Maturity</strong> | Organizational solidity, combining age, associates base, and workforce structure.
* <strong>Efficiency</strong> | Ability to allocate resources toward projects (higher share of project spending vs revenues).
* <strong>Globalization</strong> | Geographic breadth, based on the number of countries where projects are active.
* <strong>Dimension</strong> | Operational scale and consistency of the workforce (volume and trend over time vs category).
* <strong>Trust</strong> | Donor confidence, combining donation and donor dynamics (level and trend vs previous year/category).
* <strong>Growth</strong> | Momentum over time, combining trends in revenues, expenses, projects, and beneficiaries.
"""

LLMPrompt = """
ROLE: You are a philanthropic analyst. You must provide a donation recommendation using only the provided ranking data.

INPUT RANKING TABLE (already in markdown): {summaryMarkdownTable}

ANALYSIS STRUCTURE:
1. Highlight strengths and weaknesses of the top recommendation, compared to the alternatives.
2. Highlight risk and opportunities of the top recommendation, compared to the alternatives.
3. Point out the best and worst dimension of the top recommendation, compared to the alternatives.

OBJECTIVE:
1. Start immediately with a markdown heading.
2. Show the exact INPUT RANKING TABLE once, right after the first heading.
3. Then provide your recommendation and analysis using the required ANALYSIS STRUCTURE, comparing the first and second recommendations.

STRICT RULES:
1. Use only data present in the INPUT RANKING TABLE.
2. Do not invent numbers, rows, columns, or organizations.
3. Do not rewrite, reformat, or regenerate the table.
4. Follow the required ANALYSIS STRUCTURE precisely and in order. Build a speech with it, not a list of bullet points.
5. Output must be valid markdown and render correctly in Streamlit."""

# Liquid Layout
BaseRadiusInput  = 15
BaseRadiusCard   = 25

# Colors
WhiteColor = '#FFFFFF'

Palette1A  = '#2f4858'
Palette1B  = '#485a73'
Palette1C  = '#676a8b'
Palette1D  = '#8c7a9f'
Palette1E  = '#b38aae'
Palette1F  = '#da9bb7'

Palette2A  = Palette1A
Palette2B  = '#1c6e7d'
Palette2C  = '#039590'
Palette2D  = '#4bbc8e'
Palette2E  = '#9bde7e'
Palette2F  = '#f9f871'

Palette3A  = Palette1A
Palette3B  = '#9baebc'
Palette3C  = '#677987'
Palette3D  = '#876e7d'
Palette3E  = '#553e4c'

# Fonts & Typography
FontFamily  = "'Inter', sans-serif"

FontWeight1 = '100'
FontWeight2 = '200'
FontWeight3 = '300'
FontWeight4 = '400'
FontWeight5 = '500'
FontWeight6 = '600'
FontWeight7 = '700'
FontWeight8 = '800'
FontWeight9 = '900'

BaseFontSize75  = 0.75
BaseFontSize80  = 0.8
BaseFontSize85  = 0.85
BaseFontSize90  = 0.9
BaseFontSize95  = 0.95
BaseFontSize100 = 1.0
BaseFontSize105 = 1.05
BaseFontSize110 = 1.1
BaseFontSize115 = 1.15
BaseFontSize120 = 1.2
BaseFontSize125 = 1.25

# Line Height
LineHeight1         = '1.1'
LineHeight2         = '1.2'
LineHeight3         = '1.3'
LineHeight4         = '1.4'
LineHeight5         = '1.5'

# Letter Spacing
BaseLetterSpacing1  = 0.1
BaseLetterSpacing2  = 0.2
BaseLetterSpacing3  = 0.3

# Opacity
Opacity50 = '0.5'
Opacity75 = '0.75'
Opacity85 = '0.85'
Opacity95 = '0.95'

# Spacing
BaseSpacing1   = 10
BaseSpacing2   = 20
BaseSpacing3   = 30
BaseSpacing4   = 40
BaseSpacing5   = 50
BaseSpacing6   = 60

# Border
BaseBorder1 = 10
BaseBorder2 = 20
BaseBorder3 = 30
BaseBorder4 = 40
BaseBorder5 = 50

# Title
BaseTitleTopPx           = 100
BaseTitleLeftExpandedPx  = 275
BaseTitleLeftCollapsedPx = 100
TopbarHeightPx           = 35

# Responsive System
ResponsiveBaseWidth      = 1440
ResponsiveMinScale       = 0.78
ResponsiveMaxScale       = 1.03
ResponsiveStepPx         = 40
ResponsiveFallbackVw     = 1360
ResponsiveViewportWidth  = ResponsiveFallbackVw
ResponsiveViewportHeight = 900
ResponsiveScale          = 1.0

ResponsiveValues = AdaptiveUI.ApplyResponsiveScale(queryParams={},
                                baseValues={
                                    'BaseRadiusInput'           : BaseRadiusInput,
                                    'BaseRadiusCard'            : BaseRadiusCard,
                                    'BaseFontSize75'            : BaseFontSize75,
                                    'BaseFontSize80'            : BaseFontSize80,
                                    'BaseFontSize85'            : BaseFontSize85,
                                    'BaseFontSize90'            : BaseFontSize90,
                                    'BaseFontSize95'            : BaseFontSize95,
                                    'BaseFontSize100'           : BaseFontSize100,
                                    'BaseFontSize105'           : BaseFontSize105,
                                    'BaseFontSize110'           : BaseFontSize110,
                                    'BaseFontSize115'           : BaseFontSize115,
                                    'BaseFontSize120'           : BaseFontSize120,
                                    'BaseFontSize125'           : BaseFontSize125,
                                    'BaseLetterSpacing1'        : BaseLetterSpacing1,
                                    'BaseLetterSpacing2'        : BaseLetterSpacing2,
                                    'BaseLetterSpacing3'        : BaseLetterSpacing3,
                                    'BaseSpacing1'              : BaseSpacing1,
                                    'BaseSpacing2'              : BaseSpacing2,
                                    'BaseSpacing3'              : BaseSpacing3,
                                    'BaseSpacing4'              : BaseSpacing4,
                                    'BaseSpacing5'              : BaseSpacing5,
                                    'BaseSpacing6'              : BaseSpacing6,
                                    'BaseBorder1'               : BaseBorder1,
                                    'BaseBorder2'               : BaseBorder2,
                                    'BaseBorder3'               : BaseBorder3,
                                    'BaseBorder4'               : BaseBorder4,
                                    'BaseBorder5'               : BaseBorder5,
                                    'BaseTitleTopPx'            : BaseTitleTopPx,
                                    'BaseTitleLeftExpandedPx'   : BaseTitleLeftExpandedPx,
                                    'BaseTitleLeftCollapsedPx'  : BaseTitleLeftCollapsedPx,
                                },
                                responsiveValues={'BaseWidth': ResponsiveBaseWidth, 'MinScale': ResponsiveMinScale, 'MaxScale': ResponsiveMaxScale, 'StepPx': ResponsiveStepPx, 'FallbackVw': ResponsiveFallbackVw, 'ViewportHeight': ResponsiveViewportHeight},
                                minimumValues={'LetterSpacing': 0, 'RadiusInput': 8, 'RadiusCard': 12},
                                target=globals())

FontSize75           = ResponsiveValues['FontSize75']
FontSize80           = ResponsiveValues['FontSize80']
FontSize85           = ResponsiveValues['FontSize85']
FontSize90           = ResponsiveValues['FontSize90']
FontSize95           = ResponsiveValues['FontSize95']
FontSize100          = ResponsiveValues['FontSize100']
FontSize105          = ResponsiveValues['FontSize105']
FontSize110          = ResponsiveValues['FontSize110']
FontSize115          = ResponsiveValues['FontSize115']
FontSize120          = ResponsiveValues['FontSize120']
FontSize125          = ResponsiveValues['FontSize125']

LetterSpacing1       = ResponsiveValues['LetterSpacing1']
LetterSpacing2       = ResponsiveValues['LetterSpacing2']
LetterSpacing3       = ResponsiveValues['LetterSpacing3']

Spacing1             = ResponsiveValues['Spacing1']
Spacing2             = ResponsiveValues['Spacing2']
Spacing3             = ResponsiveValues['Spacing3']
Spacing4             = ResponsiveValues['Spacing4']
Spacing5             = ResponsiveValues['Spacing5']
Spacing6             = ResponsiveValues['Spacing6']

Border1              = ResponsiveValues['Border1']
Border2              = ResponsiveValues['Border2']
Border3              = ResponsiveValues['Border3']
Border4              = ResponsiveValues['Border4']
Border5              = ResponsiveValues['Border5']

RadiusInput          = ResponsiveValues['RadiusInput']
RadiusCard           = ResponsiveValues['RadiusCard']

TitleTopPx           = ResponsiveValues['TitleTopPx']
TitleLeftExpandedPx  = ResponsiveValues['TitleLeftExpandedPx']
TitleLeftCollapsedPx = ResponsiveValues['TitleLeftCollapsedPx']