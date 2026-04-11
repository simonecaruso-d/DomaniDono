# Environment Setting
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import re
import requests
import time
from urllib.parse import urljoin

# Static Inputs
BaseUrl         = 'https://www.open-cooperazione.it'
ListUrl         = BaseUrl + '/web/organizzazioni-lista.aspx?&pg={}'
Headers         = {'User-Agent': 'Mozilla/5.0 (compatible; OpenCooperazioneProjectsByCountryExport/1.0)'}

OutputFileName  = 'Open Cooperazione - Projects By Country.xlsx'
TargetsFilePath = 'Organizzazioni Target.txt' 

# Helpers
def NormalizeText(value):
    'Normalize text by collapsing whitespace and trimming.'
    return re.sub(r"\s+", " ", value or "").strip()

# Scraping
def GetSoup(session, url, headers=Headers, timeout=40):
    'Fetch the content of a URL and return a BeautifulSoup object.'
    response = session.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'html.parser')

def DiscoverProfileUrls(baseUrl=BaseUrl, listUrl=ListUrl, session=None, maxPages = 14):
    'Discover profile URLs from the listing pages.'
    profileUrls = []
    seen        = set()

    for page in range(1, maxPages + 1):
        soup = GetSoup(session, listUrl.format(page))
        for anchor in soup.select('a[href]'):
            href = anchor.get('href', '')
            if '/web/org-' not in href or '-scheda-' not in href.lower(): continue
            if not href.lower().endswith('.aspx')                       : continue
            url = urljoin(baseUrl, href)
            if url in seen: continue

            seen.add(url)
            profileUrls.append(url)

        time.sleep(0.2)

    return sorted(profileUrls)

# Extract Info
def ExtractYearLinks(profileSoup):
    'Extract year links from a profile page.'
    yearLinks = {}

    for anchor in profileSoup.select('a[href]'):
        text = NormalizeText(anchor.get_text(' ', strip=True))
        if not re.fullmatch(r"20\d{2}", text): continue
        href = anchor.get('href', '')
        if not href: continue
        yearLinks[int(text)] = urljoin(BaseUrl, href)

    return dict(sorted(yearLinks.items()))

def ExtractProjectsTableRows(yearSoup, organization, profileUrl, year, yearUrl):
    'Extract project table rows from a year page.'
    rowsOut = []

    for table in yearSoup.find_all('table'):
        rows = table.find_all('tr')
        if not rows: continue

        headers = [NormalizeText(c.get_text(' ', strip=True)).lower() for c in rows[0].find_all(['th', 'td'])]
        if len(headers) < 2: continue

        if 'nome' not in headers[0] or 'progetti' not in headers[1]: continue

        for row in rows[1:]:
            cells = [NormalizeText(c.get_text(' ', strip=True)) for c in row.find_all(['th', 'td'])]
            if len(cells) < 2: continue

            rawCountry = cells[0]
            rawProjects = cells[1]

            countryMatch = re.match(r"^(.*?)\s*-\s*([A-Z]{2})$", rawCountry)
            if countryMatch:
                countryName = countryMatch.group(1).strip()
                countryCode = countryMatch.group(2).strip()
            else:
                countryName = rawCountry
                countryCode = ''

            projects = None
            if re.fullmatch(r"\d+", rawProjects): projects = int(rawProjects)

            rowsOut.append({'Organization': organization, 'Year': year, 'Country': countryName, 'Projects': projects})

    return rowsOut

# Find Organizations
def LoadTargetNames(targetFilePath=TargetsFilePath):
    'Load target organization names from a file.'
    path                = Path(targetFilePath)
    if not path.exists(): return None
    names               = {NormalizeText(line) for line in path.read_text(encoding="utf-8").splitlines() if NormalizeText(line)}

    return names or None

# Main
def BuildExport(outputFileName=OutputFileName, targetsFilePath=TargetsFilePath):
    'Build the export file with project data.'
    session     = requests.Session()
    targetNames = LoadTargetNames(targetsFilePath)

    profileUrls = DiscoverProfileUrls(session=session)
    rows        = []

    for index, profileUrl in enumerate(profileUrls, start=1):
        try:
            profileSoup  = GetSoup(session, profileUrl)
            title        = profileSoup.select_one("h2")
            organization = NormalizeText(title.get_text(" ", strip=True)) if title else ""
            if targetNames is not None and organization not in targetNames: continue
            yearLinks    = ExtractYearLinks(profileSoup)
            if not yearLinks:
                print(f'[{index}/{len(profileUrls)}] Nessun anno: {organization}')
                continue

            for year, yearUrl in yearLinks.items():
                yearSoup = GetSoup(session, yearUrl)
                rows.extend(ExtractProjectsTableRows(yearSoup=yearSoup, organization=organization, profileUrl=profileUrl, year=year, yearUrl=yearUrl))
                time.sleep(0.2)

            print(f'[{index}/{len(profileUrls)}] OK: {organization} ({len(yearLinks)} anni)')

        except Exception as exc: print(f'[{index}/{len(profileUrls)}] ERRORE su {profileUrl}: {exc}')

    df = pd.DataFrame(rows)
    if not df.empty: df = df.sort_values(['Organization', 'Year', 'Country']).reset_index(drop=True)

    with pd.ExcelWriter(outputFileName, engine="openpyxl") as writer: df.to_excel(writer, sheet_name="ProjectsByCountry", index=False)

# Run
BuildExport()