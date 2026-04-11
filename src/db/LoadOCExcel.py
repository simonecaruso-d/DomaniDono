# Environment Setting
import pandas as pd
from pathlib import Path
import sys

SrcPath = Path(__file__).resolve().parents[1]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

import configuration.LoadingConfiguration as Configuration
import db.LoadingHelpers                  as Helpers

# Individual Dataframes
def BuildRegistryDf(sheetDf):
    'Build normalized Registry DataFrame.'
    dataFrame = sheetDf.copy().rename(columns=Configuration.RegistryColumnMap)

    for column in Configuration.RegistryTextColumns:
        if column in dataFrame.columns:
            dataFrame[column] = Helpers.CleanTextSeries(dataFrame[column])

    for integerColumn in Configuration.RegistryNumericColumns:
        if integerColumn in dataFrame.columns: dataFrame[integerColumn] = pd.to_numeric(dataFrame[integerColumn], errors='coerce').astype('Int64')

    return dataFrame.sort_values(['Organization', 'Category'], na_position='last').reset_index(drop=True)

def BuildMetricsDf(sheetDf):
    'Build normalized Metrics DataFrame.'
    dataFrame = sheetDf.copy().rename(columns=Configuration.MetricsColumnMap)

    for textColumn in Configuration.MetricsTextColumns:
        if textColumn in dataFrame.columns: dataFrame[textColumn] = Helpers.CleanTextSeries(dataFrame[textColumn])

    dataFrame['Year'] = pd.to_numeric(dataFrame['Year'], errors='coerce').astype('Int64')
    dataFrame['Value'] = pd.to_numeric(dataFrame['Value'], errors='coerce')

    return dataFrame.sort_values(['Organization', 'Year', 'Domain', 'Specific'], na_position='last').reset_index(drop=True)

def BuildGeographicDf(sheetDf):
    'Build normalized Geographic DataFrame.'
    dataFrame = sheetDf.copy()

    for textColumn in Configuration.GeographicTextColumns:
        if textColumn in dataFrame.columns: dataFrame[textColumn] = Helpers.CleanTextSeries(dataFrame[textColumn])

    dataFrame['Year'] = pd.to_numeric(dataFrame['Year'], errors='coerce').astype('Int64')
    dataFrame['Projects'] = pd.to_numeric(dataFrame['Projects'], errors='coerce').astype('Int64')

    dataFrame = dataFrame.sort_values(['Organization', 'Year', 'Country'], na_position='last').reset_index(drop=True)
    return dataFrame

# Wrapper
def BuildAllDfs():
    'Load workbook and return three normalized DataFrames, one per sheet.'
    sheets = pd.read_excel(Configuration.ExcelPath, sheet_name=['Anagrafica', 'Per Anno', 'Projects By Country'], engine='openpyxl')

    registryDf   = BuildRegistryDf(sheets['Anagrafica'])
    metricsDf    = BuildMetricsDf(sheets['Per Anno'])
    metricsDf    = metricsDf.merge(registryDf[['Organization', 'ShortName', 'Category']], on='Organization', how='left')
    geographicDf = BuildGeographicDf(sheets['Projects By Country'])
    geographicDf = geographicDf.merge(registryDf[['Organization', 'ShortName', 'Category']], on='Organization', how='left')

    return registryDf, metricsDf, geographicDf

# Run
RegistryDf, MetricsDf, GeographicDf = BuildAllDfs()