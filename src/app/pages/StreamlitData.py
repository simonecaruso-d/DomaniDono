# Environment Setting
import pandas as pd
from pathlib import Path
import sys
import streamlit as st

SrcPath = Path(__file__).resolve().parents[2]
if str(SrcPath) not in sys.path: sys.path.insert(0, str(SrcPath))

# Helpers
def AddDeltaPreviousYear(df, valueColumn, entityColumns, yearColumn='Year', deltaColumn='DeltaPreviousYear'):
    'Adds percentage delta vs previous year for the same entity columns.'
    previousValueColumn    = f'{valueColumn}PreviousYear'
    dfPrevious             = df[entityColumns + [yearColumn, valueColumn]].copy()
    dfPrevious[yearColumn] = dfPrevious[yearColumn] + 1
    dfPrevious             = dfPrevious.rename(columns={valueColumn: previousValueColumn})
    df                     = df.merge(dfPrevious, on=entityColumns + [yearColumn], how='left')
    validPrevious          = df[previousValueColumn].notna() & (df[previousValueColumn] != 0)
    df[deltaColumn]        = ((df[valueColumn] - df[previousValueColumn]) / df[previousValueColumn]).where(validPrevious, None)
    return df

def AddDeltaAgainstGroupMean(df, valueColumn, groupColumns, deltaColumn='DeltaCategory', meanColumn='CategoryMean'):
    'Adds percentage delta vs mean of other entities in the same group.'
    sumColumn       = f'{valueColumn}GroupSum'
    countColumn     = f'{valueColumn}GroupCount'
    dfGroup         = (df.groupby(groupColumns)[valueColumn].agg(['sum', 'count']).reset_index().rename(columns={'sum': sumColumn, 'count': countColumn}))
    df              = df.merge(dfGroup, on=groupColumns, how='left')
    df[meanColumn]  = ((df[sumColumn] - df[valueColumn]) / (df[countColumn] - 1)).where(df[countColumn] > 1, None)
    validGroup      = df[meanColumn].notna() & (df[meanColumn] != 0)
    df[deltaColumn] = ((df[valueColumn] - df[meanColumn]) / df[meanColumn]).where(validGroup, None)
    return df

def BuildScoreSeries(series, higherIsBetter=True, minScore=0, maxScore=100, neutralScore=50):
    'Transforms a numeric series into an integer score between minScore and maxScore based on rank order.'
    numericSeries = pd.to_numeric(series, errors='coerce')
    scoreSeries   = pd.Series(pd.NA, index=series.index, dtype='Int64')
    validSeries   = numericSeries.dropna()

    if validSeries.nunique() <= 1:
        scoreSeries.loc[validSeries.index] = int(neutralScore)
        return scoreSeries

    ascendingRank = validSeries.rank(method='average', ascending=True)
    normalized    = (ascendingRank - 1) / (len(validSeries) - 1)
    if not higherIsBetter: normalized = 1 - normalized

    scaledScores = (minScore + normalized * (maxScore - minScore)).round().clip(minScore, maxScore)
    scoreSeries.loc[validSeries.index] = scaledScores.astype('Int64')
    
    return scoreSeries

def AddScoreColumn(df, valueColumn, scoreColumn=None, higherIsBetter=True, groupColumns=None, minScore=0, maxScore=100, neutralScore=50):
    'Adds a 0-100 score column to a dataframe using the rank order of a numeric column.'
    df          = df.copy()
    scoreColumn = scoreColumn or f'{valueColumn}Score'

    if groupColumns: df[scoreColumn] = df.groupby(groupColumns, dropna=False)[valueColumn].transform(lambda series: BuildScoreSeries(series, higherIsBetter=higherIsBetter, minScore=minScore, maxScore=maxScore, neutralScore=neutralScore))
    else: df[scoreColumn] = BuildScoreSeries(df[valueColumn], higherIsBetter=higherIsBetter, minScore=minScore, maxScore=maxScore, neutralScore=neutralScore)

    return df

# Filters
def IsMultiValueFilter(value):
    'Checks if the filter value is a multi-value filter.'
    return isinstance(value, (list, tuple, set))

def FilterDf(df, category, organization, year, donorType):
    'Filter df by category, organization, year, and donor type.'
    filteredDf = df.copy()    

    if category:
        if IsMultiValueFilter(category): filteredDf = filteredDf[filteredDf['Category'].isin(category)]
        else                          : filteredDf = filteredDf[filteredDf['Category'] == category]

    if organization:
        if IsMultiValueFilter(organization): filteredDf = filteredDf[filteredDf['Organization'].isin(organization)]
        else                               : filteredDf = filteredDf[filteredDf['Organization'] == organization]

    if year:
        if IsMultiValueFilter(year): filteredDf = filteredDf[filteredDf['Year'].isin(year)]
        else                       : filteredDf = filteredDf[filteredDf['Year'] == year]

    if donorType:
        donorTypeColumn = None
        for column in ['Specific', 'DonorType', 'ContractType']:
            if column in filteredDf.columns:
                donorTypeColumn = column
                break

        if donorTypeColumn:
            if IsMultiValueFilter(donorType): filteredDf = filteredDf[filteredDf[donorTypeColumn].isin(donorType)]
            else                            : filteredDf = filteredDf[filteredDf[donorTypeColumn] == donorType]

    return filteredDf.reset_index(drop=True)

