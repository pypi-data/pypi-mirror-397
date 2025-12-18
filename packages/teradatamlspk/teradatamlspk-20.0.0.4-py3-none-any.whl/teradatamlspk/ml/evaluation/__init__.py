from teradatamlspk.ml.param import Params, Param
from teradatamlspk.ml.constants import ARGUMENT_MAPPER, SPARK_TO_OSML
from teradatamlspk.ml.util import _Metrics
from teradataml import RegressionEvaluator as tdml_RegressionEvaluator
from teradataml import Silhouette, ClassificationEvaluator
from teradatamlspk.sql.functions import monotonically_increasing_id
from teradatamlspk.sql.dataframe import DataFrame
from teradataml import td_sklearn as osml

class RegressionEvaluator(Params):
    def evaluate(self, dataset):
        observation_column = self.getlabelCol()
        prediction_column = self.getpredictionCol()
        metric = self.getmetricName()
        r = tdml_RegressionEvaluator(data=dataset._data,
                                observation_column=observation_column,
                                prediction_column=prediction_column,
                                freedom_degrees=[1, 2],
                                independent_features_num=2,
                                metrics=[metric.upper()])
        output = next(r.result.itertuples())._asdict()
        return list(output.values())[0]
    
class ClusteringEvaluator(Params):
    def evaluate(self, dataset):
        data = dataset.withColumn("id", monotonically_increasing_id())
        target_columns = self.getFeaturesCol()
        cluster_id_column = self.getPredictionCol()
        ce = Silhouette(id_column="id",
                        cluster_id_column=cluster_id_column,
                        target_columns=target_columns,
                        data=data,
                        output_type="SCORE")
        output = next(ce.result.itertuples())._asdict()
        return list(output.values())[0]
    
class MulticlassClassificationEvaluator(Params, _Metrics):

    def evaluate(self, dataset):
        self.observation_column = "label"
        self.prediction_column = "prediction"
        self.data = dataset
        for param in self._paramMap:
            if param.name == "predictionCol":
                self.prediction_column = self._paramMap[param]
            if param.name == "labelCol":
                self.observation_column = self._paramMap[param]
        metric = self.getMetricName()
        beta = self.getBeta()
        eps = self.getEps()

        if metric == "truePositiveRateByLabel":
            res =self.truePositiveRateByLabel
        elif metric == "falsePositiveRateByLabel":
            res = self.falsePositiveRateByLabel
        elif metric == "precisionByLabel":
            res = self.precisionByLabel
        elif metric == "recallByLabel":
            res = self.recallByLabel
        elif metric == "weightedTruePositiveRate":
            res = self.weightedTruePositiveRate
        elif metric == "weightedFalsePositiveRate":
            res = self.weightedFalsePositiveRate
        elif metric == "fMeasureByLabel":
            res = self.fMeasureByLabel(beta)
        elif metric == "weightedFMeasure":
            res =self.weightedFMeasure(beta)
        elif metric in ["f1","accuracy","weightedPrecision","weightedRecall"]:
            num_labels = self.get_label_count_df()
            ce = ClassificationEvaluator(data=self.data._data,
                                observation_column=self.observation_column,
                                prediction_column=self.prediction_column,
                                num_labels=num_labels.count())
            for item in ce.output_data.itertuples():
                result = list((item._asdict()).values())
                metric_name = result[1].rstrip('\x00').replace("-","").lower()
                if metric_name == metric.lower():
                    res = result[2]
                if metric_name == "weightedf1" and metric == "f1":
                    res = result[2]
        else: 
            y_true_df , y_pred_df = self.get_ytrue_ypred()
            if metric == "hammingLoss":
                res = osml.hamming_loss(y_true = y_true_df._data, y_pred = y_pred_df._data)
        return res
            
    def get_ytrue_ypred(self):
        return self.data.select(self.observation_column), self.data.select(self.prediction_column)
    
    def get_labels(self):
        num_labels = self.get_label_count_df()
        label = self.observation_column
        return [row.label for row in num_labels.select(label).collect()]
    
    def get_label_count_df(self):
        return self.data.select([self.observation_column]).groupBy(self.observation_column).count()
