# Environment Setting
import folium
import json
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import sys
import urllib.request

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import configuration.StreamlitConfiguration as Configuration
import app.ui.Layout                        as UI

# Tooltips
def TooltipTheme(fontSize=None):
    'Shared tooltip tokens.'
    if fontSize is None: fontSize = Configuration.FontSize80
    return {
        'background' : f'rgba(28, 110, 125, {Configuration.Opacity85})',
        'border'     : 'rgba(75, 188, 142, 0.52)',
        'text'       : Configuration.WhiteColor,
        'radius'     : Configuration.Border1,
        'padding'    : '8px 10px',
        'fontFamily' : Configuration.FontFamily,
        'fontSize'   : fontSize,
        'lineHeight' : Configuration.LineHeight2,
        'shadow'     : 'none'}

# Alert
def AlertCss():
    'Returns CSS styles for alert components, customizing their appearance.'
    return f"""<style>
        div[data-testid="stAlert"] {{background-color: {Configuration.Palette2B} !important; border: none !important; border-radius: {Configuration.RadiusCard}px !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stAlert"] > * {{background-color: {Configuration.Palette2B} !important; border: none !important; border-radius: {Configuration.RadiusCard}px !important; outline: none !important;}}
        div[data-testid="stAlert"] p,
        div[data-testid="stAlert"] svg {{color: rgba(255,255,255,0.88) !important; fill: rgba(255,255,255,0.88) !important; font-family: {Configuration.FontFamily} !important; font-size: {Configuration.FontSize100} !important; font-weight: {Configuration.FontWeight4} !important;}}
    </style>"""

def RenderAlert():
    'Renders an alert message when no city is selected.'
    st.markdown(AlertCss(), unsafe_allow_html=True)
    st.info('⛔ No available data: please change organizations or year!')
    st.stop()

# Parameter
def ParameterFiltersCss():
    return f"""<style>
        .filter-title {{color: {Configuration.Palette2B} !important; font-size: {Configuration.FontSize95} !important; font-family: {Configuration.FontFamily} !important; font-weight: {Configuration.FontWeight6} !important; letter-spacing: {Configuration.LetterSpacing2} !important; margin-bottom: {Configuration.Spacing1} !important; line-height: {Configuration.LineHeight5} !important;}}

        div[data-testid="stMultiSelect"],
        div[data-testid="stSelectbox"] {{margin-bottom: 0 !important;}}

        div[data-testid="stMultiSelect"] > label,
        div[data-testid="stSelectbox"] > label {{ display: none !important; }}

        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child {{background: {Configuration.Palette2B} !important; border-color: {Configuration.Palette2C} !important; font-family: {Configuration.FontFamily} !important; font-size: {Configuration.FontSize80} !important; min-height: 2rem !important; height: 2rem !important; padding-top: 0 !important; padding-bottom: 0 !important; display: flex !important; align-items: center !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child > div {{padding-top: 0 !important; padding-bottom: 0 !important; min-height: 2rem !important; height: 2rem !important; display: flex !important; align-items: center !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] div[role="combobox"] {{display: flex !important; align-items: center !important; min-height: 2rem !important; height: 2rem !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"] [aria-live="polite"] {{display: flex !important; align-items: center !important; line-height: 1 !important; min-height: 2rem !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"] [id$="-select-value"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="single-value"] {{display: flex !important; align-items: center !important; line-height: 2rem !important; height: 2rem !important;}}
        div[data-testid="stMultiSelect"] > div:focus-within,
        div[data-testid="stSelectbox"] > div:focus-within {{border-color: {Configuration.Palette2C} !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child:focus-within,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child:focus-within {{border-color: {Configuration.Palette2C} !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child *,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child * {{color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="placeholder"],
        div[data-testid="stSelectbox"] [data-baseweb="placeholder"] {{color: rgba(255,255,255,0.55) !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{background: {Configuration.Palette2C} !important; color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] * {{color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{margin-top: 0 !important; margin-bottom: 0 !important; min-height: 1.4rem !important;}}

        /* Keep dropdown menu dark when filters are opened */
        div[data-baseweb="popover"] [role="listbox"],
        div[data-baseweb="popover"] ul {{background: {Configuration.Palette2B} !important; border: 1px solid {Configuration.Palette2C} !important;}}
        div[data-baseweb="popover"] [role="option"],
        div[data-baseweb="popover"] li {{background: {Configuration.Palette2B} !important; color: {Configuration.WhiteColor} !important;}}
        div[data-baseweb="popover"] [role="option"] *,
        div[data-baseweb="popover"] li * {{color: {Configuration.WhiteColor} !important;}}
        div[data-baseweb="popover"] [role="option"]:hover,
        div[data-baseweb="popover"] li:hover {{background: {Configuration.Palette2C} !important;}}
        div[data-baseweb="popover"] [role="option"][aria-selected="true"],
        div[data-baseweb="popover"] li[aria-selected="true"] {{background: {Configuration.Palette2D} !important; color: {Configuration.Palette2B} !important;}}
        div[data-baseweb="popover"] [role="option"][aria-selected="true"] *,
        div[data-baseweb="popover"] li[aria-selected="true"] * {{color: {Configuration.Palette2B} !important;}}

        div[data-testid="stRadio"] > label {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] {{display: flex !important; flex-wrap: nowrap !important; gap: {Configuration.Spacing1} !important; width: 100% !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {{
            margin: 0 !important; padding: 2px {Configuration.Spacing4} !important; border-radius: 999px !important;
            border: 1px solid transparent !important; background: {Configuration.Palette2C} !important;
            color: {Configuration.WhiteColor} !important; font-size: {Configuration.FontSize90} !important;
            font-family: {Configuration.FontFamily} !important; flex: 1 1 0 !important; min-width: 180px !important;
            font-weight: {Configuration.FontWeight3} !important; transition: background-color 160ms ease, transform 160ms ease, box-shadow 160ms ease !important;
            cursor: pointer !important; display: flex !important; align-items: center !important;
            justify-content: center !important; text-align: center !important; white-space: nowrap !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {{background: {Configuration.Palette2D} !important; color: {Configuration.Palette2B} !important; transform: translateY(-1px) !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child {{margin: 0 !important; padding: 0 !important; width: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div {{color: inherit !important; font-size: {Configuration.FontSize90} !important; font-family: {Configuration.FontFamily} !important; text-align: center !important; width: 100% !important; margin: 0 !important; justify-content: center !important; white-space: nowrap !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"],
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {{background: {Configuration.Palette2B} !important; color: {Configuration.WhiteColor} !important; box-shadow: 0 6px 14px rgba(28, 110, 125, 0.28) !important;}}
    </style>"""

