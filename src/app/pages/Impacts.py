# Environment Setting
from pathlib import Path
import streamlit as st
import sys

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import app.pages.ImpactsLLM                 as LLM
import app.pages.ImpactsVisuals             as Visuals
import app.pages.StreamlitData              as Data

# Fragments
@st.fragment
def RenderMap(df, height):
    'Isolated fragment.'
    Visuals.RenderMap(df, height)

@st.fragment
def RenderLlm(llmSummary):
    'Isolated fragment.'
    LLM.RenderDonationInsights(llmSummary)

@st.fragment
def RenderSankey(df, registryDf, parameter, height):
    'Isolated fragment.'
    Visuals.RenderSankey(df, registryDf, parameter, height)

@st.fragment
def RenderPeopleProjects(df, parameter, height):
    'Isolated fragment.'
    Visuals.RenderPeopleProjects(df, parameter, height)

# Wrapper
def RenderImpactsContent(registryDf, geographyDf, metricsDf):
    'Render the complete Impacts page layout and content.'

    st.markdown(Visuals.ParameterFiltersCss(), unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="filter-title">Category</div>', unsafe_allow_html=True)
        selectedCategories = Visuals.RenderCategoryMultiselectFilter(registryDf)
    with col2:
        st.markdown('<div class="filter-title">Organization</div>', unsafe_allow_html=True)
        selectedOrganizations = Visuals.RenderOrganizationMultiselectFilter(registryDf, selectedCategories)
    with col3:
        st.markdown('<div class="filter-title">Year</div>', unsafe_allow_html=True)
        selectedYear = Visuals.RenderYearSingleselectFilter(metricsDf)
    with col4:
        st.markdown('<div class="filter-title">Donor Type</div>', unsafe_allow_html=True)
        selectedDonorType = Visuals.RenderDonorTypeMultiselectFilter()

    previousFilters    = st.session_state.get('_impacts_previous_filters', {})
    currentFilters     = {'cat': selectedCategories, 'org': selectedOrganizations, 'year': selectedYear, 'donor': selectedDonorType}
    if previousFilters != currentFilters:
        st.session_state['impacts_llm_response'] = None
        st.session_state['_impacts_previous_filters'] = currentFilters
    if selectedYear is None: Visuals.RenderAlert()
    if selectedOrganizations:
        filteredMetricsDf = Data.FilterDf(metricsDf, selectedCategories, selectedOrganizations, selectedYear, None)
        if filteredMetricsDf.empty: Visuals.RenderAlert()

    organizationsDfs = Data.BuildOrganizationDfs(registryDf, geographyDf, metricsDf, selectedCategories, selectedOrganizations, selectedYear, selectedDonorType)
    categoryDfs      = Data.BuildCategoryDfs(registryDf, geographyDf, metricsDf, selectedCategories, selectedOrganizations, selectedYear, selectedDonorType)
    llmSummary       = Data.BuildLLMDf(organizationsDfs)
    boxesDfs         = organizationsDfs['Boxes']
    Visuals.RenderBoxes(boxesDfs)

    st.markdown('<br><br>', unsafe_allow_html=True)
    st.markdown("""<div style="height: 1px; width: 100%; background: linear-gradient(90deg, rgba(0,0,0,0) 0%, rgba(3,149,144,0.24) 12%, rgba(3,149,144,0.32) 50%, rgba(3,149,144,0.24) 88%, rgba(0,0,0,0) 100%); margin: 18px 0 6px 0;"></div>""", unsafe_allow_html=True)
    st.markdown('<br><br>', unsafe_allow_html=True)
    selectedParameter = Visuals.RenderParameter()
    dfs = organizationsDfs if selectedParameter == 'Organization' else categoryDfs

    col1, col2 = st.columns([1, 1])
    with col1: RenderPeopleProjects(dfs['PeopleProjects'], selectedParameter, 400)
    with col2: RenderSankey(dfs['Sankey'], registryDf, selectedParameter, 400)  

    RenderMap(dfs['ProjectsMap'], 400)
    RenderLlm(llmSummary)
    return