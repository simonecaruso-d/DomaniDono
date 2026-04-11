# Environment Setting
import base64
import streamlit as st
from urllib.parse import urlencode

import app.ui.AdaptiveUI                    as AdaptiveUI
import configuration.StreamlitConfiguration as Configuration

# Components
def HexToRgb(hexColor):
    color = (hexColor or '').strip().lstrip('#')
    if len(color) != 6: return (154, 43, 46)
    try: return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))
    except ValueError: return (154, 43, 46)

def DarkenRgb(rgbColor, factor=0.2):
    return tuple(max(0, min(255, int(channel * (1 - factor)))) for channel in rgbColor)

def RgbToCss(rgbColor):
    return ', '.join(str(max(0, min(255, int(channel)))) for channel in rgbColor)

def ScalePx(value, minimum=1):
    return AdaptiveUI.ScalePx(value, Configuration.ResponsiveScale, minimum=minimum)

def SetupPage():
    'Configure the base page metadata and layout.'
    st.set_page_config(page_title            = Configuration.PageTitle,
                       page_icon             = Configuration.PageIcon,
                       layout                = Configuration.Layout,
                       initial_sidebar_state = Configuration.InitialSidebarState)

def LoadLogo():
    'Load and encode the app logo as a base64 string.'
    with open(Configuration.LogoPath, 'rb') as file: return base64.b64encode(file.read()).decode()

def LoadSidebarIcons():
    'Load and encode sidebar page icons as base64 strings.'
    iconsB64 = {}
    for page, iconPath in Configuration.PageIconPaths.items(): 
        with open(iconPath, 'rb') as file: iconsB64[page] = base64.b64encode(file.read()).decode()
    return iconsB64

def LoadFooterIcons():
    'Load and encode sidebar footer icons as base64 strings.'
    iconsB64 = {}
    for key, iconPath in Configuration.FooterIconPaths.items():
        with open(iconPath, 'rb') as file: iconsB64[key] = base64.b64encode(file.read()).decode()
    return iconsB64

def GetCurrentPage(pages):
    'Resolve the active page from query parameters with a safe fallback.'
    currentPage                = st.query_params.get('page', pages[0])
    if currentPage not in pages: return pages[0]
    return currentPage

def GetPageTheme(pageName):
    'Resolve page-level theme colors using the existing configuration palette names.'
    if pageName == 'Impacts': return {'primary': Configuration.Palette2B, 'border': Configuration.Palette2D, 'background': Configuration.WhiteColor}
    if pageName == 'Registry': return {'primary': Configuration.Palette3E, 'border': Configuration.Palette3B, 'background': Configuration.WhiteColor}
    return {'primary': Configuration.Palette1A, 'border': Configuration.Palette1D, 'background': Configuration.WhiteColor}

def RenderSidebar(sidebarIcons, footerIcons):
    'Render the sidebar navigation and footer.'
    currentPage     = GetCurrentPage(Configuration.Pages)
    navigationItems = []

    currentVw = st.query_params.get('vw')
    currentVh = st.query_params.get('vh')

    for page in Configuration.Pages:
        activeClass = 'active' if page == currentPage else ''
        icon        = sidebarIcons.get(page, '')
        queryParams = {'page': page, 'loaded': '1'}
        if currentVw: queryParams['vw'] = currentVw
        if currentVh: queryParams['vh'] = currentVh
        queryString = urlencode(queryParams)
        navigationItems.append(f"""<a class="sidebar-nav-item {activeClass}" href="?{queryString}" target="_self">
                               <span class="sidebar-nav-item-content"><img class="sidebar-icon" src="data:image/png;base64,{icon}" alt="" /><span>{page}</span></span></a>""")

    emailIcon       = footerIcons.get('Email', '')
    copyrightIcon   = footerIcons.get('Copyright', '')

    footerHtml      = (
        """<div class="sidebar-footer"><a class="sidebar-footer-link" href="mailto:simocaruso1997@libero.it">"""
        f'<img class="sidebar-footer-icon" src="data:image/png;base64,{emailIcon}" alt="" />'
        """<span class="sidebar-footer-text">Contattami</span></a><div class="sidebar-footer-item">"""
        f'<img class="sidebar-footer-icon" src="data:image/png;base64,{copyrightIcon}" alt="" />'
        """<span class="sidebar-footer-text">Simone Caruso 2026, v 1.0</span></div></div>""")

    st.sidebar.markdown('<div class="sidebar-shell">' + '<div class="sidebar-nav">' + ''.join(navigationItems) + '</div>' + footerHtml + '</div>', unsafe_allow_html=True)
    return currentPage