def RenderParameter():
    'Renders the parameter.'
    st.markdown(f'<div class="filter-title">Select how you want to group data:</div>', unsafe_allow_html=True)
    selectedParameter = st.radio('Parametro', options=Configuration.Parameters, horizontal=True, index=0, key='accuracy_parameter_filter', label_visibility='collapsed')
    return selectedParameter

# Filters
def RenderCategoryMultiselectFilter(registryDf, selectedOrganizations=None):
    'Renders a multiselect input for choosing categories, scoped to selected organizations if any.'
    if selectedOrganizations is None:
        selectedOrganizations = st.session_state.get('filterOrganization', [])

    filteredRegistry     = registryDf[registryDf['Organization'].isin(selectedOrganizations)] if selectedOrganizations else registryDf
    categoryOptions      = sorted(filteredRegistry['Category'].dropna().unique())
    currentSelection     = st.session_state.get('filterCategory', [])
    validSelection       = [c for c in currentSelection if c in categoryOptions]

    if currentSelection  != validSelection: st.session_state['filterCategory'] = validSelection
    categorySelectedRaw  = st.multiselect('Category', options=categoryOptions, default=validSelection, placeholder='All', key='filterCategory', label_visibility='collapsed')
    return None if not categorySelectedRaw else categorySelectedRaw

def RenderOrganizationMultiselectFilter(registryDf, selectedCategories=None):
    'Renders a multiselect input for choosing organizations, scoped to selected categories if any.'
    filteredRegistry        = registryDf[registryDf['Category'].isin(selectedCategories)] if selectedCategories else registryDf
    organizationOptions     = sorted(filteredRegistry['Organization'].dropna().unique())
    currentSelection        = st.session_state.get('filterOrganization', [])
    validSelection          = [o for o in currentSelection if o in organizationOptions]

    if currentSelection     != validSelection: st.session_state['filterOrganization'] = validSelection
    organizationSelectedRaw = st.multiselect('Organization', options=organizationOptions, default=validSelection, placeholder='All', key='filterOrganization', label_visibility='collapsed')
    
    return None if not organizationSelectedRaw else organizationSelectedRaw

