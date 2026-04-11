# Environment Setting
from pathlib import Path
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
import sys

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import configuration.StreamlitConfiguration as Configuration
import app.ui.Layout                        as UI

# Tooltips
def TooltipTheme(fontSize=None):
    'Shared tooltip tokens.'
    if fontSize is None: fontSize = Configuration.FontSize80
    return {
        'background' : f'rgba(85, 62, 76, {Configuration.Opacity85})',
        'border'     : 'rgba(155, 174, 188, 0.72)',
        'text'       : Configuration.WhiteColor,
        'radius'     : Configuration.Border1,
        'padding'    : '8px 10px',
        'fontFamily' : Configuration.FontFamily,
        'fontSize'   : fontSize,
        'lineHeight' : Configuration.LineHeight2,
        'shadow'     : 'none'}

def ChartCustomTooltipChartCss(containerHeight, chartHeight):
    'Returns scoped CSS for chart shell and custom rounded tooltip.'
    tooltipTheme  = TooltipTheme(fontSize=Configuration.FontSize80)

    return f"""<style>
        html, body {{margin: 0; padding: 0; overflow: hidden; background: transparent;}}
        #associates-chart-shell {{position: relative; height: {containerHeight}px; overflow-y: auto; overflow-x: hidden; border-radius: {Configuration.Border4}; background: transparent; box-shadow: 0 8px 28px rgba(var(--dp-primary-rgb), 0.14), 0 2px 8px rgba(var(--dp-primary-rgb), 0.08), inset 0 1px 0 rgba(255,255,255,0.70); scrollbar-width: none; margin: 0; padding: 0}}
        #associates-chart-shell::-webkit-scrollbar {{ width: 0; height: 0; background: transparent; }}
        #associates-chart-shell::-webkit-scrollbar-thumb {{ background: transparent; }}
        #associates-chart-shell .plotly-graph-div {{min-height: {chartHeight}px; height: {chartHeight}px;}}
        #associates-chart-shell .yaxislayer-above .ytick text,
        #associates-chart-shell .yaxislayer-below .ytick text {{font-weight: {Configuration.FontWeight4} !important;}}
        #associates-chart-tooltip {{position: absolute; display: none; pointer-events: none; z-index: 999; background: {tooltipTheme['background']}; color: {tooltipTheme['text']}; border: 1px solid {tooltipTheme['border']}; border-radius: {tooltipTheme['radius']}; padding: {tooltipTheme['padding']}; font-family: {tooltipTheme['fontFamily']}; font-size: {tooltipTheme['fontSize']}; line-height: {tooltipTheme['lineHeight']}; box-shadow: {tooltipTheme['shadow']}; white-space: nowrap}}
        .hoverlayer {{ pointer-events: none; }}
        .hovertext {{ border-radius: 10px !important; }}
        .hoverlayer .hovertext rect,
        .hoverlayer .hovertext .bg,
        .hoverlayer .bg {{ rx: 10 !important; ry: 10 !important; }}
    </style>"""

