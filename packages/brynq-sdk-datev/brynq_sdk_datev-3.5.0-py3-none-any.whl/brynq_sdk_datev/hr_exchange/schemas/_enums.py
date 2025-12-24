# Enum definitions for HR Exchange models
# This file contains all enum classes used across the HR Exchange API

from enum import Enum


# Absence related enums
class ReasonForAbsence(Enum):
    AS__EK__EO__ER__EÜ__EZ__FR__GR__K__K6__KA__KE__KO__KP__MS__OS__PB__PE__PK__PO__PU__PZ__QA__QF__QO__QU__RA__SZ8__UA__UB__UE__UF__UU__VG__VL__WE__WK__ZD = 'AS, EK, EO, ER, EÜ, EZ, FR, GR, K, K6, KA, KE, KO, KP, MS, OS, PB, PE, PK, PO, PU, PZ, QA, QF, QO, QU, RA, SZ8, UA, UB, UE, UF, UU, VG, VL, WE, WK, ZD'


class ReasonForAbsence1(Enum):
    integer_32 = 32
    integer_47 = 47
    integer_300 = 300
    integer_29 = 29
    integer_64 = 64
    integer_51 = 51
    integer_301 = 301
    integer_61 = 61
    integer_33 = 33
    integer_103 = 103
    integer_41 = 41
    integer_260 = 260
    integer_28 = 28
    integer_25 = 25
    integer_16 = 16
    integer_45 = 45
    integer_302 = 302
    integer_14 = 14
    integer_200 = 200
    integer_11 = 11
    integer_24 = 24
    integer_210 = 210
    integer_15 = 15
    integer_303 = 303
    integer_305 = 305
    integer_304 = 304
    integer_306 = 306
    integer_31 = 31
    integer_106 = 106
    integer_23 = 23
    integer_105 = 105
    integer_43 = 43
    integer_19 = 19
    integer_21 = 21
    integer_44 = 44
    integer_42 = 42
    integer_63 = 63
    integer_81 = 81
    integer_62 = 62


# API and Error related enums
class Severity(Enum):
    ERROR = 'ERROR'
    WARNING = 'WARNING'
    INFORMATION = 'INFORMATION'


# Employment related enums
class HighestLevelOfProfessionalTraining(Enum):
    integer_1 = 1
    integer_2 = 2
    integer_3 = 3
    integer_4 = 4
    integer_5 = 5
    integer_6 = 6
    integer_9 = 9


class HighestLevelOfEducation(Enum):
    integer_1 = 1
    integer_2 = 2
    integer_3 = 3
    integer_4 = 4
    integer_9 = 9


class EmployeeType(Enum):
    field_101 = '101'
    field_102 = '102'
    field_103 = '103'
    field_104 = '104'
    field_105 = '105'
    field_106 = '106'
    field_107 = '107'
    field_108 = '108'
    field_109 = '109'
    field_110 = '110'
    field_111 = '111'
    field_112 = '112'
    field_113 = '113'
    field_114 = '114'
    field_116 = '116'
    field_117 = '117'
    field_118 = '118'
    field_119 = '119'
    field_120 = '120'
    field_121 = '121'
    field_122 = '122'
    field_123 = '123'
    field_124 = '124'
    field_127 = '127'
    field_190 = '190'
    field_900 = '900'


class ContractualStructure(Enum):
    field_1 = '1'
    field_2 = '2'
    field_3 = '3'
    field_4 = '4'


class EmploymentType(Enum):
    integer_1 = 1
    integer_2 = 2


# Personal data related enums
class Sex(Enum):
    D = 'D'
    M = 'M'
    W = 'W'
    X = 'X'


# Financial related enums
class PaymentMethod(Enum):
    field_1 = '1'
    field_4 = '4'
    field_5 = '5'


class FlatRateTax(Enum):
    integer_0 = 0
    integer_1 = 1
    integer_2 = 2