def RenderYearSingleselectFilter(metricDf):
    'Renders a single-choice multiselect for choosing the year, with options sorted in reverse chronological order.'
    retrievalYears = sorted(metricDf['Year'].dropna().unique(), reverse=True)
    defaultYear = [retrievalYears[0]] if retrievalYears else []
    selectedYearRaw = st.multiselect('Year', options=retrievalYears, default=defaultYear, max_selections=1, key='filterYear', label_visibility='collapsed')
    return selectedYearRaw[0] if selectedYearRaw else None

def RenderDonorTypeMultiselectFilter():
    'Renders a multiselect for choosing donor types, without a preselected value.'
    donorTypeOptions = sorted(Configuration.DonorTypes)
    donorTypeSelectedRaw = st.multiselect('Donor Type', options=donorTypeOptions, default=[], placeholder='All', key='filterDonorType', label_visibility='collapsed')
    return None if not donorTypeSelectedRaw else donorTypeSelectedRaw

# Boxes
def BoxesCss():
    'Returns CSS styles for impact metric boxes.'
    return f"""<style>
        .impact-box {{min-height: 106px; border-radius: {Configuration.Border3}; border: 1px solid rgba(255, 255, 255, 0.62); background: {Configuration.WhiteColor}; box-shadow: 0 8px 24px rgba(87, 66, 64, 0.10), inset 0 1px 0 rgba(255, 255, 255, 0.75); padding: {Configuration.Spacing1}px {Configuration.Spacing1}px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; gap: 4px; overflow: hidden;}}
        .impact-box-label {{color: {Configuration.Palette2B}; font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize75}; font-weight: {Configuration.FontWeight3}; letter-spacing: {Configuration.LetterSpacing2}; line-height: {Configuration.LineHeight4};}}
        .impact-box-value {{color: {Configuration.Palette2B}; font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize115}; font-weight: {Configuration.FontWeight5}; letter-spacing: {Configuration.LetterSpacing1}; line-height: {Configuration.LineHeight3};}}
        .impact-box-delta {{padding: 2px 8px; border-radius: 999px; font-family: {Configuration.FontFamily}; font-size: {Configuration.FontSize75}; font-weight: {Configuration.FontWeight4}; letter-spacing: {Configuration.LetterSpacing1}; line-height: {Configuration.LineHeight2}; border: 1px solid transparent;}}
        .impact-box-delta-positive {{color: #3e5d00; background: rgba(62, 93, 0, 0.12); border-color: rgba(62, 93, 0, 0.26);}}
        .impact-box-delta-negative {{color: #9a2b2e; background: rgba(169, 49, 55, 0.12); border-color: rgba(169, 49, 55, 0.26);}}
        .impact-box-delta-neutral {{color: {Configuration.Palette2B}; background: rgba(3, 149, 144, 0.08); border-color: rgba(3, 149, 144, 0.18);}}
    </style>"""

def FormatImpactMetric(value, unitMeasure):
    'Format impact metric values shown in boxes.'
    if value is None: return 'N/A'
    return f'{value:,.2f} {unitMeasure}'

def FormatImpactDelta(delta):
    'Build signed percentage delta and visual class against sector overall metric.'
    if delta is None or pd.isna(delta): return 'N/A', 'neutral'
    if delta > 0: return f'+{delta:.2f}% vs category average', 'positive'
    if delta < 0: return f'{delta:.2f}% vs category average', 'negative'
    return '0.0% vs category average', 'neutral'