# Alert
def AlertCss():
    'Returns CSS styles for alert components, customizing their appearance.'
    return f"""<style>
        div[data-testid="stAlert"] {{background-color: {Configuration.Palette3E} !important; border: none !important; border-radius: {Configuration.RadiusCard}px !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stAlert"] > * {{background-color: {Configuration.Palette3E} !important; border: none !important; border-radius: {Configuration.RadiusCard}px !important; outline: none !important;}}
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
        .filter-title {{color: {Configuration.Palette3E} !important; font-size: {Configuration.FontSize95} !important; font-family: {Configuration.FontFamily} !important; font-weight: {Configuration.FontWeight6} !important; letter-spacing: {Configuration.LetterSpacing2} !important; margin-bottom: {Configuration.Spacing1} !important; line-height: {Configuration.LineHeight5} !important;}}

        div[data-testid="stMultiSelect"],
        div[data-testid="stSelectbox"] {{margin-bottom: 0 !important;}}

        div[data-testid="stMultiSelect"] > label,
        div[data-testid="stSelectbox"] > label {{ display: none !important; }}

        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child {{background: {Configuration.Palette3E} !important; border-color: {Configuration.Palette3D} !important; font-family: {Configuration.FontFamily} !important; font-size: {Configuration.FontSize80} !important; min-height: 2rem !important; height: 2rem !important; padding-top: 0 !important; padding-bottom: 0 !important; display: flex !important; align-items: center !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child > div {{padding-top: 0 !important; padding-bottom: 0 !important; min-height: 2rem !important; height: 2rem !important; display: flex !important; align-items: center !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
        div[data-testid="stSelectbox"] [data-baseweb="select"] div[role="combobox"] {{display: flex !important; align-items: center !important; min-height: 2rem !important; height: 2rem !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"] [aria-live="polite"] {{display: flex !important; align-items: center !important; line-height: 1 !important; min-height: 2rem !important;}}
        div[data-testid="stSelectbox"] [data-baseweb="select"] [id$="-select-value"],
        div[data-testid="stSelectbox"] [data-baseweb="select"] [data-baseweb="single-value"] {{display: flex !important; align-items: center !important; line-height: 2rem !important; height: 2rem !important;}}
        div[data-testid="stMultiSelect"] > div:focus-within,
        div[data-testid="stSelectbox"] > div:focus-within {{border-color: {Configuration.Palette3D} !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child:focus-within,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child:focus-within {{border-color: {Configuration.Palette3D} !important; box-shadow: none !important; outline: none !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="select"] > div:first-child *,
        div[data-testid="stSelectbox"] [data-baseweb="select"] > div:first-child * {{color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="placeholder"],
        div[data-testid="stSelectbox"] [data-baseweb="placeholder"] {{color: rgba(255,255,255,0.55) !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{background: {Configuration.Palette3D} !important; color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] * {{color: {Configuration.WhiteColor} !important;}}
        div[data-testid="stMultiSelect"] [data-baseweb="tag"] {{margin-top: 0 !important; margin-bottom: 0 !important; min-height: 1.4rem !important;}}

        /* Keep dropdown menu dark when filters are opened */
        div[data-baseweb="popover"] [role="listbox"],
        div[data-baseweb="popover"] ul {{background: {Configuration.Palette3E} !important; border: 1px solid {Configuration.Palette3D} !important;}}
        div[data-baseweb="popover"] [role="option"],
        div[data-baseweb="popover"] li {{background: {Configuration.Palette3E} !important; color: {Configuration.WhiteColor} !important;}}
        div[data-baseweb="popover"] [role="option"] *,
        div[data-baseweb="popover"] li * {{color: {Configuration.WhiteColor} !important;}}
        div[data-baseweb="popover"] [role="option"]:hover,
        div[data-baseweb="popover"] li:hover {{background: {Configuration.Palette3D} !important;}}
        div[data-baseweb="popover"] [role="option"][aria-selected="true"],
        div[data-baseweb="popover"] li[aria-selected="true"] {{background: {Configuration.Palette3B} !important; color: {Configuration.Palette3E} !important;}}
        div[data-baseweb="popover"] [role="option"][aria-selected="true"] *,
        div[data-baseweb="popover"] li[aria-selected="true"] * {{color: {Configuration.Palette3E} !important;}}

        div[data-testid="stRadio"] > label {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] {{display: flex !important; flex-wrap: nowrap !important; gap: {Configuration.Spacing1} !important; width: 100% !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] {{
            margin: 0 !important; padding: 2px {Configuration.Spacing4} !important; border-radius: 999px !important;
            border: 1px solid transparent !important; background: {Configuration.Palette3D} !important;
            color: {Configuration.WhiteColor} !important; font-size: {Configuration.FontSize90} !important;
            font-family: {Configuration.FontFamily} !important; flex: 1 1 0 !important; min-width: 180px !important;
            font-weight: {Configuration.FontWeight3} !important; transition: background-color 160ms ease, transform 160ms ease, box-shadow 160ms ease !important;
            cursor: pointer !important; display: flex !important; align-items: center !important;
            justify-content: center !important; text-align: center !important; white-space: nowrap !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:hover {{background: {Configuration.Palette3B} !important; color: {Configuration.Palette3E} !important; transform: translateY(-1px) !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12) !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] > div:last-child {{margin: 0 !important; padding: 0 !important; width: 100% !important; display: flex !important; justify-content: center !important; align-items: center !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] input {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"] div {{color: inherit !important; font-size: {Configuration.FontSize90} !important; font-family: {Configuration.FontFamily} !important; text-align: center !important; width: 100% !important; margin: 0 !important; justify-content: center !important; white-space: nowrap !important;}}
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"][aria-checked="true"],
        div[data-testid="stRadio"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {{background: {Configuration.Palette3E} !important; color: {Configuration.WhiteColor} !important; box-shadow: 0 6px 14px rgba(85, 62, 76, 0.28) !important;}}
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

# Table
def TableCss(tableHeight):
    'Returns CSS styles for tables, customizing their appearance and layout.'
    return f"""<style>
        /* Container con Scroll e Bordo Arrotondato */
        .scrollable-table-container {{max-height: {tableHeight}px; overflow-y: auto; overflow-x: auto; border-radius: {Configuration.Spacing3} !important; border: 1px solid rgba(255, 255, 255, 0.1); background-color: rgba(255, 255, 255, 0.1); backdrop-filter: blur(10px);}}
        .styled-table {{width: max-content; min-width: 100%; border-collapse: collapse; font-family: {Configuration.FontFamily}; background-color: transparent; table-layout: auto;}}

        /* Header: Sfondo scuro (o accent) e TESTO BIANCO */
        .styled-table th {{position: sticky; top: 0; background-color: {Configuration.Palette3D} !important; color: {Configuration.WhiteColor} !important; font-size: {Configuration.FontSize75} !important; font-weight: {Configuration.FontWeight3}; text-align: left; padding: 10px 12px !important; z-index: 2; letter-spacing: {Configuration.LetterSpacing2}; white-space: nowrap;}}

        /* Celle: Testo piccolo e scuro (o coerente con palette) */
        .styled-table td {{color: {Configuration.Palette3E} !important; font-size: {Configuration.FontSize75} !important; padding: 8px 12px !important; border-bottom: 1px solid rgba(0,0,0,0.05); background-color: rgba(255, 255, 255, 0.4); white-space: nowrap;}}

        /* Scrollbar sottile per non rovinare il design */
        .scrollable-table-container::-webkit-scrollbar {{ width: {Configuration.Spacing1}; }}
        .scrollable-table-container::-webkit-scrollbar:horizontal {{ height: {Configuration.Spacing1}; }}
        .scrollable-table-container::-webkit-scrollbar-thumb {{ background: rgba(0,0,0,0.1); border-radius: {Configuration.Spacing1}; }}
    </style>"""

def RenderTable(registry, tableHeight):
    'Renders a table with specific styling and columns.'
    st.markdown(TableCss(tableHeight), unsafe_allow_html=True)
    UI.ObjectTitleCss(Configuration.Palette3E, classSuffix='organizations-table')
    UI.ObjectSubtitleCss(Configuration.Palette3D, classSuffix='organizations-table')
    st.markdown("<div class='object-title-wrap-organizations-table'><div class='object-title-organizations-table'>Organizations Registry</div>", unsafe_allow_html=True)
    st.markdown("<p class='object-subtitle-organizations-table'>Detailed overview of registered organizations</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    tableHtml = registry.to_html(index=False, classes='styled-table', escape=False)
    st.markdown(f"<div class='scrollable-table-container'>{tableHtml}</div>", unsafe_allow_html=True)

# Associates
def GeneralCSS(radiusCard=None):
    'Returns CSS styles for Plotly chart containers, matching the Impacts page style.'
    if radiusCard is None: radiusCard = Configuration.RadiusCard + 15
    st.markdown(f"""
        <style>
            div[data-testid="stPlotlyChart"] {{background: {Configuration.WhiteColor} !important; border-radius: {radiusCard}px; overflow: hidden !important;}}
            div[data-testid="stPlotlyChart"] > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: {Configuration.WhiteColor} !important; border: 1px solid rgba(255, 255, 255, 0.75); backdrop-filter: blur(6px) saturate(120%); box-shadow: 0 14px 32px rgba(87, 66, 64, 0.14), inset 0 1px 0 rgba(255, 255, 255, 0.78);}}
            div[data-testid="stPlotlyChart"] > div > div {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
            div[data-testid="stPlotlyChart"] .js-plotly-plot,
            div[data-testid="stPlotlyChart"] .plot-container,
            div[data-testid="stPlotlyChart"] .svg-container {{border-radius: {radiusCard}px; overflow: hidden !important; background: transparent !important;}}
        </style>""", unsafe_allow_html=True)

def RenderPlotlyWithCustomTooltip(fig, containerHeight):
    'Render Plotly chart with a true rounded HTML tooltip.'
    chartHeight = int(fig.layout.height) if fig.layout.height else containerHeight
    fig.update_traces(hoverinfo='none', hovertemplate=None)

    plotHtml = pio.to_html(fig, include_plotlyjs='cdn', full_html=False, config={'displayModeBar': False, 'responsive': True, 'scrollZoom': False, 'doubleClick': False})
    css      = ChartCustomTooltipChartCss(containerHeight, chartHeight)
    html     = f"""{css}<div id="associates-chart-shell">{plotHtml}<div id="associates-chart-tooltip"></div></div>
    <script>
        (function() {{
            const shell = document.getElementById('associates-chart-shell');
            if (!shell) return;

            const chart = shell.querySelector('.plotly-graph-div');
            const tooltip = document.getElementById('associates-chart-tooltip');
            if (!chart || !tooltip || chart.dataset.tooltipBound === '1') return;

            chart.dataset.tooltipBound = '1';

            const formatValue = (value) => {{
                if (typeof value !== 'number') return value;
                return value.toLocaleString('it-IT');
            }};

            const moveTooltip = (evt) => {{
                const shellRect = shell.getBoundingClientRect();
                const x = (evt.clientX - shellRect.left) + 14 + shell.scrollLeft;
                const y = (evt.clientY - shellRect.top) + 14 + shell.scrollTop;
                tooltip.style.left = `${{x}}px`;
                tooltip.style.top = `${{y}}px`;
            }};

            chart.on('plotly_hover', (data) => {{
                const point = data && data.points && data.points[0];
                if (!point) return;

                const label = point.y ?? '';
                const metric = point.data && point.data.name ? point.data.name : 'Value';
                const value = formatValue(point.x);
                tooltip.innerHTML = `<div><strong>${{label}}</strong></div><div>${{metric}}: <strong>${{value}}</strong></div>`;
                tooltip.style.display = 'block';

                if (data.event) moveTooltip(data.event);
            }});

            chart.on('plotly_unhover', () => {{
                tooltip.style.display = 'none';
            }});

            chart.on('plotly_hover', (data) => {{
                if (data && data.event) moveTooltip(data.event);
            }});
        }})();
    </script>
    """

    st.components.v1.html(html, height=containerHeight)

def RenderAssociatesChart(associatesDf, parameter, chartHeight):
    'Renders a vertical stacked bar chart showing AssociatesPeople and AssociatesOrganizations by the given parameter.'
    associatesDf = associatesDf.sort_values(by=parameter, ascending=True).reset_index(drop=True)
    xValues      = associatesDf[parameter]
    barOpacity   = float(Configuration.Opacity85)
    labelColor   = Configuration.Palette3E
    tooltipTheme = TooltipTheme(fontSize=Configuration.FontSize80)

    fig = go.Figure()
    fig.add_trace(go.Bar(name          = 'Associated People',
                         x             = xValues,
                         y             = associatesDf['AssociatesPeople'],
                         marker        = dict(color=Configuration.Palette3E, opacity=barOpacity, line=dict(width=0)),
                         hovertemplate = '<b>%{x}</b><br>People: <b>%{y}</b><extra></extra>'))
    fig.add_trace(go.Bar(name          = 'Associated Organizations',
                         x             = xValues,
                         y             = associatesDf['AssociatesOrganizations'],
                         marker        = dict(color=Configuration.Palette3D, opacity=barOpacity, line=dict(width=0)),
                         hovertemplate = '<b>%{x}</b><br>Organizations: <b>%{y}</b><extra></extra>'))

    fig.update_layout(
        barmode       = 'stack',
        bargap        = 0.32,
        dragmode      = False,
        paper_bgcolor = Configuration.WhiteColor,
        plot_bgcolor  = Configuration.WhiteColor,
        font          = dict(family=Configuration.FontFamily, color=labelColor, size=11),
        margin        = dict(l=20, r=20, t=38, b=80, pad=0),
        height        = chartHeight,
        legend        = dict(orientation='h', yanchor='top', y=1.08, xanchor='left', x=0, font=dict(size=10, color=labelColor), bgcolor='rgba(0,0,0,0)', borderwidth=0),
        xaxis         = dict(showgrid=False, showline=False, zeroline=False, automargin=True, fixedrange=True, tickfont=dict(size=10, color=labelColor), tickangle=-45),
        yaxis         = dict(showgrid=False, showline=True, linecolor='rgba(85, 62, 76, 0.35)', linewidth=1, zeroline=False, fixedrange=True, tickfont=dict(size=11, color=labelColor)),
        hoverlabel    = dict(bgcolor=tooltipTheme['background'], bordercolor=tooltipTheme['background'], font=dict(color=tooltipTheme['text'], family=tooltipTheme['fontFamily'], size=12)))

    GeneralCSS()
    UI.ObjectTitleCss(Configuration.Palette3E, classSuffix='associates-chart')
    UI.ObjectSubtitleCss(Configuration.Palette3D, classSuffix='associates-chart')
    st.markdown(f"<div class='object-title-wrap-associates-chart'><div class='object-title-associates-chart'>Who is trusted more?</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='object-subtitle-associates-chart'>People and organizations affiliated by {parameter}</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True, 'scrollZoom': False, 'doubleClick': False})

# Workers
def RenderWorkersChart(workersDf, parameter, chartHeight):
    'Renders a stacked bar chart showing Workers by ContractType (genders summed), grouped by the given parameter.'
    mergeMap     = {'Dipendenti - Donne': 'Dipendenti', 'Dipendenti - Uomini': 'Dipendenti',
                    'Co.Co.Co. - Donne' : 'Co.Co.Co.',  'Co.Co.Co. - Uomini' : 'Co.Co.Co.',
                    'Partita IVA - Donne': 'Partita IVA','Partita IVA - Uomini': 'Partita IVA'}
    mergedColors = {'Dipendenti': Configuration.Palette3D, 'Co.Co.Co.': Configuration.Palette3E, 'Partita IVA': Configuration.Palette3C,
                    'Volontari' : Configuration.Palette1A, 'Servizio Civile': Configuration.Palette3B}
    mergedOrder  = ['Co.Co.Co.', 'Dipendenti', 'Partita IVA', 'Servizio Civile', 'Volontari']
    groupColumn  = 'ShortName' if parameter == 'Organization' else parameter

    workersDf                  = workersDf[workersDf['ContractType'] != 'Totale'].copy()
    workersDf['ContractType']  = workersDf['ContractType'].replace(mergeMap)
    pivoted                    = workersDf.groupby([groupColumn, 'ContractType'], as_index=False)['Workers'].sum().pivot(index=groupColumn, columns='ContractType', values='Workers').fillna(0)
    pivoted                    = pivoted.reindex(columns=[ct for ct in mergedOrder if ct in pivoted.columns])
    pivoted                    = pivoted.sort_index(ascending=True)
    yValues                    = pivoted.index.tolist()

    barOpacity   = float(Configuration.Opacity85)
    labelColor   = Configuration.Palette3E
    tooltipTheme = TooltipTheme(fontSize=Configuration.FontSize80)

    fig = go.Figure()
    for contractType in pivoted.columns:
        color = mergedColors.get(contractType, Configuration.Palette3D)
        fig.add_trace(go.Bar(name          = contractType,
                             y             = yValues,
                             x             = pivoted[contractType].tolist(),
                             orientation   = 'h',
                             marker        = dict(color=color, opacity=barOpacity, line=dict(width=0)),
                             hovertemplate = '<b>%{y}</b><br>' + contractType + ': <b>%{x}</b><extra></extra>'))

    fig.update_layout(
        barmode       = 'stack',
        bargap        = 0.32,
        dragmode      = False,
        paper_bgcolor = Configuration.WhiteColor,
        plot_bgcolor  = Configuration.WhiteColor,
        font          = dict(family=Configuration.FontFamily, color=labelColor, size=11),
        margin        = dict(l=92, r=12, t=38, b=20, pad=0),
        height        = chartHeight,
        legend        = dict(orientation='h', yanchor='top', y=1.08, xanchor='left', x=-0.03, font=dict(size=10, color=labelColor), bgcolor='rgba(0,0,0,0)', borderwidth=0),
        xaxis         = dict(showgrid=False, showline=True, linecolor='rgba(85, 62, 76, 0.35)', linewidth=1, zeroline=False, fixedrange=True, tickfont=dict(size=11, color=labelColor)),
        yaxis         = dict(showgrid=False, showline=False, zeroline=False, autorange='reversed', automargin=True, fixedrange=True, tickfont=dict(size=10, color=labelColor)),
        hoverlabel    = dict(bgcolor=tooltipTheme['background'], bordercolor=tooltipTheme['background'], font=dict(color=tooltipTheme['text'], family=tooltipTheme['fontFamily'], size=12)))

    GeneralCSS()
    UI.ObjectTitleCss(Configuration.Palette3E, classSuffix='workers-chart')
    UI.ObjectSubtitleCss(Configuration.Palette3D, classSuffix='workers-chart')
    st.markdown(f"<div class='object-title-wrap-workers-chart'><div class='object-title-workers-chart'>Who employes more people and how?</div>", unsafe_allow_html=True)
    st.markdown(f"<p class='object-subtitle-workers-chart'>Workers by {parameter}</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True, 'scrollZoom': False, 'doubleClick': False})