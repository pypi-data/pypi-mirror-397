from collections import namedtuple
from teradataml import td_sklearn as osml, OneHotEncodingFit
TeradatamlspkMLArgument = namedtuple('TeradatamlspkMLArgument', ['name', 'default_value', 'description'])

ARGUMENT_MAPPER = {
    "LinearSVC": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxIter", 100, ""),
        TeradatamlspkMLArgument("regParam", 1.0, ""),
        TeradatamlspkMLArgument("tol", 1e-06, ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("fitIntercept", True, ""),
        TeradatamlspkMLArgument("standardization", True, ""),
        TeradatamlspkMLArgument("threshold", 0.0, ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("aggregationDepth", 2, ""),
        TeradatamlspkMLArgument("maxBlockSizeInMB", 0.0, "")
    ],
    "LogisticRegression": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxIter", 100, ""),
        TeradatamlspkMLArgument("regParam", 1.0, ""),
        TeradatamlspkMLArgument("elasticNetParam", 0.0, ""),
        TeradatamlspkMLArgument("tol", 1e-06, ""),
        TeradatamlspkMLArgument("fitIntercept", True, ""),
        TeradatamlspkMLArgument("threshold", 0.5, ""),
        TeradatamlspkMLArgument("thresholds", None, ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("standardization", True, ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("aggregationDepth", 2, ""),
        TeradatamlspkMLArgument("family", "auto", ""),
        TeradatamlspkMLArgument("lowerBoundsOnCoefficients", None, ""),
        TeradatamlspkMLArgument("upperBoundsOnCoefficients", None, ""),
        TeradatamlspkMLArgument("lowerBoundsOnIntercepts", None, ""),
        TeradatamlspkMLArgument("upperBoundsOnIntercepts", None, ""),
        TeradatamlspkMLArgument("maxBlockSizeInMB", 0.0, "")
    ],
    "DecisionTreeClassifier": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("impurity","gini", ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
    ],
    "GBTClassifier": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("lossType", "log_loss", ""),
        TeradatamlspkMLArgument("maxIter", 20, ""),
        TeradatamlspkMLArgument("stepSize", 0.1, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("subsamplingRate", 1.0, ""),
        TeradatamlspkMLArgument("impurity","friedman_mse", ""),
        TeradatamlspkMLArgument("featureSubsetStrategy", "all", ""),
        TeradatamlspkMLArgument("validationTol", 0.01, ""),
        TeradatamlspkMLArgument("validationIndicatorCol", None, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
    ],
    "RandomForestClassifier": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("impurity","gini", ""),
        TeradatamlspkMLArgument("numTrees", 20, ""),
        TeradatamlspkMLArgument("featureSubsetStrategy", "auto", ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("subsamplingRate", 1.0, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
        TeradatamlspkMLArgument("bootstrap", True, "")
    ],
    "NaiveBayes": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("smoothing", 1.0, ""),
        TeradatamlspkMLArgument("modelType", "multinomial", ""),
        TeradatamlspkMLArgument("thresholds", None, ""),
        TeradatamlspkMLArgument("weightCol", None, "")
    ],
    "MultilayerPerceptronClassifier": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxIter", 100, ""),
        TeradatamlspkMLArgument("tol", 1e-06, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("layers", None, ""),
        TeradatamlspkMLArgument("blockSize", 128, ""),
        TeradatamlspkMLArgument("stepSize", 0.03, ""),
        TeradatamlspkMLArgument("solver", "lbfgs", ""),
        TeradatamlspkMLArgument("initialWeights", None, ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
    ],
    "OneVsRest": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("rawPredictionCol", "rawPrediction", ""),
        TeradatamlspkMLArgument("classifier", None, ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("parallelism",1, "")
    ],
    "BisectingKMeans": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxIter", 20, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("k", 4, ""),
        TeradatamlspkMLArgument("minDivisibleClusterSize", 1.0, ""),
        TeradatamlspkMLArgument("distanceMeasure", "euclidean", ""),
        TeradatamlspkMLArgument("weightCol", None, "")
    ],
    "KMeans": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("k", 2, ""),
        TeradatamlspkMLArgument("initMode","k-means++", ""),
        TeradatamlspkMLArgument("initSteps", 2, ""),
        TeradatamlspkMLArgument("tol", 0.0001, ""),
        TeradatamlspkMLArgument("maxIter", 20, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("distanceMeasure", "euclidean", ""),        
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("solver", "auto", ""),
        TeradatamlspkMLArgument("maxBlockSizeInMB", 0.0, "")
    ],
    "GaussianMixture": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("k", 2, ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("tol", 0.01, ""),
        TeradatamlspkMLArgument("maxIter", 100, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("aggregationDepth", 2, ""),       
        TeradatamlspkMLArgument("weightCol", None, "")
    ],
    "LDA": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("maxIter", 20, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("k", 10, ""),
        TeradatamlspkMLArgument("optimizer", "online", ""),
        TeradatamlspkMLArgument("learningOffset", 1024.0, ""),
        TeradatamlspkMLArgument("learningDecay", 0.51, ""),
        TeradatamlspkMLArgument("subsamplingRate", 0.05, ""),
        TeradatamlspkMLArgument("optimizeDocConcentration", True, ""),
        TeradatamlspkMLArgument("docConcentration", None, ""),
        TeradatamlspkMLArgument("topicConcentration", None, ""),
        TeradatamlspkMLArgument("topicDistributionCol", "topicDistribution", ""),
        TeradatamlspkMLArgument("keepLastCheckpoint", True, "")
    ],
    "IDF": [
        TeradatamlspkMLArgument("minDocFreq", 0, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, "")
    ],
    "Imputer": [
        TeradatamlspkMLArgument("strategy", "mean", ""),
        TeradatamlspkMLArgument("missingValue", None, ""),#nan
        TeradatamlspkMLArgument("inputCols", None, ""),
        TeradatamlspkMLArgument("outputCols", None, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("relativeError", 0.001, "")
    ],
    "MaxAbsScaler": [
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, "")
    ],
    "MinHashLSH": [
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("numHashTables", 1, ""),
    ],
    "MinMaxScaler": [
        TeradatamlspkMLArgument("min", 0.0, ""),
        TeradatamlspkMLArgument("max", 1.0, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, "")
    ],
    "OneHotEncoder": [
        TeradatamlspkMLArgument("handleInvalid", "error", ""),
        TeradatamlspkMLArgument("dropLast", True, ""),
        TeradatamlspkMLArgument("inputCols", None, ""),
        TeradatamlspkMLArgument("outputCols", None, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
    ],
    "RobustScaler": [
        TeradatamlspkMLArgument("lower", 0.25, ""),
        TeradatamlspkMLArgument("upper", 0.75, ""),
        TeradatamlspkMLArgument("withCentering", False, ""),
        TeradatamlspkMLArgument("withScaling", True, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("relativeError", 0.001, "")
    ],
    "StandardScaler": [
        TeradatamlspkMLArgument("withMean", False, ""),
        TeradatamlspkMLArgument("withStd", True, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, "")
    ],
    "DecisionTreeRegressor": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("varianceCol", None, ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("impurity","squared_error", ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
    ],
    "IsotonicRegression": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("isotonic", True, ""),
        TeradatamlspkMLArgument("featureIndex", 0, "")
    ],
    "LinearRegression": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxIter", 100, ""),
        TeradatamlspkMLArgument("regParam", 0.0, ""),
        TeradatamlspkMLArgument("elasticNetParam", 0.0, ""),
        TeradatamlspkMLArgument("tol", 1e-06, ""),
        TeradatamlspkMLArgument("solver", "l-bfgs", ""),
        TeradatamlspkMLArgument("loss", "squaredError", ""),
        TeradatamlspkMLArgument("epsilon", 1.35, ""),
        TeradatamlspkMLArgument("fitIntercept", True, ""),
        TeradatamlspkMLArgument("standardization", True, ""),
        TeradatamlspkMLArgument("threshold", 0.0, ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("aggregationDepth", 2, ""),
        TeradatamlspkMLArgument("maxBlockSizeInMB", 0.0, "")
    ],
    "RandomForestRegressor": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("impurity","mse", ""),
        TeradatamlspkMLArgument("numTrees", 20, ""),
        TeradatamlspkMLArgument("featureSubsetStrategy", "auto", ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("subsamplingRate", 1.0, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
        TeradatamlspkMLArgument("bootstrap", True, "")
    ],
    "RegressionEvaluator": [
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("metricName", "rmse", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("throughOrigin", False, "")
    ],
    "VarianceThresholdSelector": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("varianceThreshold", 0.0, "")
    ],
    "PCA": [
        TeradatamlspkMLArgument("k", None, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, "")
    ],
    "Binarizer": [
        TeradatamlspkMLArgument("threshold", 0.0, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("thresholds", None, ""),
        TeradatamlspkMLArgument("inputCols", None, ""),
        TeradatamlspkMLArgument("outputCols", None, "")
    ],
    "GBTRegressor": [
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("maxDepth", 5, ""),
        TeradatamlspkMLArgument("maxBins", 32, ""),
        TeradatamlspkMLArgument("minInstancesPerNode", 1.0, ""),
        TeradatamlspkMLArgument("minInfoGain", 0.0, ""),
        TeradatamlspkMLArgument("maxMemoryInMB", 256, ""),
        TeradatamlspkMLArgument("cacheNodeIds", False, ""),
        TeradatamlspkMLArgument("checkpointInterval", 10, ""),
        TeradatamlspkMLArgument("lossType", "ls", ""),
        TeradatamlspkMLArgument("maxIter", 20, ""),
        TeradatamlspkMLArgument("stepSize", 0.1, ""),
        TeradatamlspkMLArgument("seed", None, ""),
        TeradatamlspkMLArgument("subsamplingRate", 1.0, ""),
        TeradatamlspkMLArgument("impurity","mse", ""),
        TeradatamlspkMLArgument("featureSubsetStrategy", "all", ""),
        TeradatamlspkMLArgument("validationTol", 0.01, ""),
        TeradatamlspkMLArgument("validationIndicatorCol", None, ""),
        TeradatamlspkMLArgument("leafCol", "", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("minWeightFractionPerNode", 0.0, ""),
    ],
    "Bucketizer": [
        TeradatamlspkMLArgument("splits", None, ""),
        TeradatamlspkMLArgument("splitsArray", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("inputCols", None, ""),
        TeradatamlspkMLArgument("outputCols", None, ""),
        TeradatamlspkMLArgument("handleInvalid", "error", "")
    ],
    "SQLTransformer": [
        TeradatamlspkMLArgument("statement", None, "")
    ],
    "ClusteringEvaluator": [
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("featuresCol", "features", ""),
        TeradatamlspkMLArgument("metricName", "silhouette", ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("distanceMeasure", "squaredEuclidean", "")
    ],
    "MulticlassClassificationEvaluator": [
        TeradatamlspkMLArgument("predictionCol", "prediction", ""),
        TeradatamlspkMLArgument("labelCol", "label", ""),
        TeradatamlspkMLArgument("metricName", "f1", ""),
        TeradatamlspkMLArgument("metricLabel", 0.0, ""),
        TeradatamlspkMLArgument("weightCol", None, ""),
        TeradatamlspkMLArgument("beta", 1.0, ""),
        TeradatamlspkMLArgument("probabilityCol", "probability", ""),
        TeradatamlspkMLArgument("eps", 1e-15, ""),
    ],
    "UnivariateFeatureSelector": [
        TeradatamlspkMLArgument("featuresCol", 'features', ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("labelCol", 'label', ""),
        TeradatamlspkMLArgument("selectionMode", "numTopFeatures", ""),
        TeradatamlspkMLArgument("featureType", None, ""),
        TeradatamlspkMLArgument("labelType", None, ""),
        TeradatamlspkMLArgument("selectionThreshold", None, "")
    ],
    "RegexTokenizer": [
        TeradatamlspkMLArgument("minTokenLength", 1, ""),
        TeradatamlspkMLArgument("gaps", True, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("pattern", '[\s]+', ""),
        TeradatamlspkMLArgument("toLowercase", True, ""),
    ],
    "Tokenizer": [
        TeradatamlspkMLArgument("inputCol", None, ""),
        TeradatamlspkMLArgument("outputCol", None, ""),
    ]
}


SPARK_TO_OSML = {
    "LinearSVC":
                {"osml_func": osml.LinearSVC,
                "arguments":
                    {"maxIter": "max_iter", "tol": "tol", "fitIntercept": "fit_intercept", "regParam": "C", "weightCol": "class_weight"}
                },
    "RandomForestClassifier":
                            {"osml_func": osml.RandomForestClassifier,
                            "arguments":
                                {"maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "impurity": "criterion", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf", "weightCol": "class_weight", "bootstrap": "bootstrap"}
                            },
    "LogisticRegression":
                        {"osml_func": osml.LogisticRegression,
                        "arguments":
                            {"maxIter": "max_iter", "tol": "tol", "fitIntercept": "fit_intercept", "regParam": "C", "weightCol": "class_weight"}
                        },
    "DecisionTreeClassifier":
                            {"osml_func": osml.DecisionTreeClassifier,
                            "arguments":
                                {"maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "impurity": "criterion", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf", "weightCol": "class_weight"}
                            },
    "GBTClassifier":
                    {"osml_func": osml.GradientBoostingClassifier,
                    "arguments":
                        {"maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "impurity": "criterion", "lossType": "loss", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf", "subsamplingRate": "subsample", "stepSize": "learning_rate"}
                    },
    "MultilayerPerceptronClassifier":
                                    {"osml_func": osml.MLPClassifier,
                                    "arguments":
                                        {"tol": "tol", "seed": "random_state", "blockSize": "batch_size", "stepSize": "learning_rate_init", "solver": "solver"}
                                    },
    "OneVsRest":
                {"osml_func": osml.OneVsRestClassifier,
                "arguments":
                    {"classifier": "estimator", "parallelism": "n_jobs"}
                }, 
    "DecisionTreeRegressor":
                            {"osml_func": osml.DecisionTreeRegressor,
                            "arguments":
                                {"maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf"}
                            },
    "RandomForestRegressor":
                            {"osml_func": osml.RandomForestRegressor,
                            "arguments":
                                {"numTrees": "n_estimators", "maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "impurity": "criterion", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf", "bootstrap": "bootstrap"}
                            },
    "GBTRegressor":
                {"osml_func": osml.GradientBoostingRegressor,
                "arguments":
                    {"maxDepth": "max_depth", "minInstancesPerNode": "min_samples_split", "impurity": "criterion", "lossType": "loss", "seed": "random_state", "minWeightFractionPerNode": "min_weight_fraction_leaf", "subsamplingRate": "subsample", "stepSize": "learning_rate"}
                },
    "LinearRegression":
                    {"osml_func": osml.LinearRegression,
                    "arguments":
                        {"fitIntercept": "fit_intercept"}
                    },
    "IsotonicRegression":
                        {"osml_func": osml.IsotonicRegression,
                        "arguments":
                            {"isotonic": "increasing"}
                        },
    "BisectingKMeans":
                    {"osml_func": osml.BisectingKMeans,
                    "arguments":
                        {"maxIter": "max_iter", "k": "n_clusters"}
                    },
    "GaussianMixture":
                    {"osml_func": osml.GaussianMixture,
                    "arguments":
                        {"maxIter": "max_iter", "k": "n_components", "tol": "tol", "seed": "random_state"}
                    },
    "KMeans":
            {"osml_func": osml.KMeans,
            "arguments":
                {"maxIter": "max_iter", "k": "n_clusters", "initMode": "init", "initSteps": "n_init", "tol": "tol"}
            },
    "LDA":
        {"osml_func": osml.LatentDirichletAllocation,
        "arguments":
            {"maxIter": "max_iter", "k": "n_components", "learningOffset": "learning_offset", "learningDecay": "learning_decay", "docConcentration": "doc_topic_prior", "topicConcentration": "topic_word_prior", "seed": "random_state"}
        },
    "Imputer":
            {"osml_func": osml.SimpleImputer,
            "arguments":
                {"strategy": "strategy"}
            },
    "MaxAbsScaler":
                    {"osml_func": osml.MaxAbsScaler,
                    "arguments":
                        {}
                    },
    "MinHashLSH":
                    {"osml_func": osml.LSHForest,
                    "arguments":
                        {"seed": "random_state"}
                    },
    "MinMaxScaler":
                    {"osml_func": osml.MinMaxScaler,
                    "arguments":
                        {}
                    },
    "OneHotEncoder":
                    {"osml_func": OneHotEncodingFit,
                    "arguments":
                        {"inputCols": "target_column", "inputCol": "target_column"}
                    },
    "RobustScaler":
                    {"osml_func": osml.RobustScaler,
                    "arguments":
                        {"withCentering": "with_centering", "withScaling": "with_scaling"} 
                    },
    "StandardScaler":
                    {"osml_func": osml.StandardScaler,
                    "arguments":
                        {"withMean": "with_mean", "withStd": "with_std"}
                    },
    "VarianceThresholdSelector":
                                {"osml_func": osml.VarianceThreshold,
                                "arguments":
                                    {"varianceThreshold": "threshold"}
                                },
    "IDF":
        {"osml_func": osml.TfidfVectorizer,
        "arguments":
            {"minDocFreq": "min_df"}
        },
    "PCA":
        {"osml_func": osml.PCA,
        "arguments":
            {"k": "n_components"}
        }
    
}                          

def _get_reference_class(ref_class, ref_class_type="model"):
    from teradatamlspk.ml.classification import LinearSVC, LinearSVCModel, LinearSVCSummary, LinearSVCTrainingSummary, LogisticRegression, LogisticRegressionModel, LogisticRegressionSummary, LogisticRegressionTrainingSummary, RandomForestClassifier, RandomForestClassificationModel, RandomForestClassificationSummary, RandomForestClassificationTrainingSummary, DecisionTreeClassificationModel, DecisionTreeClassifier, GBTClassifier, GBTClassificationModel, NaiveBayes, NaiveBayesModel, MultilayerPerceptronClassificationModel, MultilayerPerceptronClassificationSummary, MultilayerPerceptronClassificationTrainingSummary, MultilayerPerceptronClassifier, OneVsRest, OneVsRestModel                                               
    from teradatamlspk.ml.regression import LinearRegression, LinearRegressionModel, LinearRegressionSummary, LinearRegressionTrainingSummary, DecisionTreeRegressionModel, DecisionTreeRegressor, IsotonicRegression, IsotonicRegressionModel, RandomForestRegressionModel, RandomForestRegressor, GBTRegressor, GBTRegressionModel
    from teradatamlspk.ml.clustering import BisectingKMeans, BisectingKMeansModel, BisectingKMeansSummary, KMeans, KMeansModel, KMeansSummary, GaussianMixture, GaussianMixtureModel, GaussianMixtureSummary, LDA, LDAModel
    from teradatamlspk.ml.feature import IDF, IDFModel, Imputer, ImputerModel, MaxAbsScaler, MaxAbsScalerModel, MinHashLSH, MinHashLSHModel, MinMaxScaler, MinMaxScalerModel, OneHotEncoder, OneHotEncoderModel, RobustScaler, RobustScalerModel, StandardScaler, StandardScalerModel, VarianceThresholdSelector, VarianceThresholdSelectorModel, PCA, PCAModel, UnivariateFeatureSelector, UnivariateFeatureSelectorModel
    from teradatamlspk.ml.stat import Summarizer, SummaryBuilder

    _map = {LinearSVC: {"model": LinearSVCModel},
            LinearSVCModel: {"evaluate": LinearSVCSummary, "summary": LinearSVCTrainingSummary},
            LogisticRegression: {"model": LogisticRegressionModel},
            LogisticRegressionModel: {"evaluate": LogisticRegressionSummary, "summary": LogisticRegressionTrainingSummary},
            DecisionTreeClassifier: {"model": DecisionTreeClassificationModel},
            GBTClassifier: {"model": GBTClassificationModel},
            RandomForestClassifier: {"model": RandomForestClassificationModel},
            RandomForestClassificationModel: {"evaluate": RandomForestClassificationSummary, "summary": RandomForestClassificationTrainingSummary},
            NaiveBayes: {"model": NaiveBayesModel},
            MultilayerPerceptronClassifier: {"model": MultilayerPerceptronClassificationModel},
            MultilayerPerceptronClassificationModel: {"evaluate": MultilayerPerceptronClassificationSummary, "summary": MultilayerPerceptronClassificationTrainingSummary},
            OneVsRest: {"model": OneVsRestModel},
            BisectingKMeans: {"model": BisectingKMeansModel},
            BisectingKMeansModel: {"summary": BisectingKMeansSummary},
            KMeans: {"model": KMeansModel},
            KMeansModel: {"summary": KMeansSummary},
            GaussianMixture: {"model": GaussianMixtureModel},
            GaussianMixtureModel: {"summary": GaussianMixtureSummary},
            LDA: {"model": LDAModel},
            IDF: {"model": IDFModel},
            PCA: {"model": PCAModel},
            Imputer: {"model": ImputerModel},
            MaxAbsScaler: {"model": MaxAbsScalerModel},
            MinHashLSH: {"model": MinHashLSHModel},
            MinMaxScaler: {"model": MinMaxScalerModel},
            OneHotEncoder: {"model": OneHotEncoderModel},
            RobustScaler: {"model": RobustScalerModel},
            StandardScaler: {"model": StandardScalerModel},
            VarianceThresholdSelector: {"model": VarianceThresholdSelectorModel},
            DecisionTreeRegressor: {"model": DecisionTreeRegressionModel},
            IsotonicRegression: {"model": IsotonicRegressionModel},
            LinearRegression: {"model": LinearRegressionModel}, 
            LinearRegressionModel: {"evaluate": LinearRegressionSummary, "summary": LinearRegressionTrainingSummary},
            RandomForestRegressor: {"model": RandomForestRegressionModel},
            GBTRegressor: {"model": GBTRegressionModel},
            UnivariateFeatureSelector: {"model": UnivariateFeatureSelectorModel},
            Summarizer: {"summary": SummaryBuilder}
            }
    return _map.get(ref_class)[ref_class_type]

SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES = {
    "LinearSVC": {"coefficients": "coef_", "numClasses": "classes_", "numFeatures": "n_features_in_", "intercept": "intercept_"},
    "DecisionTreeClassifier": {"toDebugString": "tree_", "featureImportances": "feature_importances_", "numClasses": "n_classes_", "numFeatures": "n_features_in_","thresholds": None, "numNodes": None},
    "MultilayerPerceptronClassifier": {"numClasses": "classes_", "numFeatures": "n_features_in_"},
    "DecisionTreeRegressor": {"featureImportances": "feature_importances_", "numFeatures": "n_features_in_"},
    "LinearRegression": {"coefficients": "coef_", "numFeatures": "n_features_in_", "intercept": "intercept_"},
    "LogisticRegression": {"coefficients": "coef_","numClasses": "classes_", "numFeatures": "n_features_in_", "intercept": "intercept_"},
    "StandardScaler": {"mean": "mean_"},
    "RobustScaler": {"median": "center_", "range": "scale_"},
    "MinMaxScaler": {"originalMax": "data_max_", "originalMin": "data_min_"},
    "PCA": {"explainedVariance": "explained_variance_"},
    "KMeans": {"numIter": "n_iter_"},
    "GaussianMixture": {"weights": "weights_", "numIter": "n_iter_"},
    "GBTClassifier": {"featureImportances": "feature_importances_", "numClasses": "n_classes_", "numFeatures": "n_features_in_"},
    "RandomForestRegressor": {"featureImportances": "feature_importances_", "numFeatures": "n_features_in_"},
    "RandomForestClassifier": {"featureImportances": "feature_importances_", "numClasses": "n_classes_", "numFeatures": "n_features_in_"},
    "OneVsRest": {"models": "estimators_"},
    "GBTRegressor": {"featureImportances": "feature_importances_", "numFeatures": "n_features_in_"}
}