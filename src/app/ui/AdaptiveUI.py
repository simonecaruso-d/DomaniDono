# Functions
def Clamp(value, minimum, maximum):
    return max(minimum, min(value, maximum))

def RoundStep(value, step):
    if step <= 0: return int(value)
    return int(round(value / step) * step)

def MergeValues(defaultValues, customValues):
    merged = defaultValues.copy()
    if customValues: merged.update(customValues)
    return merged

def ExtractQueryValue(queryParams, key, defaultValue):
    if queryParams is None       : return defaultValue
    rawValue                     = queryParams.get(key, defaultValue)
    if isinstance(rawValue, list): rawValue = rawValue[0] if rawValue else defaultValue

    try: return int(float(rawValue))
    except Exception: return defaultValue

def FormatRem(value):
    return f'{value:.3f}'.rstrip('0').rstrip('.') + 'rem'

def FormatPx(value):
    return f'{int(round(value))}px'

def ScaleInt(value, scale, minimum=1):
    return max(minimum, int(round(value * scale)))

def ScaleCssPx(value, scale, minimum=1):
    return FormatPx(ScaleInt(value, scale, minimum=minimum))

def ScaleCssRem(value, scale):
    return FormatRem(value * scale)

def ScaleCssPairPx(firstValue, secondValue, scale):
    return f'{ScaleCssPx(firstValue, scale)} {ScaleCssPx(secondValue, scale)}'

def GetResponsiveScale(queryParams, responsiveValues):
    viewportWidth = ExtractQueryValue(queryParams, 'vw', responsiveValues['FallbackVw'])
    viewportWidth = RoundStep(viewportWidth, responsiveValues['StepPx'])
    computedScale = viewportWidth / responsiveValues['BaseWidth']
    return Clamp(computedScale, responsiveValues['MinScale'], responsiveValues['MaxScale']), viewportWidth

def ScalePx(value, scale, minimum=1):
    return ScaleInt(value, scale, minimum=minimum)

def BuildResponsiveValues(queryParams, baseValues, responsiveValues, minimumValues):
    scale, viewportWidth = GetResponsiveScale(queryParams=queryParams, responsiveValues=responsiveValues)
    viewportHeight = ExtractQueryValue(queryParams, 'vh', responsiveValues['ViewportHeight'])

    return {
        'ResponsiveScale'         : scale,
        'ResponsiveViewportWidth' : viewportWidth,
        'ResponsiveViewportHeight': viewportHeight,
        'FontSize75'              : ScaleCssRem(baseValues['BaseFontSize75'], scale),
        'FontSize80'              : ScaleCssRem(baseValues['BaseFontSize80'], scale),
        'FontSize85'              : ScaleCssRem(baseValues['BaseFontSize85'], scale),
        'FontSize90'              : ScaleCssRem(baseValues['BaseFontSize90'], scale),
        'FontSize95'              : ScaleCssRem(baseValues['BaseFontSize95'], scale),
        'FontSize100'             : ScaleCssRem(baseValues['BaseFontSize100'], scale),
        'FontSize105'             : ScaleCssRem(baseValues['BaseFontSize105'], scale),
        'FontSize110'             : ScaleCssRem(baseValues['BaseFontSize110'], scale),
        'FontSize115'             : ScaleCssRem(baseValues['BaseFontSize115'], scale),
        'FontSize120'             : ScaleCssRem(baseValues['BaseFontSize120'], scale),
        'FontSize125'             : ScaleCssRem(baseValues['BaseFontSize125'], scale),
        'LetterSpacing1'          : ScaleCssPx(baseValues['BaseLetterSpacing1'], scale, minimum=minimumValues['LetterSpacing']),
        'LetterSpacing2'          : ScaleCssPx(baseValues['BaseLetterSpacing2'], scale, minimum=minimumValues['LetterSpacing']),
        'LetterSpacing3'          : ScaleCssPx(baseValues['BaseLetterSpacing3'], scale, minimum=minimumValues['LetterSpacing']),
        'Spacing1'                : ScaleCssPx(baseValues['BaseSpacing1'], scale),
        'Spacing2'                : ScaleCssPx(baseValues['BaseSpacing2'], scale),
        'Spacing3'                : ScaleCssPx(baseValues['BaseSpacing3'], scale),
        'Spacing4'                : ScaleCssPx(baseValues['BaseSpacing4'], scale),
        'Spacing5'                : ScaleCssPx(baseValues['BaseSpacing5'], scale),
        'Spacing6'                : ScaleCssPx(baseValues['BaseSpacing6'], scale),
        'Border1'                 : ScaleCssPx(baseValues['BaseBorder1'], scale),
        'Border2'                 : ScaleCssPx(baseValues['BaseBorder2'], scale),
        'Border3'                 : ScaleCssPx(baseValues['BaseBorder3'], scale),
        'Border4'                 : ScaleCssPx(baseValues['BaseBorder4'], scale),
        'Border5'                 : ScaleCssPx(baseValues['BaseBorder5'], scale),
        'RadiusInput'             : ScaleInt(baseValues['BaseRadiusInput'], scale, minimum=minimumValues['RadiusInput']),
        'RadiusCard'              : ScaleInt(baseValues['BaseRadiusCard'], scale, minimum=minimumValues['RadiusCard']),
        'TitleTopPx'              : ScaleCssPx(baseValues['BaseTitleTopPx'], scale),
        'TitleLeftExpandedPx'     : ScaleCssPx(baseValues['BaseTitleLeftExpandedPx'], scale),
        'TitleLeftCollapsedPx'    : ScaleCssPx(baseValues['BaseTitleLeftCollapsedPx'], scale),
    }

def ApplyValues(target, values):
    if isinstance(target, dict):
        target.update(values)
        return

    for key, value in values.items(): setattr(target, key, value)

def ApplyResponsiveScale(queryParams, baseValues, responsiveValues, minimumValues, target=None):
    computedValues = BuildResponsiveValues(queryParams=queryParams, baseValues=baseValues, responsiveValues=responsiveValues, minimumValues=minimumValues)

    if target is not None: ApplyValues(target, computedValues)
    return computedValues