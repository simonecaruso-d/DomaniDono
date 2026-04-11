# Environment Setting
import pandas as pd

# Helpers
def CleanTextSeries(series):
    'Normalize text values by trimming and collapsing internal spaces.'
    cleanSeries = series.astype('string').str.replace(r"\s+", " ", regex=True).str.strip()
    return cleanSeries.replace('', pd.NA)