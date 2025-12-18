from teradataml import td_sklearn as osml
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.ml.util import _FeatureMethods, _StandardScalarMethods, _ImputerMethods, _MaxAbsScalerMethods, \
    _MinMaxScalerMethods, _VarianceThresholdMethods, _PCAMethods, _BinarizerMethods, _OneHotEncoder, _BucketizerMethods,\
    _SQLTransformerMethods, _UnivariateFeatureSelector, _RegexTokenizerMethods
from teradatamlspk.ml.param import Params, Param
from teradatamlspk.ml.constants import ARGUMENT_MAPPER, SPARK_TO_OSML

IDF = type("IDF", (Params, _FeatureMethods, ), {})
IDFModel = type("IDFModel", (_FeatureMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

PCA = type("PCA", (Params, _PCAMethods, ), {})
PCAModel = type("PCAModel", (_PCAMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

Imputer = type("Imputer", (Params, _ImputerMethods, ), {})
ImputerModel = type("ImputerModel", (_ImputerMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

MaxAbsScaler = type("MaxAbsScaler", (Params, _MaxAbsScalerMethods, ), {})
MaxAbsScalerModel = type("MaxAbsScalerModel", (_MaxAbsScalerMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

MinHashLSH = type("MinHashLSH", (Params, _FeatureMethods, ), {})
MinHashLSHModel = type("MinHashLSHModel", (_FeatureMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

MinMaxScaler = type("MinMaxScaler", (Params, _MinMaxScalerMethods, ), {})
MinMaxScalerModel = type("MinMaxScalerModel", (_MinMaxScalerMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

OneHotEncoder = type("OneHotEncoder", (Params, _OneHotEncoder, ), {})
OneHotEncoderModel = type("OneHotEncoderModel", (_OneHotEncoder, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

RobustScaler = type("RobustScaler", (Params, _FeatureMethods, ), {})
RobustScalerModel = type("RobustScalerModel", (_FeatureMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

StandardScaler = type("StandardScaler", (Params, _StandardScalarMethods, ), {})
StandardScalerModel = type("StandardScalerModel", (_StandardScalarMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

VarianceThresholdSelector = type("VarianceThresholdSelector", (Params, _VarianceThresholdMethods, ), {})
VarianceThresholdSelectorModel = type("VarianceThresholdSelectorModel", (_VarianceThresholdMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

Binarizer = type("Binarizer", (Params, _BinarizerMethods, ), {})

Bucketizer = type("Bucketizer", (Params, _BucketizerMethods, ), {})

SQLTransformer = type("SQLTransformer", (Params, _SQLTransformerMethods, ), {})

UnivariateFeatureSelector = type("UnivariateFeatureSelector", (Params, _UnivariateFeatureSelector, ), {})
UnivariateFeatureSelectorModel = type("UnivariateFeatureSelectorModel", (_UnivariateFeatureSelector, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

RegexTokenizer = type("RegexTokenizer", (Params, _RegexTokenizerMethods, ), {})

Tokenizer = type("Tokenizer", (Params, _RegexTokenizerMethods, ), {})

class VectorAssembler:
    def __init__(self, *, inputCols=None, outputCol=None, handleInvalid='error'):
        self._inputCols = inputCols
        self.outputCol = outputCol

    def transform(self, df):
        df._ml_params = {"inputCols": self._inputCols, "outputCol": self.outputCol}
        return df

    def clear(self, param):
        pass

    def copy(self, extra=None):
        pass

    def explainParam(self, param):
        pass

    def explainParams(self):
        pass

    def extractParamMap(extra=None):
        pass

    def getHandleInvalid(self):
        pass

    def getInputCols(self):
        return self._params.get("inputCols")

    def getOrDefault(self):
        pass

    def getOutputCol(self):
        return self._params.get("outputCol")

    def getParam(self, paramName):
        pass

    def hasDefault(self, param):
        pass

    def hasParam(self, paramName):
        pass

    def isDefined(self, param):
        pass

    def isSet(self,param):
        pass

    @classmethod
    def load(cls, path):
        pass

    @classmethod
    def read(cls):
        pass

    @classmethod
    def save(cls, path):
        pass

    def set(self, param, value):
        pass

    def setHandleInvalid(self, value):
        pass

    def setInputCols(self, value):
        pass

    def setOutputCol(self, value):
        pass

    def setParams(self, *, inputCols=None, outputCol=None, handleInvalid="error"):
        pass

    def write(self):
        pass

