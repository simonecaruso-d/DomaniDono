# Environment Setting
from pathlib import Path

# File Paths
ProjectRootPath = Path(__file__).resolve().parents[2]
ExcelPath       = ProjectRootPath / 'files' / 'data' / 'Open Cooperazione.xlsx'

# Column Mappings
RegistryColumnMap = {'Short Name': 'ShortName', 'Founding Year': 'FoundingYear', 'Associates (People)': 'AssociatesPeople', 'Associates (Organizations)': 'AssociatesOrganizations'}
MetricsColumnMap  = {'Measure Unit': 'MeasureUnit'}

# Column Types
RegistryTextColumns = ['Organization', 'ShortName', 'Category', 'Address', 'Email', 'Website', 'Facebook', 'X', 'Linkedin', 'Instagram']
RegistryNumericColumns = ['Founding Year', 'AssociatesPeople', 'AssociatesOrganizations']
MetricsTextColumns = ['Organization', 'Domain', 'Specific', 'MeasureUnit']
GeographicTextColumns = ['Organization', 'Country']