def RenderBoxes(boxesDf):
    'Renders 4 horizontal boxes with impact metrics from a boxes dataframe.'   
    if boxesDf['Organization'].nunique() != 1:    
        st.markdown(AlertCss(), unsafe_allow_html=True)
        st.info('Please select a single organization to view impact metrics.')
        return
    
    boxRow      = boxesDf.iloc[0]
    metricOne   = boxRow.get('MetricOne')
    metricTwo   = boxRow.get('MetricTwo')
    metricThree = boxRow.get('MetricThree')
    metricFour  = boxRow.get('MetricFour')
    deltaOne    = boxRow.get('MetricOneDeltaCategory')
    deltaTwo    = boxRow.get('MetricTwoDeltaCategory')
    deltaThree  = boxRow.get('MetricThreeDeltaCategory')
    deltaFour   = boxRow.get('MetricFourDeltaCategory')
    
    st.markdown(BoxesCss(), unsafe_allow_html=True)
    UI.ObjectTitleCss(Configuration.Palette2B, classSuffix='impacts-boxes')
    UI.ObjectSubtitleCss(Configuration.Palette2C, classSuffix='impacts-boxes')
    st.markdown("<div class='object-title-wrap-impacts-boxes'><div class='object-title-impacts-boxes'>What did 100 € of donations achieve?</div>", unsafe_allow_html=True)
    st.markdown("<p class='object-subtitle-impacts-boxes'>Donation impacts under several dimensions</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    boxes = [
        {'label': 'Indirect Projects', 'value': FormatImpactMetric(metricOne, '% of project funded'), 'delta': FormatImpactDelta(deltaOne)},
        {'label': 'Direct Projects', 'value': FormatImpactMetric(metricTwo, '% of project funded'), 'delta': FormatImpactDelta(deltaTwo)},
        {'label': 'Humans', 'value': FormatImpactMetric(metricThree, 'people impacted'), 'delta': FormatImpactDelta(deltaThree)},
        {'label': 'Expenses', 'value': FormatImpactMetric(metricFour, '€ spent'), 'delta': FormatImpactDelta(deltaFour)}]
    
    columns = st.columns(4, gap='small')
    for column, box in zip(columns, boxes):
        with column:
            deltaValue, deltaClass = box['delta']
            st.markdown(f"""
                <div class='impact-box'>
                    <div class='impact-box-label'>{box['label']}</div>
                    <div class='impact-box-value'>{box['value']}</div>
                    <div class='impact-box-delta impact-box-delta-{deltaClass}'>{deltaValue}</div>
                </div>""", unsafe_allow_html=True)

# Charts
def GeneralCSS(radiusCard = Configuration.RadiusCard + 15):
    'Returns CSS styles for charts.'
    st.markdown(f"""
        <style>
            div[data-testid="stPlotlyChart"] {{background: {Configuration.WhiteColor} !important; border-radius: {radiusCard}px; overflow: hidden !important;}}
            div[data-testid="stPlotlyChart"] > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: {Configuration.WhiteColor} !important; border: 1px solid rgba(255, 255, 255, 0.75); backdrop-filter: blur(6px) saturate(120%); box-shadow: 0 14px 32px rgba(87, 66, 64, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78);}}
            div[data-testid="stPlotlyChart"] > div > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
            div[data-testid="stPlotlyChart"] .js-plotly-plot,
            div[data-testid="stPlotlyChart"] .plot-container,
            div[data-testid="stPlotlyChart"] .svg-container {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
        </style>""", unsafe_allow_html=True)
    
# People & Projects Chart
def PeopleProjectsCss(radiusCard = Configuration.RadiusCard + 12):
    'Returns CSS styles for the people vs projects scatterplot chart.'
    st.markdown(f"""
        <style>
            div[data-testid="stPlotlyChart"] {{background: {Configuration.WhiteColor} !important; border-radius: {radiusCard}px; overflow: hidden !important;}}
            div[data-testid="stPlotlyChart"] > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: {Configuration.WhiteColor} !important; border: 1px solid rgba(255, 255, 255, 0.75); backdrop-filter: blur(6px) saturate(120%); box-shadow: 0 14px 32px rgba(87, 66, 64, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78);}}
            div[data-testid="stPlotlyChart"] > div > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
            div[data-testid="stPlotlyChart"] .js-plotly-plot,
            div[data-testid="stPlotlyChart"] .plot-container,
            div[data-testid="stPlotlyChart"] .svg-container {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
        </style>""", unsafe_allow_html=True)

