from enum import Enum, StrEnum

class CaseStyle(StrEnum):
    SNAKE = "Snake"
    CAMEL = "Camel"
    PASCAL = "Pascal"
    KEBAB = "Kebab"

class DistFamily(StrEnum):
    GAUSSIAN = "Gaussian"
    BINOMIAL = "Binomial"
    NEG_BINOMIAL = "Negative Binomial"

class EstMethod(StrEnum):
    TAYLOR = "Taylor"
    BRR = "BRR"
    BOOTSTRAP = "Bootstrap"
    JACKKNIFE = "Jackknife"

class FitMethod(StrEnum):
    OLS = "OLS"
    WLS = "WLS"
    FH = "FH"
    ML = "ML"
    REML = "REML"

class MeanVarMode(StrEnum):
    EQUAL_VAR = "Equal Variances"
    UNEQUAL_VAR = "Unequal Variances"

class ModelType(StrEnum):
    LINEAR = "Linear"
    LOGISTIC = "Logistic"

class MissingKind(StrEnum):
    DONT_KNOW = "dnk"
    REFUSED = "refused"
    STRUCTURAL = "struct"
    SYSTEM = "system"
    NO_ANSWER = "no_answer"

class MissingMechanism(StrEnum):
    MCAR = "Completely Missing At Random"
    MAR = "Missing At Random"
    MNAR = "Missing Not At Random"

class LetterCase(str, Enum):
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    ORIGINAL = "original"

class LinkFunction(StrEnum):
    IDENTITY = "Identity"
    LOGIT = "Logit"
    PROBIT = "Probit"
    CAUCHY = "Cauchy"
    CLOGLOG = "Cloglog"
    LOGLOG = "Loglog"
    LOG = "Log"
    INVERSE = "Inverse"
    INVERSE_SQUARED = "Inverse Squared"
    INVERSE_POWER = "Inverse Power"

class MeasurementType(StrEnum):
    CONTINUOUS = "Numerical Continuous"
    DISCRETE = "Numerical Discrete"
    NOMINAL = "Categorical Nominal"
    ORDINAL = "Categorical Ordinal"
    STRING = "String"
    BOOLEAN = "Boolean"
    DATETIME = "Datetime"

class OnePropSizeMethod(StrEnum):
    WALD = "Wald"
    FLEISS = "Fleiss"
    WILSON = "Wilson"
    AGRESTI_COULL = "Agresti-Coull"
    CLOPPER_PEARSON = "Clopper-Pearson"

class PopParam(StrEnum):
    MEAN = "Mean"
    TOTAL = "Total"
    PROP = "Proportion"
    RATIO = "Ratio"
    MEDIAN = "Median"

class PPSMethod(StrEnum):
    BREWER = "PPS Brewer"
    MURPHY = "PPS Murphy"
    RS = "PPS Rao-Sampford"
    SYS = "PPS Systematic"
    WR = "PPS with replacement"

class PropVarMode(StrEnum):
    ALT_PROPS = "Alternative Proportions"
    POOLED_PROP = "Pooled Proportion"
    MAX_VAR = "Maximum Variance"

class QuantileMethod(StrEnum):
    LOWER = "Lower"
    HIGHER = "Higher"
    NEAREST = "Nearest"
    LINEAR = "Linear"
    MIDDLE = "Middle"

class SelectMethod(StrEnum):
    SRS_WR = "SRS with replacement"
    SRS_WOR = "SRS without replacement"
    SRS_SYS = "Systematic"
    PPS_BREWER = "PPS Brewer"
    PPS_MURPHY = "PPS Murphy"
    PPS_RS = "PPS Rao-Sampford"
    PPS_SYS = "PPS Systematic"
    PPS_WR = "PPS with replacement"
    GRS = "General"

class SingletonMethod(StrEnum):
    """Estimation options for strata with singleton PSU"""

    ERROR = "Raise Error when one PSU in a stratum"
    SKIP = "Set variance to zero and skip stratum with one PSU"
    CERTAINTY = "Use SSUs or lowest units to estimate the variance"
    COMBINE = "Combine the strata with the singleton psu to another stratum"

class TwoPropsSizeMethod(StrEnum):
    WALD = "Wald (closed-form)"
    NEWCOMBE = "Newcombe"
    MIETTINEN_NURMINEN = "Miettinen-Nurminen"
    FARRINGTON_MANNING = "Farrington-Manning"

class TableType(StrEnum):
    ONE_WAY = "One-Way"
    TWO_WAY = "Two-Way"

class TableUnits(StrEnum):
    PROPORTION = "Proportion"
    PERCENT = "Percent"
    COUNT = "Count"

class TTestType(StrEnum):
    ONE_SAMPLE = "One-Sample"
    TWO_SAMPLE = "Two-Sample"