# Social Insurance related enums
class ContributionClassHealthInsurance(Enum):
    integer_0 = 0
    integer_1 = 1
    integer_3 = 3
    integer_4 = 4
    integer_5 = 5
    integer_6 = 6
    integer_9 = 9


class ContributionClassPensionInsurance(Enum):
    integer_0 = 0
    integer_1 = 1
    integer_3 = 3
    integer_5 = 5


# Tax related enums
class Denomination(Enum):
    ak = 'ak'
    ev = 'ev'
    fa = 'fa'
    fb = 'fb'
    fg = 'fg'
    fm = 'fm'
    fr = 'fr'
    fs = 'fs'
    ib = 'ib'
    ih = 'ih'
    il = 'il'
    is_ = 'is'
    iw = 'iw'
    jd = 'jd'
    jh = 'jh'
    lt = 'lt'
    rf = 'rf'
    rk = 'rk'


class SpousesDenomination(Enum):
    ak = 'ak'
    ev = 'ev'
    fa = 'fa'
    fb = 'fb'
    fg = 'fg'
    fm = 'fm'
    fr = 'fr'
    fs = 'fs'
    ib = 'ib'
    ih = 'ih'
    il = 'il'
    is_ = 'is'
    iw = 'iw'
    jd = 'jd'
    jh = 'jh'
    lt = 'lt'
    rf = 'rf'
    rk = 'rk'


# API Resource enums
class ResourceType(Enum):
    CLIENTS = 'CLIENTS'
    EMPLOYEES = 'EMPLOYEES'
    ACCOUNT = 'ACCOUNT'
    ACTIVITY = 'ACTIVITY'
    ADDRESS = 'ADDRESS'
    EMPLOYMENT_PERIODS = 'EMPLOYMENT_PERIODS'
    MONTH_RECORDS = 'MONTH_RECORDS'
    ABSENCES = 'ABSENCES'
    PERSONAL_DATA = 'PERSONAL_DATA'
    SOCIAL_INSURANCE = 'SOCIAL_INSURANCE'
    INDIVIDUAL_DATA = 'INDIVIDUAL_DATA'
    TAXATION = 'TAXATION'
    TAX_CARD = 'TAX_CARD'
    VACATION_ENTITLEMENT = 'VACATION_ENTITLEMENT'
    VOCATIONAL_TRAINING = 'VOCATIONAL_TRAINING'
    GROSS_PAYMENTS = 'GROSS_PAYMENTS'
    HOURLY_WAGES = 'HOURLY_WAGES'
    CALLBACK = 'CALLBACK'
    JOBS = 'JOBS'
    RESULT = 'RESULT'
    RESTHOOKS = 'RESTHOOKS'
    CLIENT_DATA = 'CLIENT_DATA'
    BUSINESS_UNIT = 'BUSINESS_UNIT'
    COST_CENTER = 'COST_CENTER'
    DEPARTMENT = 'DEPARTMENT'
    HEALTH_INSURER = 'HEALTH_INSURER'
    ERRORS = 'ERRORS'


class InnermostResourceType(Enum):
    CLIENTS = 'CLIENTS'
    EMPLOYEES = 'EMPLOYEES'
    ACCOUNT = 'ACCOUNT'
    ACTIVITY = 'ACTIVITY'
    ADDRESS = 'ADDRESS'
    EMPLOYMENT_PERIODS = 'EMPLOYMENT_PERIODS'
    MONTH_RECORDS = 'MONTH_RECORDS'
    ABSENCES = 'ABSENCES'
    PERSONAL_DATA = 'PERSONAL_DATA'
    SOCIAL_INSURANCE = 'SOCIAL_INSURANCE'
    INDIVIDUAL_DATA = 'INDIVIDUAL_DATA'
    TAXATION = 'TAXATION'
    TAX_CARD = 'TAX_CARD'
    VACATION_ENTITLEMENT = 'VACATION_ENTITLEMENT'
    VOCATIONAL_TRAINING = 'VOCATIONAL_TRAINING'
    GROSS_PAYMENTS = 'GROSS_PAYMENTS'
    HOURLY_WAGES = 'HOURLY_WAGES'
    CALLBACK = 'CALLBACK'
    JOBS = 'JOBS'
    RESULT = 'RESULT'
    RESTHOOKS = 'RESTHOOKS'
    CLIENT_DATA = 'CLIENT_DATA'
    BUSINESS_UNIT = 'BUSINESS_UNIT'
    COST_CENTER = 'COST_CENTER'
    DEPARTMENT = 'DEPARTMENT'
    HEALTH_INSURER = 'HEALTH_INSURER'
    ERRORS = 'ERRORS'