def RenderPeopleProjects(df, parameter, chartHeight):
    'Renders a beneficiaries vs projects scatterplot.'
    PeopleProjectsCss()
    UI.ObjectTitleCss(Configuration.Palette2B, classSuffix='people-projects-scatter-modern')
    UI.ObjectSubtitleCss(Configuration.Palette2C, classSuffix='people-projects-scatter-modern')
    st.markdown(f"<div class='object-title-wrap-people-projects-scatter-modern'><div class='object-title-people-projects-scatter-modern'>Which {parameter} has the biggest impacts?</div>", unsafe_allow_html=True)
    st.markdown(f'<p class="object-subtitle-people-projects-scatter-modern">People & Projects by {parameter}</p></div>', unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)

    chartDf                  = df.copy()
    entityColumn             = parameter if parameter in chartDf.columns else ('Organization' if 'Organization' in chartDf.columns else 'Category')
    chartDf['Projects']      = pd.to_numeric(chartDf['Projects'], errors='coerce').fillna(0)
    chartDf['Beneficiaries'] = pd.to_numeric(chartDf['Beneficiaries'], errors='coerce').fillna(0)

    if 'SplitProjects' in chartDf.columns and chartDf['SplitProjects'].notna().any(): medianProjects = float(pd.to_numeric(chartDf['SplitProjects'], errors='coerce').dropna().median())
    else: medianProjects = float(pd.to_numeric(chartDf['MedianProjects'], errors='coerce').dropna().median())
    if 'SplitBeneficiaries' in chartDf.columns and chartDf['SplitBeneficiaries'].notna().any(): medianPeople = float(pd.to_numeric(chartDf['SplitBeneficiaries'], errors='coerce').dropna().median())
    else: medianPeople = float(pd.to_numeric(chartDf['MedianBeneficiaries'], errors='coerce').dropna().median())

    clusterColors  = {'Under Development': Configuration.Palette2F, 'Scale to Unlock': Configuration.Palette2E, 'Efficient Reach': Configuration.Palette2C, 'High Impact': Configuration.Palette2A}

    xMin   = float(chartDf['Projects'].min())
    xMax   = float(chartDf['Projects'].max())
    yMin   = float(chartDf['Beneficiaries'].min())
    yMax   = float(chartDf['Beneficiaries'].max())
    xPad   = (xMax - xMin) * 0.08 if xMax > xMin else 1
    yPad   = (yMax - yMin) * 0.10 if yMax > yMin else 1
    xRange = [xMin - xPad, xMax + xPad]
    yRange = [yMin - yPad, yMax + yPad]

    outerBubbleSize = 25
    innerBubbleSize = 10
    mainBubbleSize  = 15

    fig = go.Figure()
    fig.add_shape(type='rect', x0=xRange[0], x1=medianProjects, y0=yRange[0], y1=medianPeople, fillcolor=clusterColors['Under Development'], opacity=0.32, line=dict(width=0), layer='below')
    fig.add_shape(type='rect', x0=medianProjects, x1=xRange[1], y0=yRange[0], y1=medianPeople, fillcolor=clusterColors['Efficient Reach'], opacity=0.32, line=dict(width=0), layer='below')
    fig.add_shape(type='rect', x0=xRange[0], x1=medianProjects, y0=medianPeople, y1=yRange[1], fillcolor=clusterColors['Scale to Unlock'], opacity=0.32, line=dict(width=0), layer='below')
    fig.add_shape(type='rect', x0=medianProjects, x1=xRange[1], y0=medianPeople, y1=yRange[1], fillcolor=clusterColors['High Impact'], opacity=0.32, line=dict(width=0), layer='below')

    chartDf['DisplayCluster'] = 'Under Development'
    chartDf.loc[(chartDf['Projects'] >= medianProjects) & (chartDf['Beneficiaries'] < medianPeople), 'DisplayCluster'] = 'Efficient Reach'
    chartDf.loc[(chartDf['Projects'] < medianProjects) & (chartDf['Beneficiaries'] >= medianPeople), 'DisplayCluster'] = 'Scale to Unlock'
    chartDf.loc[(chartDf['Projects'] >= medianProjects) & (chartDf['Beneficiaries'] >= medianPeople), 'DisplayCluster'] = 'High Impact'

    for clusterName in ['Under Development', 'Scale to Unlock', 'Efficient Reach', 'High Impact']:
        clusterDf  = chartDf[chartDf['DisplayCluster'] == clusterName]
        color      = clusterColors.get(clusterName, Configuration.Palette2F)
        fig.add_trace(go.Scatter(
            x=clusterDf['Projects'],
            y=clusterDf['Beneficiaries'],
            mode='markers',
            showlegend=False,
            hoverinfo='skip',
            marker=dict(color=color, opacity=0.16, size=outerBubbleSize, line=dict(width=0))))

        fig.add_trace(go.Scatter(
            x=clusterDf['Projects'],
            y=clusterDf['Beneficiaries'],
            mode='markers',
            showlegend=False,
            hoverinfo='skip',
            marker=dict(color='rgba(255, 255, 255, 0.33)', opacity=0.55, size=innerBubbleSize, line=dict(width=0))))

        fig.add_trace(go.Scatter(
            name=clusterName,
            x=clusterDf['Projects'],
            y=clusterDf['Beneficiaries'],
            mode='markers',
            marker=dict(color=color, opacity=0.92, size=mainBubbleSize, line=dict(width=0)),
            customdata=clusterDf[entityColumn].astype(str),
            hovertemplate=f'<b>%{{customdata}}</b><br>Projects: <b>%{{x:,.0f}}</b><br>Beneficiaries: <b>%{{y:,.0f}}</b><extra></extra>'))

    fig.add_shape(type='line', x0=medianProjects, x1=medianProjects, y0=yRange[0], y1=yRange[1], line=dict(color=Configuration.WhiteColor, width=1.2, dash='dash'))
    fig.add_shape(type='line', x0=xRange[0], x1=xRange[1], y0=medianPeople, y1=medianPeople, line=dict(color=Configuration.WhiteColor, width=1.2, dash='dash'))

    fig.update_layout(
        dragmode=False,
        paper_bgcolor=Configuration.WhiteColor,
        plot_bgcolor=Configuration.WhiteColor,
        font=dict(family=Configuration.FontFamily, color='#000000', size=11),
        margin=dict(l=58, r=28, t=18, b=62, pad=0),
        height=chartHeight,
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0, font=dict(size=9, color='#000000'), bgcolor='rgba(0,0,0,0)', borderwidth=0),
        xaxis=dict(title=dict(text='Projects', font=dict(color='#000000', size=10)), range=xRange, showgrid=False, showline=True, linecolor='#000000', linewidth=1.2, zeroline=False, fixedrange=True, tickfont=dict(color='#000000', size=9)),
        yaxis=dict(title=dict(text='Beneficiaries', font=dict(color='#000000', size=10)), range=yRange, showgrid=False, showline=True, linecolor='#000000', linewidth=1.2, zeroline=False, fixedrange=True, tickfont=dict(color='#000000', size=9)),
        hovermode='closest')

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True, 'scrollZoom': False, 'doubleClick': False})