def FormatUpdateLabel():
    return 'Last update: 02 Apr 2026, 10:30 (UTC)'

# Wrappers
def RenderStyles(logo = LoadLogo(),
                buttonRadiusPx  = ScalePx(1000),
                inputRadiusPx   = getattr(Configuration, 'RadiusInput', ScalePx(15)),
                cardRadiusPx    = getattr(Configuration, 'RadiusCard', ScalePx(25)),
                borderWidthPx   = ScalePx(1),
                borderColor     = Configuration.Palette1D,
                backgroundColor = Configuration.WhiteColor,
                primaryColor    = Configuration.Palette1A):
    'Inject global UI styles and render the custom topbar shell.'
    if logo is None: logo = LoadLogo()

    fontSizeSmall   = getattr(Configuration, 'FontSize2', AdaptiveUI.ScaleCssRem(0.85, Configuration.ResponsiveScale))
    fontSizeBody    = getattr(Configuration, 'FontSize3', AdaptiveUI.ScaleCssRem(0.95, Configuration.ResponsiveScale))
    fontSizeEmph    = getattr(Configuration, 'FontSize4', AdaptiveUI.ScaleCssRem(1.05, Configuration.ResponsiveScale))
    letterSpacing1  = getattr(Configuration, 'LetterSpacing1', AdaptiveUI.ScaleCssPx(0.1, Configuration.ResponsiveScale, minimum=0))
    letterSpacing2  = getattr(Configuration, 'LetterSpacing2', AdaptiveUI.ScaleCssPx(0.2, Configuration.ResponsiveScale, minimum=0))

    topbarHeightPx        = ScalePx(44)
    topbarLeftExpandedPx  = ScalePx(250)
    topbarLeftCollapsedPx = ScalePx(75)
    topbarLogoHeightPx    = ScalePx(30)
    topbarPaddingX        = ScalePx(25)
    topbarGap             = ScalePx(15)
    sidebarCollapsedWidth = ScalePx(75)
    primaryRgb            = HexToRgb(primaryColor)
    primaryDarkRgb        = DarkenRgb(primaryRgb, factor=0.22)
    primaryDarkHex        = '#' + ''.join(f'{channel:02X}' for channel in primaryDarkRgb)
    primaryRgbCss         = RgbToCss(primaryRgb)
    primaryDarkRgbCss     = RgbToCss(primaryDarkRgb)

    st.markdown(f"""<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet"><style>
            :root {{
                --dp-primary: {primaryColor};
                --dp-primary-rgb: {primaryRgbCss};
                --dp-primary-dark: {primaryDarkHex};
                --dp-primary-dark-rgb: {primaryDarkRgbCss};
                --dp-bar-bg: linear-gradient(120deg, var(--dp-primary) 0%, var(--dp-primary-dark) 100%);
                --dp-bar-overlay: linear-gradient(120deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.00) 44%);
                --dp-text-soft: rgba(255,255,255,0.84);
                --dp-glass: rgba(255,255,255,0.10);
                --dp-glass-strong: rgba(255,255,255,0.16);
                --dp-shadow-soft: 0 10px 34px rgba(var(--dp-primary-rgb), 0.18);
                --dp-shadow-glow: 0 0 24px rgba(var(--dp-primary-rgb), 0.14);
                --dp-shadow-strong: 0 20px 48px rgba(var(--dp-primary-dark-rgb), 0.28);
                --dp-glow-primary: 0 0 38px rgba(var(--dp-primary-rgb), 0.34);
                --dp-bar-blur: blur(14px) saturate(165%);
                --dp-bar-shadow: 0 10px 40px rgba(var(--dp-primary-rgb), 0.34), 0 0 30px rgba(var(--dp-primary-rgb), 0.26), inset 0 1px 0 rgba(255,255,255,0.08)}}

            html, body,
            [data-testid="stAppViewContainer"],
            [data-testid="stMain"],
            p, h1, h2, h3, h4, h5, h6,
            label, input, textarea, select,
            [data-testid="stSidebar"] p,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] div {{font-family: 'Inter', sans-serif !important;}}

            .stApp {{background-color: {backgroundColor};
                background-image:
                    radial-gradient(circle at 15% 18%, rgba(var(--dp-primary-rgb), 0.10) 0%, rgba(var(--dp-primary-rgb), 0.00) 38%),
                    radial-gradient(circle at 84% 10%, rgba(var(--dp-primary-dark-rgb), 0.12) 0%, rgba(var(--dp-primary-dark-rgb), 0.00) 42%),
                    linear-gradient(180deg, rgba(255,255,255,0.96) 0%, rgba(250,247,244,0.98) 100%);}}

            [data-testid="stHeader"],
            [data-testid="stAppHeader"],
            [data-testid="stToolbar"] {{background: transparent !important; box-shadow: none !important; backdrop-filter: none !important; border-bottom: none !important; z-index: 2147483002 !important;}}

            [data-testid="stSidebar"] {{background: var(--dp-bar-bg); box-shadow: var(--dp-bar-shadow); backdrop-filter: var(--dp-bar-blur); position: relative; overflow: visible; z-index: 2147483003 !important;}}

            [data-testid="stSidebar"] > div,
            [data-testid="stSidebar"] [data-testid="stSidebarContent"] {{background: transparent !important;}}
            [data-testid="stSidebarHeader"] {{position: relative !important; overflow: visible !important; z-index: 2147483004 !important;}}

            [data-testid="stHeader"]::before,
            [data-testid="stAppHeader"]::before,
            [data-testid="stToolbar"]::before {{content: none !important;}}

            [data-testid="stSidebar"]::before {{content: ""; position: absolute; inset: 0; pointer-events: none; background: var(--dp-bar-overlay); opacity: 0.24;}}

            [data-testid="stHeader"]::after,
            [data-testid="stAppHeader"]::after,
            [data-testid="stToolbar"]::after {{content: none !important;}}

            [data-testid="stSidebar"]::after {{content: ""; position: absolute; inset: 0; pointer-events: none; background: radial-gradient(circle at 18% 12%, rgba(255,255,255,0.07) 0%, rgba(255,255,255,0.00) 58%);}}

            .custom-topbar {{position: fixed; top: 0; left: 0; right: 0; height: {topbarHeightPx}px; background: var(--dp-bar-bg); border-bottom: 1px solid rgba(255,255,255,0.04); display: flex !important; align-items: center; padding: 0 {topbarPaddingX}px; gap: {topbarGap}px; z-index: 2147483000; pointer-events: none; transition: padding-left 0.35s cubic-bezier(0.22, 1, 0.36, 1); backdrop-filter: blur(3px) saturate(108%); box-shadow: 0 4px 12px rgba(var(--dp-primary-dark-rgb), 0.16); overflow: hidden; visibility: visible !important; box-sizing: border-box;}}
            .custom-topbar::before {{content: ""; position: absolute; inset: 0; pointer-events: none; background: var(--dp-bar-overlay); opacity: 0.12;}}
            .custom-topbar::after {{content: none;}}
            body:has([data-testid="stSidebar"][aria-expanded="true"]) .custom-topbar {{padding-left: {topbarLeftExpandedPx}px;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) .custom-topbar {{padding-left: {topbarLeftCollapsedPx}px;}}
            .custom-topbar img {{position: relative; z-index: 1; margin-left: {ScalePx(8)}px; height: {topbarLogoHeightPx}px; width: auto; filter: drop-shadow(0 0 3px rgba(255,255,255,0.20));}}
            .custom-topbar .topbar-title {{position: relative; z-index: 1; margin-left: {ScalePx(4)}px; color: {Configuration.WhiteColor}; font-size: clamp(1.35rem, 1.15rem + 0.45vw, 1.7rem); font-weight: 700; letter-spacing: {letterSpacing2}; text-shadow: 0 0 6px rgba(255,255,255,0.16), 0 0 10px rgba(var(--dp-primary-rgb), 0.12); flex: 0 0 auto; white-space: nowrap;}}
            [data-testid="stExpandSidebarButton"],
            [data-testid="stSidebarCollapseButton"] {{position: fixed !important; top: {ScalePx(5)}px !important; left: {ScalePx(12)}px !important; z-index: 2147483005 !important; visibility: visible !important; opacity: 1 !important; margin: 0 !important; transform: none !important;}}
            [data-testid="stExpandSidebarButton"],
            [data-testid="stSidebarCollapseButton"] button {{width: {ScalePx(34)}px !important; height: {ScalePx(34)}px !important; padding: 0 !important; color: #FFFFFF !important; background: rgba(255,255,255,0.22) !important; border: 1px solid rgba(255,255,255,0.40) !important; border-radius: {ScalePx(14)}px !important; box-shadow: 0 0 18px rgba(255,255,255,0.14), 0 10px 24px rgba(var(--dp-primary-dark-rgb), 0.22) !important; backdrop-filter: blur(10px) saturate(135%); transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease; display: inline-flex !important; align-items: center !important; justify-content: center !important;}}
            [data-testid="stExpandSidebarButton"]:hover,
            [data-testid="stSidebarCollapseButton"] button:hover {{background: rgba(255,255,255,0.32) !important; border-color: rgba(255,255,255,0.54) !important; box-shadow: 0 0 22px rgba(255,255,255,0.22), 0 12px 28px rgba(var(--dp-primary-dark-rgb), 0.26) !important; transform: translateY(-1px);}}
            [data-testid="stExpandSidebarButton"] svg,
            [data-testid="stSidebarCollapseButton"] button svg {{fill: currentColor !important; color: #FFFFFF !important; stroke: currentColor !important;}}

            [data-testid="stSidebar"] {{border-right: 1px solid rgba(255,255,255,0.12);}}
            [data-testid="stSidebar"] * {{color: #FFFFFF !important; font-size: {fontSizeBody} !important;}}

            [data-testid="stSidebar"] .sidebar-nav {{display: flex; flex-direction: column; gap: {ScalePx(5)}px; padding-top: {ScalePx(5)}px;}}
            [data-testid="stSidebar"] .sidebar-shell {{min-height: calc(100vh - 86px); display: flex; flex-direction: column;}}
            [data-testid="stSidebar"] .sidebar-nav-item {{display: block; text-decoration: none; color: #FFFFFF !important; border-radius: {buttonRadiusPx}px; padding: {ScalePx(10)}px {ScalePx(15)}px; font-size: {fontSizeBody}; font-weight: 500; letter-spacing: {letterSpacing1}; background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.05); transition: background 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease, border-color 0.25s ease;}}
            [data-testid="stSidebar"] .sidebar-nav-item:hover {{background: var(--dp-glass); border-color: rgba(255,255,255,0.14); box-shadow: var(--dp-shadow-glow), var(--dp-glow-primary); transform: translateX(2px);}}
            [data-testid="stSidebar"] .sidebar-nav-item.active {{background: var(--dp-glass-strong); border-color: rgba(255,255,255,0.26); box-shadow: 0 0 22px rgba(255,255,255,0.22), 0 8px 24px rgba(var(--dp-primary-dark-rgb), 0.24), var(--dp-glow-primary); font-size: {fontSizeEmph}; font-weight: 700;}}
            [data-testid="stSidebar"] .sidebar-nav-item-content {{display: flex; align-items: center; gap: {ScalePx(10)}px;}}
            [data-testid="stSidebar"] .sidebar-icon {{width: {ScalePx(15)}px; height: {ScalePx(15)}px; object-fit: contain; opacity: 0.96; transition: opacity 0.25s ease, transform 0.25s ease, filter 0.25s ease;}}
            [data-testid="stSidebar"] .sidebar-nav-item.active .sidebar-icon {{opacity: 1; transform: scale(1.08); filter: drop-shadow(0 0 6px rgba(255,255,255,0.28));}}

            [data-testid="stSidebar"][aria-expanded="false"] {{min-width: {sidebarCollapsedWidth}px !important; max-width: {sidebarCollapsedWidth}px !important; width: {sidebarCollapsedWidth}px !important; transform: translateX(0) !important;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-nav-item {{padding: {ScalePx(10)}px 0; display: flex; justify-content: center; border-radius: {ScalePx(15)}px;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-nav-item-content {{justify-content: center;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-nav-item-content span {{display: none;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-icon {{width: {ScalePx(20)}px; height: {ScalePx(20)}px;}}

            [data-testid="stSidebar"] .sidebar-footer {{margin-top: auto; padding: {ScalePx(10)}px {ScalePx(10)}px {ScalePx(5)}px; border-top: 1px solid rgba(255,255,255,0.24); display: flex; flex-direction: column; gap: {ScalePx(10)}px;}}
            [data-testid="stSidebar"] .sidebar-footer-item,
            [data-testid="stSidebar"] .sidebar-footer-link {{display: flex; align-items: center; gap: {ScalePx(10)}px; text-decoration: none; color: #FFFFFF !important; border-radius: {buttonRadiusPx}px; padding: {ScalePx(10)}px {ScalePx(10)}px; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.08); opacity: 0.96; transition: background 0.25s ease, opacity 0.25s ease, box-shadow 0.25s ease, transform 0.25s ease;}}
            [data-testid="stSidebar"] .sidebar-footer-link:hover {{background: rgba(255,255,255,0.16); box-shadow: 0 0 16px rgba(255,255,255,0.16), var(--dp-glow-primary); transform: translateX(1px); opacity: 1;}}
            [data-testid="stSidebar"] .sidebar-footer-icon {{width: {ScalePx(15)}px; height: {ScalePx(15)}px; object-fit: contain; opacity: 0.95;}}
            [data-testid="stSidebar"] .sidebar-footer-text {{font-size: {fontSizeSmall} !important; font-weight: 500; line-height: 1.2;}}

            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-footer {{align-items: center; padding-left: 0; padding-right: 0;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-footer-item,
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-footer-link {{justify-content: center; padding: {ScalePx(10)}px 0; width: {ScalePx(45)}px; border-radius: {ScalePx(15)}px;}}
            body:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stSidebar"] .sidebar-footer-text {{display: none;}}

            .stButton > button {{border-radius: {buttonRadiusPx}px; background: linear-gradient(95deg, var(--dp-primary) 0%, var(--dp-primary-dark) 100%); color: #FFFFFF; border: none; padding: {ScalePx(10)}px {ScalePx(25)}px; font-weight: 500; letter-spacing: {letterSpacing2}; transition: box-shadow 0.25s ease, transform 0.2s ease; box-shadow: var(--dp-shadow-soft), inset 0 1px 0 rgba(255,255,255,0.22);}}
            .stButton > button:hover {{box-shadow: 0 0 26px rgba(var(--dp-primary-rgb), 0.54), var(--dp-shadow-strong); transform: translateY(-2px);}}

            .stTextInput input, .stSelectbox > div, .stNumberInput input {{border-radius: {inputRadiusPx}px !important; border: 1px solid rgba(var(--dp-primary-rgb), 0.28) !important; background: rgba(255,255,255,0.72) !important; backdrop-filter: blur(8px); transition: box-shadow 0.25s ease, border-color 0.25s ease;}}
            .stTextInput input:focus, .stSelectbox > div:focus-within {{box-shadow: 0 0 0 3px rgba(var(--dp-primary-rgb), 0.20), 0 8px 20px rgba(var(--dp-primary-rgb), 0.12) !important; border-color: var(--dp-primary) !important;}}

            [data-testid="stDeckGlJsonChart"] {{ border-radius: {cardRadiusPx}px !important; overflow: hidden !important; box-shadow: 0 10px 34px rgba(var(--dp-primary-rgb), 0.18), 0 2px 8px rgba(var(--dp-primary-rgb), 0.10) !important; border: {borderWidthPx}px solid {borderColor} !important;}}

        </style>
        <script>
            (function() {{
                function syncTopbar() {{
                    var sidebar = document.querySelector('[data-testid="stSidebar"]');
                    var topbar  = document.querySelector('.custom-topbar');
                    if (!sidebar || !topbar) return;
                    var rawSidebarWidth = sidebar.offsetWidth || {ScalePx(60)};
                    var maxSafeLeft = Math.max({ScalePx(60)}, Math.floor((window.innerWidth || 0) * 0.45));
                    var sidebarWidth = Math.max({ScalePx(60)}, Math.min(rawSidebarWidth, maxSafeLeft));
                    topbar.style.left = '0px';
                    topbar.style.paddingLeft = sidebarWidth + 'px';}}
                function bootstrapViewport() {{
                    var params = new URLSearchParams(window.location.search);
                    var hasVw  = !!(params.get('vw') || '').trim();
                    var hasVh  = !!(params.get('vh') || '').trim();
                    if (hasVw && hasVh) return;

                    var widthBucket  = Math.round((window.innerWidth || 0) / 40) * 40;
                    var heightBucket = Math.round((window.innerHeight || 0) / 40) * 40;
                    if (!widthBucket || !heightBucket) return;

                    params.set('vw', String(widthBucket));
                    params.set('vh', String(heightBucket));
                    var query = params.toString();
                    var nextUrl = window.location.pathname + (query ? '?' + query : '') + window.location.hash;
                    window.location.replace(nextUrl);}}
                function init() {{
                    syncTopbar();
                    bootstrapViewport();
                    var sidebar = document.querySelector('[data-testid="stSidebar"]');
                    if (!sidebar) return;
                    new MutationObserver(syncTopbar).observe(sidebar, {{ attributes: true, attributeFilter: ['aria-expanded'] }});
                    window.addEventListener('resize', syncTopbar);}}
                if (document.readyState === 'loading') {{document.addEventListener('DOMContentLoaded', init);}} else {{
                    var attempts = 0;
                    var poll = setInterval(function() {{
                        if (document.querySelector('[data-testid="stSidebar"]') || ++attempts > 20) {{
                            clearInterval(poll);
                            init();}}}}, 100);}}}})();</script>""", unsafe_allow_html=True)

    st.markdown(f"""<div class="custom-topbar"><img src="data:image/png;base64,{logo}" /><span class="topbar-title">Domani Dono</span></div>""", unsafe_allow_html=True)

