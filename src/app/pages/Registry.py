# Environment Setting
from pathlib import Path
import streamlit as st
import sys

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import app.pages.StreamlitData              as Data
import app.pages.RegistryVisuals            as Visuals

# Wrapper
@st.fragment
def RenderAssociatesColumn(registry, selectedParameter, selectedCategory, selectedOrganizations):
    'Isolated fragment.'
    associatesDf = Data.BuildAssociates(registry, selectedParameter, selectedCategory, selectedOrganizations)
    Visuals.RenderAssociatesChart(associatesDf, selectedParameter, 400)

@st.fragment
def RenderWorkersColumn(metrics, selectedParameter, selectedCategory, selectedOrganizations, selectedYear):
    'Isolated fragment.'
    workersDf = Data.BuildWorkers(metrics, selectedCategory, selectedOrganizations, selectedYear)
    Visuals.RenderWorkersChart(workersDf, selectedParameter, 400)

@st.fragment
def RenderTable(registry, selectedCategory, selectedOrganizations):
    'Isolated fragment.'
    registryTableDf = Data.BuildRegistry(registry, selectedCategory, selectedOrganizations)
    Visuals.RenderTable(registryTableDf, 400)

@st.fragment
def RenderRegistryContent(registry, metrics):
    'Render the complete Registry page layout and content.'

    st.markdown(Visuals.ParameterFiltersCss(), unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="filter-title">Category</div>', unsafe_allow_html=True)
        selectedCategory = Visuals.RenderCategoryMultiselectFilter(registry)
    with col2:
        st.markdown('<div class="filter-title">Organization</div>', unsafe_allow_html=True)
        selectedOrganizations = Visuals.RenderOrganizationMultiselectFilter(registry, selectedCategory)
    with col3:
        st.markdown('<div class="filter-title">Year</div>', unsafe_allow_html=True)
        selectedYear = Visuals.RenderYearSingleselectFilter(metrics)

    st.markdown("<br>", unsafe_allow_html=True)
    selectedParameter = Visuals.RenderParameter()

    col1, col2 = st.columns([1, 1], gap='large')
    with col1: RenderWorkersColumn(metrics, selectedParameter, selectedCategory, selectedOrganizations, selectedYear)
    with col2: RenderAssociatesColumn(registry, selectedParameter, selectedCategory, selectedOrganizations)

    st.markdown('<br>', unsafe_allow_html=True)
    RenderTable(registry, selectedCategory, selectedOrganizations)