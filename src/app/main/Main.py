# Environment Setting
from pathlib import Path
import streamlit as st
import sys
import time

SourceDirectory = Path(__file__).resolve().parents[2]
if str(SourceDirectory) not in sys.path: sys.path.insert(0, str(SourceDirectory))

import db.LoadOCExcel                       as DataLoader
import app.ui.Layout                        as HomeUI
import app.pages.Home                       as Home
import app.pages.Registry                   as Registry
import app.pages.Impacts                    as Impacts
import configuration.StreamlitConfiguration as Configuration
import app.main.Loader                      as Loader

# Page Title
def TitleCss(pageTitle):
    'Returns CSS styles for the fixed title on the registry page, adjusting position based on sidebar state.'    
    themeColor = HomeUI.GetPageTheme(pageTitle)['primary']
    return f"""<style>
        .title-fixed {{
            display: flex !important;
            align-items: center !important;
            position: fixed !important; 
            top: {getattr(Configuration, 'TitleTopPx')} !important; 
            left: {getattr(Configuration, 'TitleLeftCollapsedPx')} !important;
            margin: 0 !important; 
            padding: 0 !important;
            color: {themeColor} !important; 
            font-size: {getattr(Configuration, 'FontSize120')} !important;
            line-height: {Configuration.LineHeight2} !important;
            font-weight: {Configuration.FontWeight7} !important;
            letter-spacing: {getattr(Configuration, 'LetterSpacing2')} !important; 
            font-family: {Configuration.FontFamily} !important;
            text-shadow: none !important; 
            z-index: 9999 !important;}}
        body:has([data-testid="stSidebar"][aria-expanded="true"])  .title-fixed {{ left: {getattr(Configuration, 'TitleLeftExpandedPx')} !important; }}
        body:has([data-testid="stSidebar"][aria-expanded="false"]) .title-fixed {{ left: {getattr(Configuration, 'TitleLeftCollapsedPx')} !important; }}
    </style><div class="title-fixed"><span>{pageTitle}</span></div>"""

# Render Pages
def RenderHomePage():
    'Render the complete Home page layout and content.'
    st.markdown(TitleCss('Home'), unsafe_allow_html=True)
    Home.RenderHomeContent()

def RenderImpactsPage(registry, geography, metrics):
    'Render the complete Impacts page layout and content.'
    st.markdown(TitleCss('Impacts'), unsafe_allow_html=True)
    Impacts.RenderImpactsContent(registry, geography, metrics)

def RenderRegistryPage(registry, metrics):
    'Render the complete Registry page layout and content.'
    st.markdown(TitleCss('Registry'), unsafe_allow_html=True)
    Registry.RenderRegistryContent(registry, metrics)

# Main
def Main():
    'Run the Home page entrypoint workflow.'
    HomeUI.SetupPage()

    st.markdown(Loader.HideRunningIndicatorCss(), unsafe_allow_html=True)
    isFirstLoad = 'app_data' not in st.session_state
    if isFirstLoad:
        targetLoadSeconds = Loader.GetTargetLoadSeconds(10, 20)
        loaderSlot        = Loader.RenderLoader(targetDurationSeconds=targetLoadSeconds)
        loadStartTime     = time.perf_counter()
        try:
            result = DataLoader.BuildAllDfs()
        except Exception as loadError:
            loaderSlot.empty()
            st.error(f'Error in uploading data: {loadError}')
            st.stop()
        elapsedLoadSeconds = time.perf_counter() - loadStartTime
        remainingSeconds   = targetLoadSeconds - elapsedLoadSeconds
        if remainingSeconds > 0: time.sleep(remainingSeconds)
        loaderSlot.empty()
        st.session_state['app_data'] = result
        registry, metrics, geography = result
    else:
        registry, metrics, geography = st.session_state['app_data']
        st.session_state['app_data'] = (registry, metrics, geography)
        

    currentPage = HomeUI.RenderLayout()
    if currentPage == 'Impacts':
        RenderImpactsPage(registry, geography, metrics)
        return    
    if currentPage == 'Registry':
        RenderRegistryPage(registry, metrics)
        return
    else: 
        RenderHomePage()
        return

Main()