# Registry
def BuildRegistry(df, category, organization):
    'Builds a df for the registry.'
    df                    = df.copy()
    df                    = FilterDf(df, category=category, organization=organization, year=None, donorType=None)
    df['TotalAssociates'] = df['AssociatesPeople'].fillna(0) + df['AssociatesOrganizations'].fillna(0)
    df                    = df[['Organization', 'ShortName', 'Category', 'FoundingYear', 'TotalAssociates', 'Address', 'Email', 'Website']].drop_duplicates()
    df['FoundingYear']    = pd.to_numeric(df['FoundingYear'], errors='coerce').astype('Int64')
    df                    = df.rename(columns={'ShortName': 'Short Name'})
    return df.reset_index(drop=True).sort_values(by=['Organization', 'Category'], ascending=True).reset_index(drop=True)

# Associates
def BuildAssociates(df, parameter, category, organization):
    'Builds a df for associates by category or organization.'
    df = df.copy()
    df = FilterDf(df, category=category, organization=organization, year=None, donorType=None)
    if parameter == 'Category': df = df.groupby('Category')[['AssociatesPeople', 'AssociatesOrganizations']].sum().reset_index()
    elif parameter == 'Organization': df = (df.groupby('ShortName')[['AssociatesPeople', 'AssociatesOrganizations']].sum().reset_index().rename(columns={'ShortName': 'Organization'}))

    return df.sort_values(by=parameter, ascending=True).reset_index(drop=True)

# Boxes
def BuildBoxes(df, category, organization, year, donorType):
    'Builds a df with metrics and deltas.'
    df = df.copy()
    df = FilterDf(df.copy(), category, organization=None, year=None, donorType=None)
    
    keyColumns  = ['Category', 'Organization', 'Year']
    donorColumn = 'Specific'
    donorTypes  = df[df['Domain'] == 'Fondi'][[donorColumn]].dropna(subset=[donorColumn]).drop_duplicates().rename(columns={donorColumn: 'DonorType'}).reset_index(drop=True)
    baseKeys    = df[keyColumns].drop_duplicates().reset_index(drop=True)
    dfBase      = baseKeys.merge(donorTypes, how='cross')

    projectsIndirect = (df[(df['Domain'] == 'Progetti') & (df['Specific'] == 'Indiretti')].groupby(keyColumns)['Value'].sum().reset_index().rename(columns={'Value': 'ProjectsIndirect'}))
    projectsDirect   = (df[(df['Domain'] == 'Progetti') & (df['Specific'] == 'Diretti')].groupby(keyColumns)['Value'].sum().reset_index().rename(columns={'Value': 'ProjectsDirect'}))
    citizens         = (df[df['Domain'] == 'Beneficiari'].groupby(keyColumns)['Value'].sum().reset_index().rename(columns={'Value': 'Citizens'}))
    expenses         = (df[df['Specific'] == 'Uscite'].groupby(keyColumns)['Value'].sum().reset_index().rename(columns={'Value': 'Expenses'}))
    fundings         = (df[df['Domain'] == 'Fondi'].groupby(['Category', 'Organization', donorColumn, 'Year'])['Value'].sum().reset_index().rename(columns={donorColumn: 'DonorType', 'Value': 'Fundings'}))
    fundings['Year'] = fundings['Year'] + 1

    dfBoxes = (dfBase
        .merge(projectsIndirect, on=keyColumns, how='left')
        .merge(projectsDirect, on=keyColumns, how='left')
        .merge(citizens, on=keyColumns, how='left')
        .merge(expenses, on=keyColumns, how='left')
        .merge(fundings, on=['Category', 'Organization', 'DonorType', 'Year'], how='left'))

    hasFundings            = dfBoxes['Fundings'].notna() & (dfBoxes['Fundings'] != 0)
    dfBoxes['MetricOne']   = (100 * dfBoxes['ProjectsIndirect'] / dfBoxes['Fundings']).where(hasFundings, None)
    dfBoxes['MetricTwo']   = (100 * dfBoxes['ProjectsDirect'] / dfBoxes['Fundings']).where(hasFundings, None)
    dfBoxes['MetricThree'] = (dfBoxes['Citizens'] / (100 * dfBoxes['Fundings'])).where(hasFundings, None)
    dfBoxes['MetricFour']  = (dfBoxes['Expenses'] / (100 * dfBoxes['Fundings'])).where(hasFundings, None)

    metricColumns          = ['MetricOne', 'MetricTwo', 'MetricThree', 'MetricFour']

    for metric in metricColumns:
        dfBoxes = AddDeltaPreviousYear(dfBoxes, metric, ['Category', 'Organization', 'DonorType'], deltaColumn=f'{metric}DeltaPreviousYear')
        dfBoxes = AddDeltaAgainstGroupMean(dfBoxes, metric, ['Category', 'Year', 'DonorType'], deltaColumn=f'{metric}DeltaCategory', meanColumn=f'{metric}CategoryMean')

    if donorType:
        if IsMultiValueFilter(donorType): dfBoxes = dfBoxes[dfBoxes['DonorType'].isin(donorType)]
        else                            : dfBoxes = dfBoxes[dfBoxes['DonorType'] == donorType]

    if organization:
        if IsMultiValueFilter(organization): dfBoxes = dfBoxes[dfBoxes['Organization'].isin(organization)]
        else                               : dfBoxes = dfBoxes[dfBoxes['Organization'] == organization]

    if year:
        if IsMultiValueFilter(year): dfBoxes = dfBoxes[dfBoxes['Year'].isin(year)]
        else                       : dfBoxes = dfBoxes[dfBoxes['Year'] == year]

    finalColumns = ['Category', 'Organization', 'DonorType', 'Year',
                    'MetricOne', 'MetricTwo', 'MetricThree', 'MetricFour',
                    'MetricOneDeltaPreviousYear', 'MetricOneDeltaCategory', 'MetricTwoDeltaPreviousYear', 'MetricTwoDeltaCategory', 'MetricThreeDeltaPreviousYear', 'MetricThreeDeltaCategory', 'MetricFourDeltaPreviousYear', 'MetricFourDeltaCategory']

    return dfBoxes[finalColumns].sort_values(by=['Category', 'Organization', 'DonorType', 'Year'], ascending=True).reset_index(drop=True)