# Map
def MapContainerCss(mapHeight):
    'Returns CSS styles for a transparent wrapper and rounded map area.'
    return f"""<style>
                html, body {{ margin: 0; padding: 0; overflow: hidden; background: transparent; }}
                .map-shell {{ position: relative; background: transparent; border: none; box-shadow: none; height: {mapHeight}px; }}
                .map-container {{ border-radius: {Configuration.Border4}; overflow: hidden; isolation: isolate; background: {Configuration.WhiteColor}; height: {mapHeight}px; }}
                .map-container .folium-map,
                .map-container .leaflet-container,
                .map-container .leaflet-pane,
                .map-container .leaflet-tile-pane {{background: {Configuration.WhiteColor} !important;}}
                .map-container iframe {{height: {mapHeight}px !important; width: 100% !important; filter: saturate(1.02) contrast(1.01);}}
                </style>"""

def FetchWorldGeoJsonRaw(worldGeoJsonUrl):
    'Fetch and cache the world GeoJSON as a raw string to avoid repeated HTTP calls.'
    with urllib.request.urlopen(worldGeoJsonUrl, timeout=10) as response: return response.read().decode('utf-8')

def BuildMapGeoJson(projectsMapDf, worldGeoJsonUrl = Configuration.WorldGeoJsonUrl):
    'Build a world GeoJSON enriched with Projects values by country.'
    geoJsonData       = json.loads(FetchWorldGeoJsonRaw(worldGeoJsonUrl))
    projectsByCountry = projectsMapDf.groupby('Country')['Projects'].sum().astype(int).to_dict()

    for feature in geoJsonData['features']:
        countryName                       = feature.get('properties', {}).get('name')
        feature['properties']['projects'] = projectsByCountry.get(countryName, 0)

    return geoJsonData

def CountryColor(projects, totalProjects):
    'Return a color-based shade according to project intensity.'
    if totalProjects <= 0: return '#717171'
    ratio = projects / totalProjects
    if ratio >= 0.025: return Configuration.Palette2B
    if ratio >= 0.005: return Configuration.Palette2D
    if ratio > 0: return Configuration.Palette2F
    return '#717171'