def RenderLayout():
    'Render styles and sidebar, then return the selected page key.'
    currentPage = GetCurrentPage(Configuration.Pages)
    theme = GetPageTheme(currentPage)
    RenderStyles(primaryColor=theme['primary'], borderColor=theme['border'], backgroundColor=theme['background'])
    return RenderSidebar(LoadSidebarIcons(), LoadFooterIcons())

# Standardized Elements
def ObjectTitleCss(color, classSuffix=None):
    wrapSelector  = '.object-title-wrap'
    titleSelector = '.object-title'
    if classSuffix:
        wrapSelector  = f'.object-title-wrap-{classSuffix}'
        titleSelector = f'.object-title-{classSuffix}'

        st.markdown(f"""<style>
        {wrapSelector} {{margin: 0 0 {Configuration.Spacing1}px 0; padding: 0;}}
        {titleSelector} {{
                    margin: 0;
                    color: {color} !important;
                    font-family: {Configuration.FontFamily} !important;
                    font-size: {Configuration.FontSize100} !important;
                    font-weight: {Configuration.FontWeight7} !important;
                    letter-spacing: {Configuration.LetterSpacing3} !important;
                    line-height: {Configuration.LineHeight5} !important;}}
            </style>""", unsafe_allow_html=True)

def ObjectSubtitleCss(color, classSuffix=None):
    subtitleSelector = '.object-subtitle'
    if classSuffix:
        subtitleSelector = f'.object-subtitle-{classSuffix}'

        st.markdown(f"""<style>
        {subtitleSelector} {{
                    margin: 2px 0 0 0;
                    color: {color} !important;
                    font-family: {Configuration.FontFamily} !important;
                    font-size: {Configuration.FontSize80} !important;
                    font-weight: {Configuration.FontWeight4} !important;
                    letter-spacing: {Configuration.LetterSpacing2} !important;
                    line-height: {Configuration.LineHeight4} !important;}}
            </style>""", unsafe_allow_html=True)