# Geographic and Location enums
class Country(Enum):
    A = 'A'
    AFG = 'AFG'
    AGO = 'AGO'
    AJ = 'AJ'
    AL = 'AL'
    AND = 'AND'
    ANG = 'ANG'
    ANT = 'ANT'
    AQ = 'AQ'
    AQU = 'AQU'
    ARM = 'ARM'
    AS = 'AS'
    ASE = 'ASE'
    AU = 'AU'
    AUS = 'AUS'
    AW = 'AW'
    AX = 'AX'
    B = 'B'
    BD = 'BD'
    BDS = 'BDS'
    BER = 'BER'
    BG = 'BG'
    BH = 'BH'
    BHT = 'BHT'
    BIH = 'BIH'
    BIO = 'BIO'
    BJ = 'BJ'
    BL = 'BL'
    BOL = 'BOL'
    BQ = 'BQ'
    BR = 'BR'
    BRN = 'BRN'
    BRU = 'BRU'
    BS = 'BS'
    BV = 'BV'
    BY = 'BY'
    C = 'C'
    CAM = 'CAM'
    CC = 'CC'
    CDN = 'CDN'
    CH = 'CH'
    CHD = 'CHD'
    CI = 'CI'
    CL = 'CL'
    CO = 'CO'
    COI = 'COI'
    CP = 'CP'
    CR = 'CR'
    CV = 'CV'
    CW = 'CW'
    CX = 'CX'
    CY = 'CY'
    CZ = 'CZ'
    D = 'D'
    DK = 'DK'
    DOM = 'DOM'
    DSC = 'DSC'
    DY = 'DY'
    DZ = 'DZ'
    E = 'E'
    EAK = 'EAK'
    EAT = 'EAT'
    EAU = 'EAU'
    EC = 'EC'
    EH = 'EH'
    ERI = 'ERI'
    ES = 'ES'
    EST = 'EST'
    ET = 'ET'
    ETH = 'ETH'
    F = 'F'
    FAL = 'FAL'
    FG = 'FG'
    FIN = 'FIN'
    FJI = 'FJI'
    FL = 'FL'
    FP = 'FP'
    FR = 'FR'
    GAB = 'GAB'
    GB = 'GB'
    GCA = 'GCA'
    GEO = 'GEO'
    GG = 'GG'
    GH = 'GH'
    GIB = 'GIB'
    GR = 'GR'
    GRO = 'GRO'
    GS = 'GS'
    GUA = 'GUA'
    GUB = 'GUB'
    GUM = 'GUM'
    GUY = 'GUY'
    H = 'H'
    HCA = 'HCA'
    HEL = 'HEL'
    HKG = 'HKG'
    HM = 'HM'
    HOK = 'HOK'
    HR = 'HR'
    HV = 'HV'
    I = 'I'
    IL = 'IL'
    IND = 'IND'
    IO = 'IO'
    IR = 'IR'
    IRL = 'IRL'
    IRQ = 'IRQ'
    IS = 'IS'
    J = 'J'
    JA = 'JA'
    JE = 'JE'
    JOR = 'JOR'
    K = 'K'
    KAI = 'KAI'
    KAN = 'KAN'
    KAS = 'KAS'
    KIB = 'KIB'
    KIS = 'KIS'
    KOM = 'KOM'
    KOR = 'KOR'
    KOS = 'KOS'
    KWT = 'KWT'
    L = 'L'
    LAO = 'LAO'
    LAR = 'LAR'
    LB = 'LB'
    LS = 'LS'
    LT = 'LT'
    LV = 'LV'
    M = 'M'
    MA = 'MA'
    MAL = 'MAL'
    MAN = 'MAN'
    MAO = 'MAO'
    MAR = 'MAR'
    MAT = 'MAT'
    MAY = 'MAY'
    MC = 'MC'
    MD = 'MD'
    MEX = 'MEX'
    MF = 'MF'
    MIK = 'MIK'
    MK = 'MK'
    MNE = 'MNE'
    MON = 'MON'
    MOT = 'MOT'
    MOZ = 'MOZ'
    MP = 'MP'
    MS = 'MS'
    MW = 'MW'
    MYA = 'MYA'
    N = 'N'
    NAU = 'NAU'
    NEP = 'NEP'
    NF = 'NF'
    NIC = 'NIC'
    NIU = 'NIU'
    NKA = 'NKA'
    NL = 'NL'
    NLA = 'NLA'
    NMA = 'NMA'
    NZ = 'NZ'
    OTI = 'OTI'
    P = 'P'
    PA = 'PA'
    PAL = 'PAL'
    PE = 'PE'
    PIE = 'PIE'
    PIN = 'PIN'
    PIT = 'PIT'
    PK = 'PK'
    PL = 'PL'
    PNG = 'PNG'
    PRI = 'PRI'
    PSE = 'PSE'
    PY = 'PY'
    QAT = 'QAT'
    RA = 'RA'
    RB = 'RB'
    RC = 'RC'
    RCA = 'RCA'
    RCB = 'RCB'
    RCH = 'RCH'
    REU = 'REU'
    RG = 'RG'
    RH = 'RH'
    RI = 'RI'
    RIM = 'RIM'
    RL = 'RL'
    RM = 'RM'
    RMM = 'RMM'
    RN = 'RN'
    RO = 'RO'
    ROK = 'ROK'
    ROU = 'ROU'
    RP = 'RP'
    RSM = 'RSM'
    RU = 'RU'
    RUS = 'RUS'
    RWA = 'RWA'
    S = 'S'
    SAU = 'SAU'
    SCG = 'SCG'
    SCN = 'SCN'
    SD = 'SD'
    SDN = 'SDN'
    SGP = 'SGP'
    SJ = 'SJ'
    SK = 'SK'
    SLO = 'SLO'
    SME = 'SME'
    SN = 'SN'
    SOL = 'SOL'
    SP = 'SP'
    SRB = 'SRB'
    SSD = 'SSD'
    STP = 'STP'
    SUD = 'SUD'
    SWA = 'SWA'
    SWZ = 'SWZ'
    SX = 'SX'
    SY = 'SY'
    SYR = 'SYR'
    T = 'T'
    TAD = 'TAD'
    TF = 'TF'
    TG = 'TG'
    TJ = 'TJ'
    TN = 'TN'
    TOK = 'TOK'
    TON = 'TON'
    TR = 'TR'
    TT = 'TT'
    TUC = 'TUC'
    TUR = 'TUR'
    TUV = 'TUV'
    TWN = 'TWN'
    UA = 'UA'
    UAE = 'UAE'
    UM = 'UM'
    USA = 'USA'
    USB = 'USB'
    V = 'V'
    VAN = 'VAN'
    VN = 'VN'
    WAG = 'WAG'
    WAL = 'WAL'
    WAN = 'WAN'
    WD = 'WD'
    WF = 'WF'
    WG = 'WG'
    WL = 'WL'
    WS = 'WS'
    WV = 'WV'
    YEM = 'YEM'
    YU = 'YU'
    YV = 'YV'
    Z = 'Z'
    ZA = 'ZA'
    ZRE = 'ZRE'
    ZW = 'ZW'