# Projects By Country
def BuildProjectsMap(df, category, organization, year):
    'Builds a df for projects by country with deltas.'
    df = df.copy()
    df = df.dropna(subset=['Country']).assign(Projects=lambda data: data['Projects'].fillna(0)).groupby(['Category', 'Organization', 'Country', 'Year'], as_index=False)['Projects'].sum()

    df = AddDeltaPreviousYear(df, 'Projects', ['Category', 'Organization', 'Country'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Projects', ['Category', 'Country', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Country', 'Year', 'Projects', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Workers
def BuildWorkers(df, category, organization, year):
    'Builds a df for workers by contract type with deltas.'
    df = (df[df['Domain'] == 'Lavoratori'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'ShortName', 'Specific', 'Year'], as_index=False)['Value'].sum().rename(columns={'Specific': 'ContractType', 'Value': 'Workers'}))

    df = AddDeltaPreviousYear(df, 'Workers', ['Category', 'Organization', 'ContractType'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Workers', ['Category', 'ContractType', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'ShortName', 'ContractType', 'Year', 'Workers', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Retributions
def BuildRetributions(df, category, organization, year):
    'Builds a df for retributions by level with deltas.'
    df = (df[df['Domain'] == 'Retribuzioni'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Specific', 'Year'], as_index=False)['Value'].mean().rename(columns={'Specific': 'Level', 'Value': 'Retributions'}))

    df = AddDeltaPreviousYear(df, 'Retributions', ['Category', 'Organization', 'Level'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Retributions', ['Category', 'Level', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Level', 'Year', 'Retributions', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Beneficiaries
def BuildBeneficiaries(df, category, organization, year):
    'Builds a df for beneficiaries with deltas.'
    df = (df[df['Domain'] == 'Beneficiari'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Beneficiaries'}))

    df = AddDeltaPreviousYear(df, 'Beneficiaries', ['Category', 'Organization'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Beneficiaries', ['Category', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Year', 'Beneficiaries', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Projects
def BuildProjects(df, category, organization, year):
    'Builds a df for projects by category or organization with deltas.'
    df = (df[df['Domain'] == 'Progetti'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Projects'}))

    df = AddDeltaPreviousYear(df, 'Projects', ['Category', 'Organization'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Projects', ['Category', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Year', 'Projects', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Scatterplot People Projects
def AssignCluster(row, medianProjects, medianBeneficiaries):
    'Assigns an impact cluster based on beneficiaries and projects compared to medians.'
    beneficiaries = row['Beneficiaries']
    projects = row['Projects']
    if projects >= medianProjects and beneficiaries >= medianBeneficiaries: return 'High Impact'
    elif projects >= medianProjects and beneficiaries < medianBeneficiaries: return 'Efficient Reach'
    elif projects < medianProjects and beneficiaries < medianBeneficiaries: return 'Under Development'
    else:  return 'Scale to Unlock'

def AssignClusterWithRowMedians(row):
    'Assigns an impact cluster using median values stored in row columns.'
    return AssignCluster(row, row['MedianProjects'], row['MedianBeneficiaries'])

def BuildThresholdCandidates(series):
    'Builds candidate split thresholds from series median and unique-value midpoints.'
    numericSeries = pd.to_numeric(series, errors='coerce').dropna()
    uniqueValues  = sorted(numericSeries.unique().tolist())
    candidates    = [float(numericSeries.median())]

    if len(uniqueValues) > 1:
        midpoints = [(uniqueValues[index] + uniqueValues[index + 1]) / 2.0 for index in range(len(uniqueValues) - 1)]
        candidates.extend(midpoints)

    return list(dict.fromkeys([float(candidate) for candidate in candidates]))

def FindBestQuadrantSplit(df, projectsColumn='Projects', beneficiariesColumn='Beneficiaries'):
    'Finds split thresholds that maximize non-empty quadrants; falls back to medians.'
    projectsSeries = pd.to_numeric(df[projectsColumn], errors='coerce').fillna(0)
    peopleSeries   = pd.to_numeric(df[beneficiariesColumn], errors='coerce').fillna(0)

    defaultProjectsSplit = float(projectsSeries.median())
    defaultPeopleSplit   = float(peopleSeries.median())
    projectCandidates    = BuildThresholdCandidates(projectsSeries)
    peopleCandidates     = BuildThresholdCandidates(peopleSeries)

    bestScore = None
    bestSplit = (defaultProjectsSplit, defaultPeopleSplit)

    for projectSplit in projectCandidates:
        for peopleSplit in peopleCandidates:
            countHighImpact       = ((projectsSeries >= projectSplit) & (peopleSeries >= peopleSplit)).sum()
            countEfficientReach   = ((projectsSeries >= projectSplit) & (peopleSeries < peopleSplit)).sum()
            countUnderDevelopment = ((projectsSeries < projectSplit) & (peopleSeries < peopleSplit)).sum()
            countScaleToUnlock    = ((projectsSeries < projectSplit) & (peopleSeries >= peopleSplit)).sum()

            counts              = [int(countHighImpact), int(countEfficientReach), int(countUnderDevelopment), int(countScaleToUnlock)]
            nonEmptyQuadrants   = sum(1 for count in counts if count > 0)
            minNonEmptyCount    = min([count for count in counts if count > 0], default=0)
            splitDistance       = abs(projectSplit - defaultProjectsSplit) + abs(peopleSplit - defaultPeopleSplit)
            currentScore        = (nonEmptyQuadrants, minNonEmptyCount, -splitDistance)

            if bestScore is None or currentScore > bestScore:
                bestScore = currentScore
                bestSplit = (float(projectSplit), float(peopleSplit))

    return bestSplit

def BuildPeopleProjects(df, category, organization, year):
    'Builds a df for beneficiaries vs projects impact analysis with cluster assignment.'
    beneficiaries = (df[df['Domain'] == 'Beneficiari'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Beneficiaries'}))
    projects      = (df[df['Domain'] == 'Progetti'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Projects'}))

    df = beneficiaries.merge(projects, on=['Category', 'Organization', 'Year'], how='outer').fillna(0)
    df = FilterDf(df, category=category, organization=organization, year=year, donorType=None)

    medianBeneficiaries               = float(pd.to_numeric(df['Beneficiaries'], errors='coerce').fillna(0).median())
    medianProjects                    = float(pd.to_numeric(df['Projects'], errors='coerce').fillna(0).median())
    splitProjects, splitBeneficiaries = FindBestQuadrantSplit(df, 'Projects', 'Beneficiaries')

    df['Cluster']             = df.apply(AssignCluster, axis=1, args=(splitProjects, splitBeneficiaries))
    df['MedianBeneficiaries'] = medianBeneficiaries
    df['MedianProjects']      = medianProjects
    df['SplitBeneficiaries']  = splitBeneficiaries
    df['SplitProjects']       = splitProjects

    finalColumns = ['Category', 'Organization', 'Year', 'Beneficiaries', 'Projects', 'MedianBeneficiaries', 'MedianProjects', 'SplitBeneficiaries', 'SplitProjects', 'Cluster']

    return df[finalColumns].reset_index(drop=True)

def BuildPeopleProjectsCategory(df, category, organization, year):
    'Builds a df for beneficiaries vs projects impact analysis at category level with globally consistent split lines and clusters.'
    beneficiaries   = df[df['Domain'] == 'Beneficiari'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Beneficiaries'})
    projects        = df[df['Domain'] == 'Progetti'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Projects'})
    df              = beneficiaries.merge(projects, on=['Category', 'Organization', 'Year'], how='outer').fillna(0)
    dfCategoryLevel = df.groupby(['Category', 'Year'], as_index=False).agg({'Beneficiaries': 'sum', 'Projects': 'sum'})

    dfCategoryLevel = FilterDf(dfCategoryLevel, category=category, organization=None, year=year, donorType=None)

    medianBeneficiaries               = float(pd.to_numeric(dfCategoryLevel['Beneficiaries'], errors='coerce').fillna(0).median())
    medianProjects                    = float(pd.to_numeric(dfCategoryLevel['Projects'], errors='coerce').fillna(0).median())
    splitProjects, splitBeneficiaries = FindBestQuadrantSplit(dfCategoryLevel, 'Projects', 'Beneficiaries')

    dfCategoryLevel['MedianBeneficiaries'] = medianBeneficiaries
    dfCategoryLevel['MedianProjects']      = medianProjects
    dfCategoryLevel['SplitBeneficiaries']  = splitBeneficiaries
    dfCategoryLevel['SplitProjects']       = splitProjects
    dfCategoryLevel['Cluster']             = dfCategoryLevel.apply(AssignCluster, axis=1, args=(splitProjects, splitBeneficiaries))

    finalColumns = ['Category', 'Year', 'Beneficiaries', 'Projects', 'MedianBeneficiaries', 'MedianProjects', 'SplitBeneficiaries', 'SplitProjects', 'Cluster']

    return dfCategoryLevel[finalColumns].reset_index(drop=True)

# Revenues
def BuildRevenues(df, category, organization, year):
    'Builds a df for revenues by category or organization with deltas.'
    df = (df[(df['Domain'] == 'Bilancio') & (df['Specific'] == 'Entrate')].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Revenues'}))

    df = AddDeltaPreviousYear(df, 'Revenues', ['Category', 'Organization'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Revenues', ['Category', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Year', 'Revenues', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Expenses
def BuildExpenses(df, category, organization, year):
    'Builds a df for expenses by category or organization with deltas.'
    dfExpenses     = (df[(df['Domain'] == 'Bilancio') & (df['Specific'] == 'Uscite')].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Expenses'}))
    dfExpenseTypes = (df[df['Domain'] == 'Oneri'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Specific', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Share', 'Specific': 'ExpenseType'}))
    df             = dfExpenseTypes.merge(dfExpenses, on=['Category', 'Organization', 'Year'], how='left')
    df['Expenses'] = df['Expenses'] * (df['Share'] / 100.0)

    df = AddDeltaPreviousYear(df, 'Expenses', ['Category', 'Organization', 'ExpenseType'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Expenses', ['Category', 'ExpenseType', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'ExpenseType', 'Year', 'Expenses', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Donors
def BuildDonors(df, category, organization, year):
    'Builds a df for donors by category or organization with deltas.'
    df = (df[df['Domain'] == 'Donatori'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Donors'}))

    df = AddDeltaPreviousYear(df, 'Donors', ['Category', 'Organization'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Donors', ['Category', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=None)
    finalColumns = ['Category', 'Organization', 'Year', 'Donors', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Donations
def BuildDonations(df, category, organization, year, donorType):
    'Builds a df for donations by category or organization with deltas.'
    df = FilterDf(df.copy(), category=category, organization=organization, year=year, donorType=donorType)
    df = (df[df['Domain'] == 'Fondi'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Specific', 'Year'], as_index=False)['Value'].sum().rename(columns={'Specific': 'DonorType', 'Value': 'Donations'}))

    df = AddDeltaPreviousYear(df, 'Donations', ['Category', 'Organization', 'DonorType'], deltaColumn='DeltaPreviousYear')
    df = AddDeltaAgainstGroupMean(df, 'Donations', ['Category', 'DonorType', 'Year'], deltaColumn='DeltaCategory', meanColumn='CategoryMean')

    df           = FilterDf(df, category=category, organization=organization, year=year, donorType=donorType)
    finalColumns = ['Category', 'Organization', 'DonorType', 'Year', 'Donations', 'DeltaPreviousYear', 'DeltaCategory']

    return df[finalColumns].reset_index(drop=True)

# Sankey Funding Flow
def BuildSankey(df, category, organization, year):
    'Builds a df for sankey diagram with funding flow (Fundings → Revenues → Expenses breakdown).'
    fundings        = df[df['Domain'] == 'Fondi'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Fundings'})
    revenues        = df[(df['Domain'] == 'Bilancio') & (df['Specific'] == 'Entrate')].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Revenues'})
    dfExpenses      = df[(df['Domain'] == 'Bilancio') & (df['Specific'] == 'Uscite')].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'TotalExpenses'})
    dfExpenseShares = df[df['Domain'] == 'Oneri'].assign(Value=lambda data: data['Value'].fillna(0)).groupby(['Category', 'Organization', 'Specific', 'Year'], as_index=False)['Value'].sum().rename(columns={'Value': 'Share', 'Specific': 'ExpenseType'})
    
    dfExpensesDetails                  = dfExpenseShares.merge(dfExpenses, on=['Category', 'Organization', 'Year'], how='left')
    dfExpensesDetails['ExpenseAmount'] = dfExpensesDetails['TotalExpenses'] * (dfExpensesDetails['Share'] / 100.0)
    
    dfExpensesPivot = dfExpensesDetails.pivot_table(index=['Category', 'Organization', 'Year'], columns='ExpenseType', values='ExpenseAmount', aggfunc='sum').reset_index()
    dfExpensesPivot = dfExpensesPivot.fillna(0)
    
    for col in dfExpensesPivot.columns:
        if col not in ['Category', 'Organization', 'Year']: dfExpensesPivot = dfExpensesPivot.rename(columns={col: f'Expense{col}'})
    
    result          = fundings.merge(revenues, on=['Category', 'Organization', 'Year'], how='outer')
    dfExpensesPivot = dfExpensesPivot.rename(columns={'ExpenseMissione': 'ExpenseProjects', 'ExpenseStruttura': 'ExpenseStructure', 'ExpenseRaccolta Fondi': 'ExpenseFundings'})
    result          = result.merge(dfExpensesPivot, on=['Category', 'Organization', 'Year'], how='outer').fillna(0)
    result          = FilterDf(result, category=category, organization=organization, year=year, donorType=None)
    result          = result[(result['Fundings'] != 0) & (result['Revenues'] != 0) & (result['ExpenseProjects'] != 0)]
    finalColumns    = ['Category', 'Organization', 'Year', 'Fundings', 'Revenues', 'ExpenseProjects', 'ExpenseStructure', 'ExpenseFundings']
    
    return result[finalColumns].reset_index(drop=True)

# Wrappers
@st.cache_data(ttl=3600, show_spinner=False)
def BuildOrganizationDfs(registry, geography, metrics, category, organization, year, donorType):
    'Builds a dict of dfs for a specific organization with all metrics and deltas.'
    registryDf       = BuildRegistry(registry, category, organization)
    associatesDf     = BuildAssociates(registry, 'Organization', category, organization)
    boxesDf          = BuildBoxes(metrics, category, organization, year, donorType)
    projectsMapDf    = BuildProjectsMap(geography, category, organization, year)
    workersDf        = BuildWorkers(metrics, category, organization, year)
    retributionsDf   = BuildRetributions(metrics, category, organization, year)
    beneficiariesDf  = BuildBeneficiaries(metrics, category, organization, year)
    projectsDf       = BuildProjects(metrics, category, organization, year)
    peopleProjectsDf = BuildPeopleProjects(metrics, category, organization, year)
    revenuesDf       = BuildRevenues(metrics, category, organization, year)
    expensesDf       = BuildExpenses(metrics, category, organization, year)
    donorsDf         = BuildDonors(metrics, category, organization, year)
    donationsDf      = BuildDonations(metrics, category, organization, year, donorType)
    sankeyDf         = BuildSankey(metrics, category, organization, year)
    return {'Registry': registryDf, 'Associates': associatesDf, 'Boxes': boxesDf, 'ProjectsMap': projectsMapDf, 'Workers': workersDf, 'Retributions': retributionsDf, 'Beneficiaries': beneficiariesDf, 'Projects': projectsDf, 'PeopleProjects': peopleProjectsDf, 'Revenues': revenuesDf, 'Expenses': expensesDf, 'Donors': donorsDf, 'Donations': donationsDf, 'Sankey': sankeyDf}

@st.cache_data(ttl=3600, show_spinner=False)
def BuildCategoryDfs(registry, geography, metrics, category, organization, year, donorType):
    'Builds a dict of dfs for a specific category with all metrics and deltas.'
    associatesDf     = BuildAssociates(registry, 'Category', category, organization)
    boxesDf          = BuildBoxes(metrics, category, organization, year, donorType)
    projectsMapDf    = BuildProjectsMap(geography, category, organization, year)
    projectsMapDf    = projectsMapDf.groupby(['Category', 'Country', 'Year'], as_index=False).agg({'Projects': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    workersDf        = BuildWorkers(metrics, category, organization, year)
    workersDf        = workersDf.groupby(['Category', 'ContractType', 'Year'], as_index=False).agg({'Workers': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    retributionsDf   = BuildRetributions(metrics, category, organization, year)
    retributionsDf   = retributionsDf.groupby(['Category', 'Level', 'Year'], as_index=False).agg({'Retributions': 'mean', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    beneficiariesDf  = BuildBeneficiaries(metrics, category, organization, year)
    beneficiariesDf  = beneficiariesDf.groupby(['Category', 'Year'], as_index=False).agg({'Beneficiaries': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    projectsDf       = BuildProjects(metrics, category, organization, year)
    projectsDf       = projectsDf.groupby(['Category', 'Year'], as_index=False).agg({'Projects': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    peopleProjectsDf = BuildPeopleProjectsCategory(metrics, category, organization, year)
    revenuesDf       = BuildRevenues(metrics, category, organization, year)
    revenuesDf       = revenuesDf.groupby(['Category', 'Year'], as_index=False).agg({'Revenues': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    expensesDf       = BuildExpenses(metrics, category, organization, year)
    expensesDf       = expensesDf.groupby(['Category', 'ExpenseType', 'Year'], as_index=False).agg({'Expenses': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    donorsDf         = BuildDonors(metrics, category, organization, year)
    donorsDf         = donorsDf.groupby(['Category', 'Year'], as_index=False).agg({'Donors': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    donationsDf      = BuildDonations(metrics, category, organization, year, donorType)
    donationsDf      = donationsDf.groupby(['Category', 'DonorType', 'Year'], as_index=False).agg({'Donations': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
    sankeyDf         = BuildSankey(metrics, category, organization, year)
    sankeyDf         = sankeyDf.groupby(['Category', 'Year'], as_index=False).agg({'Fundings': 'sum', 'Revenues': 'sum', 'ExpenseProjects': 'sum', 'ExpenseStructure': 'sum', 'ExpenseFundings': 'sum'})
    return {'Associates': associatesDf, 'Boxes': boxesDf, 'ProjectsMap': projectsMapDf, 'Workers': workersDf, 'Retributions': retributionsDf, 'Beneficiaries': beneficiariesDf, 'Projects': projectsDf, 'PeopleProjects': peopleProjectsDf, 'Revenues': revenuesDf, 'Expenses': expensesDf, 'Donors': donorsDf, 'Donations': donationsDf, 'Sankey': sankeyDf}

@st.cache_data(ttl=3600, show_spinner=False)
def BuildLLMDf(organizationDictionary):
    'Builds a compact scored summary dataframe for the LLM with dimension scores, average score and top-7 ranking.'
    registryDf       = organizationDictionary.get('Registry', pd.DataFrame())
    projectsMapDf    = organizationDictionary.get('ProjectsMap', pd.DataFrame())
    workersDf        = organizationDictionary.get('Workers', pd.DataFrame())
    beneficiariesDf  = organizationDictionary.get('Beneficiaries', pd.DataFrame())
    projectsDf       = organizationDictionary.get('Projects', pd.DataFrame())
    peopleProjectsDf = organizationDictionary.get('PeopleProjects', pd.DataFrame())
    revenuesDf       = organizationDictionary.get('Revenues', pd.DataFrame())
    expensesDf       = organizationDictionary.get('Expenses', pd.DataFrame())
    donorsDf         = organizationDictionary.get('Donors', pd.DataFrame())
    donationsDf      = organizationDictionary.get('Donations', pd.DataFrame())
    sankeyDf         = organizationDictionary.get('Sankey', pd.DataFrame())

    organizationFrames = [df[['Organization']] for df in [projectsMapDf, workersDf, beneficiariesDf, projectsDf, peopleProjectsDf, revenuesDf, expensesDf, donorsDf, donationsDf, sankeyDf] if not df.empty and 'Organization' in df.columns]
    finalColumns       = ['Organization', 'Category', 'AverageScore', 'Impact', 'Maturity', 'Efficiency', 'Globalization', 'Dimension', 'Trust', 'Growth']
    summaryDf          = pd.concat(organizationFrames, ignore_index=True).drop_duplicates().reset_index(drop=True)

    if not registryDf.empty and {'Organization', 'Category'}.issubset(registryDf.columns):
        registryCols    = [c for c in ['Organization', 'Category', 'FoundingYear', 'TotalAssociates'] if c in registryDf.columns]
        registrySummary = registryDf[registryCols].drop_duplicates(subset=['Organization'])
        summaryDf       = summaryDf.merge(registrySummary, on='Organization', how='left')

    if not peopleProjectsDf.empty and {'Organization', 'Cluster'}.issubset(peopleProjectsDf.columns):
        clusterMap               = {'High Impact': 100, 'Efficient Reach': 75, 'Scale to Unlock': 50, 'Under Development': 25}
        clusterSummary           = peopleProjectsDf[['Organization', 'Cluster']].drop_duplicates(subset=['Organization']).copy()
        clusterSummary['Impact'] = clusterSummary['Cluster'].map(clusterMap).astype('Int64')
        summaryDf                = summaryDf.merge(clusterSummary[['Organization', 'Impact']], on='Organization', how='left')

    if not sankeyDf.empty and {'Organization', 'ExpenseProjects', 'Revenues'}.issubset(sankeyDf.columns):
        sankeySummary                            = sankeyDf.groupby('Organization', as_index=False).agg({'ExpenseProjects': 'sum', 'Revenues': 'sum'})
        validRevenue                             = sankeySummary['Revenues'].notna() & (sankeySummary['Revenues'] != 0)
        sankeySummary['ExpenseProjectsRevenues'] = (sankeySummary['ExpenseProjects'] / sankeySummary['Revenues']).where(validRevenue, None)
        sankeySummary                            = AddScoreColumn(sankeySummary, 'ExpenseProjectsRevenues', scoreColumn='Efficiency', higherIsBetter=True)
        summaryDf                                = summaryDf.merge(sankeySummary[['Organization', 'Efficiency']], on='Organization', how='left')

    if not projectsMapDf.empty and {'Organization', 'Country'}.issubset(projectsMapDf.columns):
        countriesSummary = projectsMapDf.groupby('Organization', as_index=False)['Country'].nunique().rename(columns={'Country': 'Countries'})
        countriesSummary = AddScoreColumn(countriesSummary, 'Countries', scoreColumn='Globalization', higherIsBetter=True)
        summaryDf        = summaryDf.merge(countriesSummary[['Organization', 'Globalization']], on='Organization', how='left')

    if not workersDf.empty and {'Organization', 'Workers', 'DeltaPreviousYear', 'DeltaCategory'}.issubset(workersDf.columns):
        workersSummary              = workersDf.groupby('Organization', as_index=False).agg({'Workers': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
        workersSummary              = AddScoreColumn(workersSummary, 'Workers', scoreColumn='_WVal', higherIsBetter=True)
        workersSummary              = AddScoreColumn(workersSummary, 'DeltaPreviousYear', scoreColumn='_WDPY', higherIsBetter=True)
        workersSummary              = AddScoreColumn(workersSummary, 'DeltaCategory', scoreColumn='_WDC', higherIsBetter=True)
        workersSummary['Dimension'] = workersSummary[['_WVal', '_WDPY', '_WDC']].astype('Float64').mean(axis=1, skipna=True).round().astype('Int64')
        summaryDf                   = summaryDf.merge(workersSummary[['Organization', 'Dimension']], on='Organization', how='left')

    trustParts = {}
    if not donationsDf.empty and {'Organization', 'Donations', 'DeltaPreviousYear', 'DeltaCategory'}.issubset(donationsDf.columns):
        donationsSummary           = donationsDf.groupby('Organization', as_index=False).agg({'Donations': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
        donationsSummary           = AddScoreColumn(donationsSummary, 'Donations', scoreColumn='_DonVal', higherIsBetter=True)
        donationsSummary           = AddScoreColumn(donationsSummary, 'DeltaPreviousYear', scoreColumn='_DonDPY', higherIsBetter=True)
        donationsSummary           = AddScoreColumn(donationsSummary, 'DeltaCategory', scoreColumn='_DonDC', higherIsBetter=True)
        donationsSummary['_DonS']  = donationsSummary[['_DonVal', '_DonDPY', '_DonDC']].astype('Float64').mean(axis=1, skipna=True)
        trustParts['_DonS']        = donationsSummary[['Organization', '_DonS']]

    if not donorsDf.empty and {'Organization', 'Donors', 'DeltaPreviousYear', 'DeltaCategory'}.issubset(donorsDf.columns):
        donorsSummary              = donorsDf.groupby('Organization', as_index=False).agg({'Donors': 'sum', 'DeltaPreviousYear': 'mean', 'DeltaCategory': 'mean'})
        donorsSummary              = AddScoreColumn(donorsSummary, 'Donors', scoreColumn='_DrsVal', higherIsBetter=True)
        donorsSummary              = AddScoreColumn(donorsSummary, 'DeltaPreviousYear', scoreColumn='_DrsDPY', higherIsBetter=True)
        donorsSummary              = AddScoreColumn(donorsSummary, 'DeltaCategory', scoreColumn='_DrsDC', higherIsBetter=True)
        donorsSummary['_DrsS']     = donorsSummary[['_DrsVal', '_DrsDPY', '_DrsDC']].astype('Float64').mean(axis=1, skipna=True)
        trustParts['_DrsS']        = donorsSummary[['Organization', '_DrsS']]

    if trustParts:
        trustDf = summaryDf[['Organization']]
        for col, part in trustParts.items(): trustDf = trustDf.merge(part, on='Organization', how='left')
        trustDf['Trust'] = trustDf[list(trustParts.keys())].astype('Float64').mean(axis=1, skipna=True).round().astype('Int64')
        summaryDf        = summaryDf.merge(trustDf[['Organization', 'Trust']], on='Organization', how='left')

    growthParts = {}
    for growthDf, growthCol in [(revenuesDf, '_RevDPY'), (expensesDf, '_ExpDPY'), (projectsDf, '_ProjDPY'), (beneficiariesDf, '_BenDPY')]:
        if not growthDf.empty and {'Organization', 'DeltaPreviousYear'}.issubset(growthDf.columns):
            part                   = growthDf.groupby('Organization', as_index=False)['DeltaPreviousYear'].mean()
            part                   = AddScoreColumn(part, 'DeltaPreviousYear', scoreColumn=growthCol, higherIsBetter=True)
            growthParts[growthCol] = part[['Organization', growthCol]]

    if growthParts:
        growthMergeDf = summaryDf[['Organization']]
        for col, part in growthParts.items(): growthMergeDf = growthMergeDf.merge(part, on='Organization', how='left')
        growthMergeDf['Growth']  = growthMergeDf[list(growthParts.keys())].astype('Float64').mean(axis=1, skipna=True).round().astype('Int64')
        summaryDf                = summaryDf.merge(growthMergeDf[['Organization', 'Growth']], on='Organization', how='left')

    maturityCols = []
    if 'FoundingYear' in summaryDf.columns:
        summaryDf = AddScoreColumn(summaryDf, 'FoundingYear', scoreColumn='_FYScore', higherIsBetter=False)
        maturityCols.append('_FYScore')
    if 'TotalAssociates' in summaryDf.columns:
        summaryDf = AddScoreColumn(summaryDf, 'TotalAssociates', scoreColumn='_TAScore', higherIsBetter=True)
        maturityCols.append('_TAScore')
    if 'Dimension' in summaryDf.columns: maturityCols.append('Dimension')
    if maturityCols: summaryDf['Maturity'] = summaryDf[maturityCols].astype('Float64').mean(axis=1, skipna=True).round().astype('Int64')

    dimensionColumns          = [c for c in ['Impact', 'Maturity', 'Efficiency', 'Globalization', 'Dimension', 'Trust', 'Growth'] if c in summaryDf.columns]
    summaryDf['AverageScore'] = summaryDf[dimensionColumns].astype('Float64').mean(axis=1, skipna=True).round().astype('Int64')

    existingFinalColumns = [c for c in finalColumns if c in summaryDf.columns]
    summaryDf            = (summaryDf[existingFinalColumns].drop_duplicates(subset=['Organization']).sort_values(by='AverageScore', ascending=False, na_position='last').head(7).reset_index(drop=True))

    return summaryDf