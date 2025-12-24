from typing import TypedDict, Dict, List, Literal, get_args

Area = str # For example, Finland, or USA_Utah. Names are Ada_Case
HexColor = str
AlphaHexColor = str

PageType = Literal["world", "europe", "europe-detailed", "asia", "americas", "americas-detailed", "africa", "africa-detailed", "usa", "usa-counties"] | str
SizeType = Literal["thinner", "thin", "medium", "thick", "thicker"]
Country = Literal["Austria","Belgium","Bulgaria","Croatia","Cyprus","Czechia","Denmark","Estonia","Finland","France","Germany","Greece","Hungary","Ireland","Italy","Latvia","Lithuania","Luxembourg","Malta","Netherlands","Poland","Portugal","Romania","Slovakia","Slovenia","Spain","Sweden","Martinique","Guadeloupe","French_Guiana","Réunion","Western_Sahara","Morocco","Algeria","Libya","Egypt","Sudan","Tunisia","Ethiopia","Eritrea","Somalia","Kenya","Djibouti","Tanzania","South_Sudan","Uganda","Rwanda","Burundi","Mozambique","Malawi","Zambia","Zimbabwe","Madagascar","Mauritius","Comoros","French_Southern_and_Antarctic_Lands","Mauritania","Mali","Niger","Benin","Togo","Ghana","Burkina_Faso","Nigeria","Cote_d_Ivoire","Liberia","Guinea","Sierra_Leone","Guinea_Bissau","Senegal","Cabo_Verde","Gambia","Chad","Central_African_Republic","DR_Congo","Angola","Gabon","Congo","Equatorial_Guinea","São_Tomé_and_Principe","Cameroon","Namibia","Botswana","South_Africa","Eswatini","Lesotho","Canada","United_States","Greenland","Mexico","Guatemala","Honduras","Belize","Haiti","Dominican_Republic","United_Kingdom","Norway","Iceland","Turkmenistan","Uzbekistan","Kyrgyzstan","Tajikistan","Kazakhstan","Azerbaijan","Armenia","Albania","Andorra","Bahrain","Belarus","Bosnia_and_Herzegovina","Georgia","Iran","Iraq","Israel","Jordan","Kuwait","Lebanon","Liechtenstein","North_Macedonia","Moldova","Monaco","Montenegro","Oman","Palestinian_Territories","Qatar","Saudi_Arabia","Serbia","Switzerland","Syria","Türkiye","Ukraine","United_Arab_Emirates","Yemen","Kosovo","Russia","Brunei","Cambodia","Indonesia","Laos","Malaysia","Myanmar","Philippines","Singapore","Thailand","Vietnam","China","Hong_Kong","Japan","South_Korea","Australia","Fiji","New_Caledonia","New_Zealand","Timor_Leste","Samoa","Solomon_Islands","Papua_New_Guinea","Vanuatu","Afghanistan","Bangladesh","Bhutan","India","Nepal","Pakistan","Sri_Lanka","American_Samoa","Mongolia","North_Korea","Taiwan","Colombia","El_Salvador","Nicaragua","Costa_Rica","Panama","Venezuela","Guyana","Suriname","Ecuador","Peru","Bolivia","Argentina","Chile","Brazil","Uruguay","Paraguay","Falkland_Islands","Jamaica","Cuba","Bahamas","Antigua_and_Barbuda","Puerto_Rico","Dominica","Barbados","Trinidad_and_Tobago","Grenada","Saint_Vincent_and_the_Grenadines"]
Territory = Literal["Yukon_CA","Prince_Edward_Island_CA","New_Brunswick_CA","Ontario_CA","British_Columbia_CA","Alberta_CA","Saskatchewan_CA","Manitoba_CA","Quebec_CA","Nunavut_CA","Newfoundland_and_Labrador_CA","Northwest_Territories_CA","Nova_Scotia_CA","USA_Alaska","USA_Wisconsin","USA_Montana","USA_Minnesota","USA_Washington","USA_Idaho","USA_North_Dakota","USA_Michigan","USA_Maine","USA_Ohio","USA_New_Hampshire","USA_New_York","USA_Vermont","USA_Pennsylvania","USA_Arizona","USA_California","USA_New_Mexico","USA_Texas","USA_Louisiana","USA_Mississippi","USA_Alabama","USA_Florida","USA_Georgia","USA_South_Carolina","USA_North_Carolina","USA_Washington_DC","USA_Virginia","USA_Maryland","USA_Delaware","USA_New_Jersey","USA_Connecticut","USA_Rhode_Island","USA_Massachusetts","USA_Oregon","USA_Hawaii","USA_Utah","USA_Wyoming","USA_Nevada","USA_Colorado","USA_South_Dakota","USA_Nebraska","USA_Kansas","USA_Oklahoma","USA_Iowa","USA_Missouri","USA_Illinois","USA_Kentucky","USA_Arkansas","USA_Tennessee","USA_West_Virginia","USA_Indiana","Scotland","Wales","England","Northern_Ireland"]

COUNTRIES = get_args(Country)
TERRITORIES = get_args(Territory)

GENERIC_COUNTRIES: List[Country | Territory] = list(COUNTRIES + TERRITORIES)
GenericCountry = Country | Territory | Area

ShowStatusType = Literal["show"] | str

class GroupType(TypedDict):
    label: str
    paths: List[Country | Territory | Area]

class SaveFile(TypedDict):
    groups: Dict[HexColor, GroupType]
    title: str
    hidden: List[Country | Territory | Area]
    background: HexColor
    borders: HexColor
    legendFont: str
    legendFontColor: AlphaHexColor
    legendBorderColor: AlphaHexColor
    legendBgColor: AlphaHexColor
    legendWidth: int
    legendBoxShape: Literal["square"] | str
    areBordersShown: bool
    defaultColor: HexColor  
    labelsColor: HexColor
    labelsFont: str
    strokeWidth: SizeType
    areLabelsShown: bool
    uncoloredScriptColor: HexColor
    zoomLevel: float
    zoomX: float
    zoomY: float
    v6: bool
    page: PageType
    usaStatesShown: bool
    canadaStatesShown: bool
    splitUK: bool
    legendPosition: Literal["bottom_left"] | str
    legendSize: SizeType
    legendTranslateX: float
    legendStatus: ShowStatusType
    scalingPatterns: bool
    legendRowsSameColor: bool
    legendColumnCount: int