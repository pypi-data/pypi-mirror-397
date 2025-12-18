from teradataml import td_sklearn as osml
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.ml.util import Identifiable, _Metrics, _ClusteringMethods, _ClusteringModelMethods, _GenericMethods
from teradatamlspk.ml.param import Params, Param
from teradatamlspk.ml.constants import ARGUMENT_MAPPER, SPARK_TO_OSML


BisectingKMeans = type("BisectingKMeans", (Params, _ClusteringMethods ), {})
BisectingKMeansModel = type("BisectingKMeansModel", (_ClusteringModelMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})
BisectingKMeansSummary = type("BisectingKMeansSummary", (_Metrics, ), {})

KMeans = type("KMeans", (Params, _ClusteringMethods ), {})
KMeansModel = type("KMeansModel", (_ClusteringModelMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item), "hasSummary": True})
KMeansSummary = type("KMeansSummary", (_Metrics, ), {})

GaussianMixture = type("GaussianMixture", (Params, _ClusteringMethods ), {})
GaussianMixtureModel = type("GaussianMixtureModel", (_ClusteringModelMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item), "hasSummary": True})
GaussianMixtureSummary = type("GaussianMixtureSummary", (_Metrics, ), {})

LDA = type("LDA", (Params, ), {})
LDAModel = type("LDAModel", (_GenericMethods, ), {"__getattr__": lambda self, item: Params.model_getattr(self, item)})