def RenderMap(projectsMapDf, mapHeight):
    'Renders a cyberpunk choropleth map from a DataFrame with Country and Projects columns.'
    mapObject     = folium.Map(location=[25, 10], zoom_start=2, tiles=None, prefer_canvas=True)
    geoJsonData   = BuildMapGeoJson(projectsMapDf)
    totalProjects = int(projectsMapDf['Projects'].fillna(0).sum())
    tooltipTheme  = TooltipTheme(fontSize=Configuration.FontSize100)

    folium.TileLayer(tiles='https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png',
                     attr='&copy; OpenStreetMap contributors &copy; CARTO',
                     name='No Labels').add_to(mapObject)

    folium.GeoJson(geoJsonData,
                   style_function=lambda feature: {'fillColor': CountryColor(feature['properties'].get('projects', 0), totalProjects), 'color': Configuration.Palette2D, 'weight': 0.6, 'fillOpacity': Configuration.Opacity85},
                   highlight_function=lambda feature: {'fillOpacity': Configuration.Opacity95, 'weight': 1.25, 'color': Configuration.Palette2F},
                   tooltip=folium.features.GeoJsonTooltip(fields=['name', 'projects'], aliases=['Country', 'Projects'], localize=True,
                                      style=(f'background-color: {tooltipTheme["background"]}; color: {tooltipTheme["text"]}; '
                                          f'border: 1px solid {tooltipTheme["border"]}; border-radius: {tooltipTheme["radius"]}; '
                                          f'font-family: {tooltipTheme["fontFamily"]}; font-size: {tooltipTheme["fontSize"]}; padding: {tooltipTheme["padding"]}; '
                                          f'box-shadow: {tooltipTheme["shadow"]};'),),).add_to(mapObject)


    UI.ObjectTitleCss(Configuration.Palette2B, classSuffix='projects-map')
    UI.ObjectSubtitleCss(Configuration.Palette2C, classSuffix='projects-map')
    st.markdown("<div class='object-title-wrap-projects-map'><div class='object-title-projects-map'>How many projects are active internationally?</div>", unsafe_allow_html=True)
    st.markdown("<p class='object-subtitle-projects-map'>Global distribution of projects</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.components.v1.html(f"{MapContainerCss(mapHeight)}<div class='map-shell'><div class='map-container'>{mapObject._repr_html_()}</div></div>", height=mapHeight)

# Sankey Diagram
def SankeyCss(radiusCard = Configuration.RadiusCard + 15):
    'Returns CSS styles for Sankey diagram chart.'
    st.markdown(f"""
        <style>
            div[data-testid="stPlotlyChart"] {{background: {Configuration.WhiteColor} !important; border-radius: {radiusCard}px; overflow: hidden !important;}}
            div[data-testid="stPlotlyChart"] > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: {Configuration.WhiteColor} !important; border: 1px solid rgba(255, 255, 255, 0.75); backdrop-filter: blur(6px) saturate(120%); box-shadow: 0 14px 32px rgba(87, 66, 64, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78);}}
            div[data-testid="stPlotlyChart"] > div > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
            div[data-testid="stPlotlyChart"] .js-plotly-plot,
            div[data-testid="stPlotlyChart"] .plot-container,
            div[data-testid="stPlotlyChart"] .svg-container {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
        </style>""", unsafe_allow_html=True)

def HexToRgb(hexColor):
    'Convert a hex color string to an RGB tuple.'
    cleanedHex = str(hexColor).strip().lstrip('#')
    return tuple(int(cleanedHex[i:i + 2], 16) for i in (0, 2, 4))

def RgbToHex(rgb):
    'Convert an RGB tuple to a hex color string.'
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def RenderSankey(sankeyDf, registryDf, parameter, chartHeight):
    'Renders a 3-step Sankey diagram: Funding → Revenue → ExpenseMissions.'  
    df = sankeyDf.copy()

    parameterColumn = parameter if parameter in df.columns else ('Organization' if 'Organization' in df.columns else 'Category')
    numericColumns  = ['Fundings', 'Revenues', 'ExpenseProjects', 'ExpenseStructure', 'ExpenseFundings']
    for column in numericColumns: df[column] = pd.to_numeric(df.get(column, 0), errors='coerce').fillna(0)

    df = (df.groupby(parameterColumn, as_index=False)[numericColumns].sum().sort_values(by='ExpenseProjects', ascending=False).reset_index(drop=True))
    df = df[(df[numericColumns].sum(axis=1) > 0)].reset_index(drop=True)
    if parameterColumn      == 'Organization' and registryDf is not None and {'Organization', 'ShortName'}.issubset(registryDf.columns):
        shortNameMap        = (registryDf[['Organization', 'ShortName']].dropna(subset=['Organization']).drop_duplicates(subset=['Organization']).set_index('Organization')['ShortName'])
        df[parameterColumn] = df[parameterColumn].map(shortNameMap).fillna(df[parameterColumn])

    entityLabels      = df[parameterColumn].astype(str).tolist()
    labels            = entityLabels + ([''] * len(entityLabels)) + ([''] * len(entityLabels))
    nodeValuesFunding = [float(value) for value in df['Fundings'].tolist()]
    nodeValuesRevenue = [float(value) for value in df['Revenues'].tolist()]
    nodeValuesExpense = [float(value) for value in (df['ExpenseProjects'] + df['ExpenseStructure'] + df['ExpenseFundings']).tolist()]
    nodeCustomData    = nodeValuesFunding + nodeValuesRevenue + nodeValuesExpense

    gradientAnchors = [
        HexToRgb(Configuration.Palette2A),
        HexToRgb(Configuration.Palette2B),
        HexToRgb(Configuration.Palette2C),
        HexToRgb(Configuration.Palette2D),
        HexToRgb(Configuration.Palette2E),
        HexToRgb(Configuration.Palette2F)
    ]
    entityCount  = len(entityLabels)
    colorSteps   = max(entityCount - 1, 1)
    entityColors = []
    for index in range(entityCount):
        ratio = index / colorSteps if colorSteps > 0 else 0
        scaled = ratio * (len(gradientAnchors) - 1)
        leftIndex = min(int(scaled), len(gradientAnchors) - 2)
        rightIndex = leftIndex + 1
        localRatio = scaled - leftIndex
        leftRgb = gradientAnchors[leftIndex]
        rightRgb = gradientAnchors[rightIndex]
        interpolatedRgb = (
            leftRgb[0] + (rightRgb[0] - leftRgb[0]) * localRatio,
            leftRgb[1] + (rightRgb[1] - leftRgb[1]) * localRatio,
            leftRgb[2] + (rightRgb[2] - leftRgb[2]) * localRatio)
        entityColors.append(RgbToHex(interpolatedRgb))

    nodeColors = entityColors + entityColors + entityColors
    nodeX      = ([0.02] * entityCount) + ([0.50] * entityCount) + ([0.98] * entityCount)

    fundingStartIndex  = 0
    revenueStartIndex  = len(entityLabels)
    expensesStartIndex = len(entityLabels) * 2

    sources    = []
    targets    = []
    values     = []
    linkColors = []

    for index, row in df.iterrows():
        fundingNodeIndex = fundingStartIndex + index
        revenueNodeIndex = revenueStartIndex + index
        expenseNodeIndex = expensesStartIndex + index
        expenseTotal     = float(row['ExpenseProjects'] + row['ExpenseStructure'] + row['ExpenseFundings'])

        if row['Fundings'] > 0:
            sources.append(fundingNodeIndex)
            targets.append(revenueNodeIndex)
            values.append(float(row['Fundings']))
            linkColors.append('rgba(28, 110, 125, 0.24)')

        if expenseTotal > 0:
            sources.append(revenueNodeIndex)
            targets.append(expenseNodeIndex)
            values.append(expenseTotal)
            linkColors.append('rgba(3, 149, 144, 0.26)')
   
    SankeyCss()
    UI.ObjectTitleCss(Configuration.Palette2B, classSuffix='sankey-diagram')
    UI.ObjectSubtitleCss(Configuration.Palette2C, classSuffix='sankey-diagram')
    st.markdown(f"<div class='object-title-wrap-sankey-diagram'><div class='object-title-sankey-diagram'>Who invests more in projects?</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='object-subtitle-sankey-diagram'>Funding ---> Revenue ---> Projects Expenses</p></div>", unsafe_allow_html=True)
    st.markdown('<br>', unsafe_allow_html=True)
    
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='rgba(0, 0, 0, 0.1)', width=0.5),
            color=nodeColors,
            label=labels,
            customdata=nodeCustomData,
            hovertemplate='%{customdata:,.0f}<extra></extra>',
            x=nodeX
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=linkColors,
            hovertemplate='Flow: %{value:,.0f}<extra></extra>'
        )
    )])
    
    fig.update_layout(
        paper_bgcolor=Configuration.WhiteColor,
        plot_bgcolor=Configuration.WhiteColor,
        font=dict(family=Configuration.FontFamily, color='#000000', size=11),
        margin=dict(l=20, r=20, t=20, b=20, pad=0),
        height=chartHeight,
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True, 'scrollZoom': False, 'doubleClick': False})