import uuid
import re
import numpy as np
import pandas as pd
from collections import OrderedDict
from teradatamlspk.ml.constants import SPARK_TO_OSML, _get_reference_class
from teradatamlspk.sql.column import Column
from teradatamlspk.sql.dataframe import DataFrame
from teradatamlspk.sql.functions import pow, sqrt, sum
from teradataml import configure, ScaleFit, ScaleTransform, SimpleImputeFit, SimpleImputeTransform, case, valib, NGramSplitter
from teradataml.common.utils import UtilFuncs
from teradataml import configure
from teradataml import td_sklearn as osml
from teradataml import DataFrame as tdmldf

class Identifiable:
    """
    Object with a unique ID.
    """

    def __init__(self) -> None:
        #: A unique id for the object.
        self.uid = self._randomUID()

    def __repr__(self) -> str:
        return self.uid

    @classmethod
    def _randomUID(cls) -> str:
        """
        Generate a unique string id for the object. The default implementation
        concatenates the class name, "_", and 12 random hex chars.
        """
        return str(cls.__name__ + "_" + uuid.uuid4().hex[-12:])

class _LoadSaveModel:

    def save(self):
        # TODO: Implement with ELE-6517.
        raise NotImplementedError()

    def load(self):
        # TODO: Implement with ELE-6517.
        raise NotImplementedError()

    def read(self):
        # TODO: Implement with ELE-6517.
        raise NotImplementedError()

    def write(self):
        # TODO: Implement with ELE-6517.
        raise NotImplementedError()



class _GenericMethods(_LoadSaveModel):
    """ Generic Methods for Classification and Regression. """

    def fit(self, dataset, params=None):

        from teradatamlspk.ml.classification import SPARK_TO_OSML

        self._train_data_set = dataset
        osml_func = SPARK_TO_OSML[self.__class__.__name__]["osml_func"]

        # Create dummy object with out any argument.
        dummy_osml_func = osml_func()
        osml_args = {}
        for spark_arg, osml_arg in SPARK_TO_OSML[self.__class__.__name__]["arguments"].items():
            if osml_arg in dummy_osml_func.__dict__:
                osml_args[osml_arg] = self.getOrDefault(getattr(self, spark_arg))

        sklearn_lvc = osml_func(**osml_args)

        # Check if user passed feature columns and output columns a.k.a label columns or not.
        # If passed, consider those. Else, Check if the input dataframe is output of VectorAssembler
        # or not. If yes, use those. Else, use default values.
        feature_columns = self._train_data_set._ml_params.get("inputCols", self.getfeaturesCol())
        self.setfeaturesCol(feature_columns)
        output_column = self.getlabelCol()
        X = self._train_data_set._data.select(feature_columns)
        Y = self._train_data_set._data.select(output_column)
        self.osml_fitted_model = sklearn_lvc.fit(X, Y)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model i.e, if fit is on LinearSVC,
        # this method generates object of LinearSVCModel. Arguments which are
        # declared in LinearSVC should be accessed from LinearSVCModel too.
        # Hence store the reference for actual model.
        model_obj._spark_model_obj = self

        from teradatamlspk.ml.constants import SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES
        model_attributes = SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES.get(self.__class__.__name__, {})

        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute, getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
            if spark_model_attribute == "numClasses":
                numClasses = getattr(self.osml_fitted_model, osml_model_attribute)
                if isinstance(numClasses, np.ndarray):
                    setattr(model_obj, spark_model_attribute, len(numClasses))
            if spark_model_attribute == "intercept":
                intercept = getattr(self.osml_fitted_model, osml_model_attribute)
                if isinstance(intercept, np.ndarray):
                    setattr(model_obj, spark_model_attribute, intercept[0])

        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X =  dataset._data.select(self.getFeaturesCol())
        Y =  dataset._data.select(self.getlabelCol())
        tdml_df = self._model.predict(X=X, y=Y)
        # Assuming last column is always prediction column.
        return DataFrame(tdml_df).withColumnRenamed(tdml_df.columns[-1], self.getpredictionCol())

    def evaluate(self, dataset, params=None):
        summary_obj = _get_reference_class(self.__class__, ref_class_type="evaluate")
        _obj = summary_obj()
        _obj._data = dataset
        _obj._model = self.osml_fitted_model
        _obj._spark_model_obj = self
        _obj._predicted_output = self.transform(dataset)
        return _obj

    def summary(self):
        training_summary = _get_reference_class(self.__class__, ref_class_type="summary")
        _obj = training_summary()
        _obj._data = self._train_data_set
        _obj._model = self.osml_fitted_model
        _obj._predicted_output = self.transform(self._train_data_set)
        _obj._spark_model_obj = self
        return _obj

    def fitMultiple(self):
        raise NotImplementedError()

    def copy(self, extra=None):
        cls = self.__class__
        params = {**self._kwargs}
        if extra:
            params.update(extra if extra else {})
        return cls(**params)

    def predict(self, value):
        return self._model.modelObj.predict([value])[0]

    def predictRaw(self, value):
        raise NotImplementedError


class _FeatureMethods(_LoadSaveModel):

    def fit(self, dataset, params=None):

        from teradatamlspk.ml.classification import SPARK_TO_OSML

        self._train_data_set = dataset
        osml_func = SPARK_TO_OSML[self.__class__.__name__]["osml_func"]
        dummy_osml_func = osml_func()
        osml_args = {}
        for spark_arg, osml_arg in SPARK_TO_OSML[self.__class__.__name__]["arguments"].items():
            if osml_arg in dummy_osml_func.__dict__:
                osml_args[osml_arg] = self.getOrDefault(getattr(self, spark_arg))

        sklearn_lvc = osml_func(**osml_args)

        # Check if user passed feature columns and output columns a.k.a label columns or not.
        # If passed, consider those. Else, Check if the input dataframe is output of VectorAssembler
        # or not. If yes, use those. Else, use default values.
        input_columns = self._train_data_set._ml_params.get("inputCols", self.getinputCol())
        self.setinputCol(input_columns)
        output_columns = self.getoutputCol()
        X = self._train_data_set._data.select(input_columns)
        self.osml_fitted_model = sklearn_lvc.fit(X)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model i.e, if fit is on LinearSVC,
        # this method generates object of LinearSVCModel. Arguments which are
        # declared in LinearSVC should be accessed from LinearSVCModel too.
        # Hence store the reference for actual model.
        model_obj._spark_model_obj = self

        from teradatamlspk.ml.constants import SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES
        model_attributes = SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES.get(self.__class__.__name__, {})

        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute,
                    getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X = dataset._data.select(self.getinputCol())
        tdml_df = self._model.transform(X=X)
        output_columns = self.getoutputCol()
        # Assuming last column is always prediction column.
        colsMap = {}
        _i = len(tdml_df.columns) // 2
        for existing_col, col_to_rename in zip(tdml_df.columns[_i:], output_columns):
            colsMap[existing_col] = col_to_rename
        return DataFrame(tdml_df).withColumnsRenamed(colsMap)
    
    def copy(self, extra=None):
        cls = self.__class__
        params = {**self._kwargs}
        if extra:
            params.update(extra if extra else {})
        return cls(**params)

class _PCAMethods(_FeatureMethods):

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X =  dataset._data.select(self.getinputCol())
        tdml_df = self._model.transform(X=X)
        return DataFrame(tdml_df)

class _NaiveBayesMethods(_GenericMethods):

    def fit(self, dataset, params=None):

        SPARK_ARG_TO_OSML_ARG = {
            "multinomial" : {"smoothing": "alpha"},
            "bernoulli" : {"smoothing": "alpha"},
            "gaussian" : {}
        }

        if self.getModelType() == "multinomial":
            osml_func = osml.MultinomialNB
        elif self.getModelType() == "bernoulli":
            osml_func = osml.BernoulliNB
        else:
            osml_func = osml.GaussianNB

        osml_args = {}
        dummy_osml_func = osml_func()
        for spark_arg, osml_arg in SPARK_ARG_TO_OSML_ARG[self.getModelType()].items():
            if osml_arg in dummy_osml_func.__dict__:
                osml_args[osml_arg] = self.getOrDefault(getattr(self, spark_arg))
        sklearn_lvc = osml_func(**osml_args)

        # Check if user passed feature columns and output columns a.k.a label columns or not.
        # If passed, consider those. Else, Check if the input dataframe is output of VectorAssembler
        # or not. If yes, use those. Else, use default values.
        self._train_data_set = dataset
        feature_columns = self._train_data_set._ml_params.get("inputCols", self.getfeaturesCol())
        self.setfeaturesCol(feature_columns)
        output_column = self.getlabelCol()
        X = self._train_data_set._data.select(feature_columns)
        Y = self._train_data_set._data.select(output_column)

        self.osml_fitted_model = sklearn_lvc.fit(X, Y)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model
        model_obj._spark_model_obj = self

        SPARK_ATTR_TO_OSML_ATTR = {
            "multinomial" : {"numFeatures": "n_features_in_", "pi" : "class_log_prior_", "numClasses": "class_count_"},
            "bernoulli" : {"numFeatures": "n_features_in_", "pi" : "class_log_prior_", "numClasses": "class_count_"},
            "gaussian" : {"sigma": "var_", "numClasses": "class_count_"}
        }

        model_attributes = SPARK_ATTR_TO_OSML_ATTR.get(self.getModelType(), {})
        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute, getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
            if spark_model_attribute == "numClasses":
                numClasses = getattr(self.osml_fitted_model, osml_model_attribute)
                if isinstance(numClasses, np.ndarray):
                    setattr(model_obj, spark_model_attribute, len(numClasses))
        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X =  dataset._data.select(self.getFeaturesCol())
        Y =  dataset._data.select(self.getlabelCol())
        tdml_df = self._model.predict(X=X, y=Y)
        # Assuming last column is always prediction column.
        return DataFrame(tdml_df).withColumnRenamed(tdml_df.columns[-1], self.getpredictionCol())

class _ClusteringMethods(_GenericMethods):

    def fit(self, dataset, params=None):

        from teradatamlspk.ml.classification import SPARK_TO_OSML

        self._train_data_set = dataset
        osml_func = SPARK_TO_OSML[self.__class__.__name__]["osml_func"]
        osml_args = {}
        dummy_osml_func = osml_func()
        for spark_arg, osml_arg in SPARK_TO_OSML[self.__class__.__name__]["arguments"].items():
            if osml_arg in dummy_osml_func.__dict__:
                osml_args[osml_arg] = self.getOrDefault(getattr(self, spark_arg))

        sklearn_lvc = osml_func(**osml_args)

        # Check if user passed feature columns and output columns a.k.a label columns or not.
        # If passed, consider those. Else, Check if the input dataframe is output of VectorAssembler
        # or not. If yes, use those. Else, use default values.
        input_columns = self._train_data_set._ml_params.get("inputCols", self.getfeaturesCol())
        self.setfeaturesCol(input_columns)
        X = self._train_data_set._data.select(input_columns)
        self.osml_fitted_model = sklearn_lvc.fit(X)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model i.e, if fit is on LinearSVC,
        # this method generates object of LinearSVCModel. Arguments which are
        # declared in LinearSVC should be accessed from LinearSVCModel too.
        # Hence store the reference for actual model.
        model_obj._spark_model_obj = self

        from teradatamlspk.ml.constants import SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES
        model_attributes = SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES.get(self.__class__.__name__, {})

        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute, getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
        return model_obj

class _ClusteringModelMethods(_GenericMethods):

    @property
    def summary(self):
        summary = _get_reference_class(self.__class__, ref_class_type="summary")
        _obj = summary()
        _obj._data = self._train_data_set
        _obj._model = self.osml_fitted_model
        _obj._predicted_output = self.transform(self._train_data_set)
        _obj._spark_model_obj = self
        return _obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X =  dataset._data.select(self.getfeaturesCol())
        tdml_df = self._model.predict(X=X)
        output_column = self.getpredictionCol()
        return DataFrame(tdml_df).withColumnRenamed(tdml_df.columns[-1], output_column)
    
class LinearRegressionMethods(_GenericMethods):

    @property
    def summary(self):
        from teradatamlspk.ml.regression import LinearRegressionTrainingSummary
        _obj = LinearRegressionTrainingSummary()
        _obj._data = self._train_data_set
        _obj._model = self.osml_fitted_model
        _obj._predicted_output = self.transform(self._train_data_set)
        _obj._spark_model_obj = self
        _obj._metrics = {}
        return _obj

    def evaluate(self, dataset, params=None):
        summary_obj = _get_reference_class(self.__class__, ref_class_type="evaluate")
        _obj = summary_obj()
        _obj._data = dataset
        _obj._model = self.osml_fitted_model
        _obj._spark_model_obj = self
        _obj._predicted_output = self.transform(dataset)
        _obj._metrics = {}
        return _obj
    
class LogisticRegressionMethods(_GenericMethods):

    @property
    def summary(self):
        from teradatamlspk.ml.classification import LogisticRegressionTrainingSummary
        _obj = LogisticRegressionTrainingSummary()
        _obj._data = self._train_data_set
        _obj._model = self.osml_fitted_model
        _obj._predicted_output = self.transform(self._train_data_set)
        _obj._spark_model_obj = self
        _obj._metrics = {}
        return _obj
        
class RandomForestClassifierMethods(_GenericMethods):

    @property
    def summary(self):
        from teradatamlspk.ml.classification import RandomForestClassificationTrainingSummary
        _obj = RandomForestClassificationTrainingSummary()
        _obj._data = self._train_data_set
        _obj._model = self.osml_fitted_model
        _obj._predicted_output = self.transform(self._train_data_set)
        _obj._spark_model_obj = self
        _obj._metrics = {}
        return _obj
    
class _OneVsRestMethods(_GenericMethods):
    
    def fit(self, dataset, params=None):

        from teradatamlspk.ml.classification import SPARK_TO_OSML

        self._train_data_set = dataset
        osml_func = SPARK_TO_OSML[self.__class__.__name__]["osml_func"]
        osml_args = {}
        for spark_arg, osml_arg in SPARK_TO_OSML[self.__class__.__name__]["arguments"].items():
            if spark_arg == "classifier":
                #Get the classifier object
                classifier = self.getOrDefault(getattr(self, spark_arg))
                func = classifier.__class__.__name__

                #Convert the classifier arguments to osml arguments.
                func_args = {}
                for spk_arg, os_arg in SPARK_TO_OSML[func]["arguments"].items():
                    func_args[os_arg] = classifier.getOrDefault(getattr(classifier, spk_arg))

                #Convert the tdmlspk classifier object to osml object.
                osml_classifier = SPARK_TO_OSML[func]["osml_func"]
                osml_args[osml_arg] = osml_classifier(**func_args)
            else:
                osml_args[osml_arg] = self.getOrDefault(getattr(self, spark_arg))

        sklearn_lvc = osml_func(**osml_args)

        # Check if user passed feature columns and output columns a.k.a label columns or not.
        # If passed, consider those. Else, Check if the input dataframe is output of VectorAssembler
        # or not. If yes, use those. Else, use default values.
        feature_columns = self._train_data_set._ml_params.get("inputCols", self.getfeaturesCol())
        self.setfeaturesCol(feature_columns)
        output_column = self.getlabelCol()
        X = self._train_data_set._data.select(feature_columns)
        Y = self._train_data_set._data.select(output_column)
        self.osml_fitted_model = sklearn_lvc.fit(X, Y)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model
        model_obj._spark_model_obj = self

        from teradatamlspk.ml.constants import SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES
        model_attributes = SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES.get(self.__class__.__name__, {})

        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute, getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
        return model_obj

class _ModelSummaryMethods:

    @property
    def labelCol(self):
        spark_model = self._spark_model_obj
        return spark_model.getOrDefault(spark_model.labelCol)

    @property
    def labels(self):
        return self._spark_model_obj._model.modelObj.classes_

    @property
    def predictionCol(self):
        spark_model = self._spark_model_obj
        return spark_model.getOrDefault(spark_model.predictionCol)

    @property
    def weightCol(self):
        spark_model = self._spark_model_obj
        return spark_model.getOrDefault(spark_model.weightCol)

    @property
    def featuresCol(self):
        spark_model = self._spark_model_obj
        return spark_model.getOrDefault(spark_model.featuresCol)

class _StandardScalarMethods(_GenericMethods):

    def fit(self, dataset, params=None):
        self._train_data_set = dataset
        input_columns = self._train_data_set._ml_params.get("inputCols", self.getinputCol())

        fit_obj = ScaleFit(data=dataset._data,
                           target_columns=input_columns,
                           scale_method="MEAN" if self.getwithMean() else "STD",
                           miss_value="KEEP",
                           global_scale=False,
                           multiplier="1",
                           intercept="0")

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = fit_obj

        # Store the reference of the actual model.
        model_obj._spark_model_obj = self

        # model object has mean and std as attributes.
        _df = dataset._data.select(input_columns)

        # TODO: mean and std can be triggered in a single expression.
        model_obj.mean = next(_df.mean().itertuples(None))
        model_obj.std = next(_df.std().itertuples(None))

        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        fitted_columns = self._spark_model_obj._train_data_set._ml_params.get(
            "inputCols", self._spark_model_obj.getinputCol())

        remaining_columns = [column for column in dataset.columns if column not in fitted_columns]

        transformed_obj = ScaleTransform(data=dataset._data,
                                         object=self._model.output,
                                         accumulate=remaining_columns)
        return DataFrame(transformed_obj.result)

class _BinarizerMethods(_GenericMethods):
    def transform(self, dataset = None, params = None):
        if params is not None:
            for param, value in params.items():
                self._paramMap[param] = value

        tdml_df = dataset._data

        if self.getinputCol() is not None and self.getinputCols() is not None:
            raise Exception("Exactly one of inputCol, inputCols Params to be set, but both are set.")

        if self.getinputCol():
            threshold = self.getThreshold()
            input_column = self.getinputCol()
            output_column = self.getoutputCol()
            _assign_expr = {output_column: case([(tdml_df[input_column] > threshold, 1)], else_=0.0)}
        else:
            threshold = self.getThresholds()
            input_columns = self.getinputCols()
            output_columns = self.getoutputCols()
            _assign_expr = {output_column: case([(tdml_df[input_column] > threshold, 1)], else_=0.0) for
                            input_column, output_column, threshold in zip(input_columns, output_columns, threshold)}
        tdml_df = tdml_df.assign(**_assign_expr)
        res = DataFrame(tdml_df)
        return res

class _SQLTransformerMethods(_GenericMethods):
    def transform(self, dataset = None, params = None):

        if params is not None:
            for param, value in params.items():
                self._paramMap[param] = value
        tdml_df = dataset._data

        df_statement = tdml_df.show_query()
        df_stmnt = "(" + df_statement + ")" + " as tmp"

        # Checking for patterns if the query have any of the mentioned pattern with * i.e
        # "Select *" or "select   *" or "* from" or "*  from" in that case just replace
        # "*" by "tmp.*"
        patterns = [(r'select\s*\*', 'select tmp.*'),
                   (r'\*\s*from', 'tmp.* from')]
        query = self.getStatement()
        for pattern, replacement in patterns:
            query = re.sub(pattern, replacement, query, flags=re.IGNORECASE)

        final_query = query.replace("__THIS__", df_stmnt)
        tdml_df = tdmldf.from_query(final_query)
        res = DataFrame(tdml_df)
        return res


class _BucketizerMethods(_GenericMethods):

    @staticmethod
    def _get_bucketed_expression(tdml_df, column_name, buckets):
        total_buckets = len(buckets)
        conditions = []
        for _i in range(total_buckets - 1):
            bucket_start = buckets[_i]
            bucket_end = buckets[_i + 1]
            if bucket_start == float("-inf"):
                conditions.append((tdml_df[column_name] < bucket_end, _i))
            elif bucket_start == float("inf"):
                conditions.append((tdml_df[column_name] > bucket_start, _i))
            else:
                conditions.append(((tdml_df[column_name] > bucket_start) & (tdml_df[column_name] < bucket_end), _i))
        return case(conditions, else_ = total_buckets)

    def transform(self, dataset = None, params = None):
        if params is not None:
            for param, value in params.items():
                self._paramMap[param] = value
        tdml_df = dataset._data
        _assign_expr = OrderedDict()
        if self.getinputCol() is not None and self.getinputCols() is not None:
            raise Exception("Exactly one of inputCol, inputCols Params to be set, but both are set.")

        if self.getinputCol():
            spls = self.getsplits()
            input_column = self.getinputCol()
            output_column = self.getoutputCol()
            conditions = self._get_bucketed_expression(tdml_df, input_column, spls)
            _assign_expr[output_column] = conditions
        else:
            splsArray = self.getsplitsArray()
            input_columns = self.getinputCols()
            output_columns = self.getoutputCols()
            for arr, inp, out in zip(splsArray, input_columns, output_columns):
                conditions = self._get_bucketed_expression(tdml_df, inp, arr)
                _assign_expr[out] = conditions

        tdml_df = tdml_df.assign(**_assign_expr)
        res = DataFrame(tdml_df)
        return res

class _ImputerMethods(_GenericMethods):

    def fit(self, dataset, params=None):
        self._train_data_set = dataset

        stats = self.getstrategy().upper()

        input_columns, output_columns = self._get_input_output_columns(dataset)

        tdml_df = dataset._data

        # Generate additional columns.
        tdml_df = tdml_df.assign(**{out_col: tdml_df[inp_col] for out_col, inp_col in
                                    zip(output_columns, input_columns)})
        fit_obj = SimpleImputeFit(data=tdml_df,
                                  stats=stats,
                                  stats_columns=output_columns)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = fit_obj

        # Store the reference of the actual model.
        model_obj._spark_model_obj = self

        return model_obj

    def transform(self, dataset):

        input_columns, output_columns = self._get_input_output_columns(dataset)

        tdml_df = dataset._data
        tdml_df = tdml_df.assign(
            **{out_col: tdml_df[inp_col] for out_col, inp_col in zip(output_columns, input_columns)})

        from teradatamlspk.sql.dataframe import DataFrame

        transformed_obj = self._model.transform(data=tdml_df)
        return DataFrame(transformed_obj.result)

    def _get_input_output_columns(self, dataset):

        input_columns = self._train_data_set._ml_params.get("inputCols", self.getinputCols())
        output_columns = self._train_data_set._ml_params.get("outputCol", self.getoutputCol())

        # User can pass inputCol also instead of inputCols.
        if input_columns is None:
            input_columns = self.getinputCol()

        # User can pass outputCols also instead of outputCol.
        if output_columns is None:
            output_columns = self.getoutputCols()

        output_columns = [output_columns] if not isinstance(output_columns, list) else output_columns
        input_columns = [input_columns] if not isinstance(input_columns, list) else input_columns

        return input_columns, output_columns

    @property
    def surrogateDF(self):

        columns_to_rename = self.getinputCols() if self.getinputCols() else self.getinputCol()
        columns_to_rename = [columns_to_rename] if not isinstance(columns_to_rename, list) else columns_to_rename

        tdml_df = self._model.output
        pivoted_df = tdml_df.select(['TD_TARGETCOLUMN_SIMFIT', 'TD_NUM_COLVAL_SIMFIT']).pivot(
            columns=tdml_df.TD_TARGETCOLUMN_SIMFIT, aggfuncs=tdml_df.TD_NUM_COLVAL_SIMFIT.max(),
            returns=columns_to_rename)

        from teradatamlspk.sql.dataframe import DataFrame
        return DataFrame(pivoted_df).withColumnsRenamed({
            actual_col: col_to_rename for actual_col, col_to_rename in zip(pivoted_df.columns, columns_to_rename)})


class _MaxAbsScalerMethods(_GenericMethods):

    def fit(self, dataset, params=None):
        self._train_data_set = dataset
        input_columns = self._train_data_set._ml_params.get("inputCols", self.getinputCol())
        input_columns = UtilFuncs._as_list(input_columns)

        tdml_df = dataset._data

        model_obj = _get_reference_class(self.__class__)()

        # Store the reference of the actual model.
        model_obj._spark_model_obj = self

        # Extract absolute values for all input columns and store it in maxAbs.
        _df = tdml_df.assign(**{col:tdml_df[col].abs().max() for col in input_columns}, drop_columns=True)
        rec = next(_df.itertuples())._asdict()

        model_obj.maxAbs = [rec[col] for col in input_columns]
        return model_obj

    def transform(self, dataset):

        tdml_df = dataset._data

        fitted_columns = self._spark_model_obj._train_data_set._ml_params.get(
            "inputCols", self._spark_model_obj.getinputCol())

        fitted_columns = {col: tdml_df[col]/(maxAbs if maxAbs !=0 else 1) for col, maxAbs in zip(
            UtilFuncs._as_list(fitted_columns), self.maxAbs)}

        remaining_columns = [column for column in dataset.columns if column not in fitted_columns]
        remaining_columns = {col: tdml_df[col] for col in UtilFuncs._as_list(remaining_columns)}

        transformed_df = tdml_df.assign(**fitted_columns, **remaining_columns, drop_columns=True)
        return DataFrame(transformed_df)

class _MinMaxScalerMethods(_GenericMethods):

    def fit(self, dataset, params=None):
        self._train_data_set = dataset
        input_columns = self._train_data_set._ml_params.get("inputCols", self.getinputCol())
        input_columns = UtilFuncs._as_list(input_columns)

        tdml_df = dataset._data

        model_obj = _get_reference_class(self.__class__)()

        # Store the reference of the actual model.
        model_obj._spark_model_obj = self

        # Extract Min/Max values for all input columns and store it.
        min_cols = {"min_{}".format(col): tdml_df[col].min() for col in input_columns}
        max_cols = {"max_{}".format(col): tdml_df[col].max() for col in input_columns}
        _df = tdml_df.assign(**min_cols, **max_cols, drop_columns=True)
        rec = next(_df.itertuples())._asdict()

        model_obj.originalMin = [rec["min_{}".format(col)] for col in input_columns]
        model_obj.originalMax = [rec["max_{}".format(col)] for col in input_columns]
        return model_obj

    def transform(self, dataset):

        tdml_df = dataset._data

        fitted_columns = self._spark_model_obj._train_data_set._ml_params.get(
            "inputCols", self._spark_model_obj.getinputCol())
        fitted_columns = UtilFuncs._as_list(fitted_columns)
        remaining_columns = [column for column in dataset.columns if column not in fitted_columns]

        # Get min and max.
        min_ = self.getmin()
        max_ = self.getmax()
        diff_ = max_-min_

        expr = lambda col_expr, min_val, max_val: (((min_val-col_expr)/(max_val-min_val))*diff_)+min_ if min_val != max_val else ((min_+max_)/2)

        fitted_columns = {col: expr(tdml_df[col], min_val, max_val) for min_val, max_val, col in zip(
            self.originalMin, self.originalMax, fitted_columns)}

        remaining_columns = {col: tdml_df[col] for col in UtilFuncs._as_list(remaining_columns)}

        transformed_df = tdml_df.assign(**fitted_columns, **remaining_columns, drop_columns=True)
        return DataFrame(transformed_df)

class _VarianceThresholdMethods(_GenericMethods):

    def fit(self, dataset, params=None):
        self._train_data_set = dataset
        input_columns = UtilFuncs._as_list(self.getfeaturesCol())

        tdml_df = dataset._data

        model_obj = _get_reference_class(self.__class__)()

        # Store the reference of the actual model.
        model_obj._spark_model_obj = self

        # Calculate Variance for all feature Columns columns and store it.
        _df = tdml_df.assign(**{col: tdml_df[col].var() for col in input_columns}, drop_columns=True)
        rec = next(_df.itertuples())._asdict()
        model_obj.selectedFeatures = [col for col in input_columns if rec[col] > self.getvarianceThreshold()]

        return model_obj

    def transform(self, dataset):

        tdml_df = dataset._data

        fitted_columns = UtilFuncs._as_list(self.getfeaturesCol())
        remaining_columns = [column for column in dataset.columns if column not in fitted_columns]

        columns_to_select = [col for col in tdml_df.columns if col in remaining_columns+self.selectedFeatures]
        transformed_df = tdml_df.select(columns_to_select)
        return DataFrame(transformed_df)
    
class _RegexTokenizerMethods(_GenericMethods):
    """ RegexTokenizer genric methods and transform method"""

    def transform(self, dataset = None, params = None):
        """
        DESCRIPTION:
            Transforms the input dataset based on the fitted model.
        PARAMETERS:
            dataset:
                Required Argument.
                Specifies the input dataset to be transformed.
                Types: teradatamlspk DataFrame
            parms:
                Optional Argument.
                Specifies the optional param map that overrides embedded params
        RETURNS:
            teradatamlspk DataFrame
        Example:
            >>> from teradatamlspk.ml.feature import RegexTokenizer
            >>> TdRT = RegexTokenizer()
            >>> TdRT.transform(df)
        """
        if params is not None:
            for param, value in params.items():
                self._paramMap[param] = value

        tdml_df = dataset._data
        input_col = self.getinputCol()
        output_col = self.getoutputCol()
        
        # Check if the object is of type RegexTokenizer or Tokenizer.
        # If it is of type RegexTokenizer, get the values of the parameters.
        # Else, set the default values.
        from teradatamlspk.ml.feature import RegexTokenizer
        if isinstance(self, RegexTokenizer):
            minTokenLength = str(self.getminTokenLength())
            gaps = self.getGaps()
            lower_case = self.getToLowercase()
            pattern = self.getPattern()
        else:
            # Tokenizer converts the input string to lowercase and then splits it by white spaces.
            # So, the default values are set accordingly.
            minTokenLength, gaps, lower_case, pattern = '1', True, True, " "

        transformed_obj = NGramSplitter(data=tdml_df,
                                text_column=input_col,
                                n_gram_column = output_col,
                                grams=minTokenLength,
                                overlapping=gaps,
                                to_lower_case=lower_case,
                                delimiter=pattern,
                                reset = pattern)
        
        return DataFrame(transformed_obj.result.drop(columns=['n', 'frequency']))
    
class _SummarizerMethods(_GenericMethods):
    """ Summarizer statistics methods"""

    count = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.count())
    mean = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.mean())
    sum = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.sum())
    max = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.max())
    min = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.min())
    variance = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.var())
    std = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.std())
    numNonZeros = lambda self, col, weightCol = None: Column(tdml_column = case([(col._tdml_column != 0, 1)], else_=0).sum())
    normL1 = lambda self, col, weightCol = None: Column(tdml_column = col._tdml_column.abs().sum())
    normL2 = lambda self, col, weightCol = None: sqrt(sum(pow(col, 2)))

    def metrics(self, metrics):
        """
        DESCRIPTION:
            Returns the object of the class SummaryBuilder to compute metric on the column.
        PARAMETERS:
            metric:
                Required Argument.
                Specifies the metric to be calculated.
                Types: str
        RETURNS:
            teradatamlspk.ml.stat.SummaryBuilder
        Example:
            >>> from teradatamlspk.ml.feature import Summarizer
            >>> TdSum = Summarizer().metrics("count")
        """
        # Return the object of the class SummaryBuilder with the metric set.
        model_obj = _get_reference_class(self.__class__, "summary")()
        model_obj._metric = metrics
        return model_obj
    
    def summary(self, col, weightCol=None):
        """
        DESCRIPTION:
            Returns the summary of the column with the requested metric.
        PARAMETERS:
            col:
                Required Argument.
                Specifies the column for which the summary statistics are to be computed.
                Types: Column
        RETURNS:
            Column
        Example:
            >>> from teradatamlspk.ml.feature import Summarizer
            >>> TdSum = Summarizer().metrics("count")
            >>> TdSum.summary(df.col1)
        """
        # Dictionary of metrics and their corresponding functions.
        metric_func_dict = {
            "count": self.count,
            "mean": self.mean,
            "sum": self.sum,
            "max": self.max,
            "min": self.min,
            "variance": self.variance,
            "std": self.std,
            "non_zero_count": self.numNonZeros,
            "normL1": self.normL1,
            "normL2": self.normL2
        }
        metric_func = metric_func_dict.get(self._metric, None)
        return metric_func(col)

class _Metrics(_ModelSummaryMethods):

    def get_labels(self):
        return self.labels
    
    def get_label_count_df(self):
        label = self._spark_model_obj.getlabelCol()
        return self._data.select([label]).groupBy(label).count()
    
    def get_ytrue_ypred(self):
        return self._predicted_output.select(self._spark_model_obj.getlabelCol()), self._predicted_output.select(self._spark_model_obj.getpredictionCol())

    def get_weighted_average(self, metric):
        labels_list = self.get_labels()
        res_df = self.get_label_count_df()
        res_df_dict = res_df.to_pandas().to_dict()
        result = 0
        count_sum = 0
        for label, value in zip(labels_list, metric):
            if res_df_dict['count'][label] > 0:
                count = res_df_dict['count'][label]
                result += count * value
                count_sum += count
        return result / count_sum
    
    def fMeasureByLabel(self, beta=1.0):
        """Returns f-measure for each label (category)."""
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        opt = osml.f1_score(y_true=y_true_df._data, y_pred=y_pred_df._data, average=None, labels=self.get_labels())
        return opt.tolist()

    def weightedFMeasure(self, beta=1.0):
        """ Returns weighted averaged f-measure. """
        fMeasure = self.fMeasureByLabel()
        return self.get_weighted_average(fMeasure)

    @property
    def accuracy(self):
        """ Returns accuracy."""
        return (self.predictions[self.predictions[self._spark_model_obj.getlabelCol()] == self.predictions[self._spark_model_obj.getpredictionCol()]].count())/self.predictions.count()

    @property
    def areaUnderROC(self):
        """ Computes the area under the receiver operating characteristic (ROC) curve. """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        return (osml.roc_auc_score(y_true = y_true_df._data, y_score = y_pred_df._data))

    @property
    def fMeasureByThreshold(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6551
        raise NotImplementedError


    @property
    def falsePositiveRateByLabel(self):
        """ Returns false positive rate for each label (category). """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true = y_true_df._data, y_pred = y_pred_df._data)
        FP = confusion_matrix.sum(axis=0) - np.diag(confusion_matrix)
        FN = confusion_matrix.sum(axis=1) - np.diag(confusion_matrix)
        TP = np.diag(confusion_matrix)
        TN = confusion_matrix.sum() - (FP + FN + TP)
        return (FP / (FP + TN)).tolist()

    @property
    def labelCol(self):
        spark_model = self._spark_model_obj
        return spark_model.getOrDefault(spark_model.labelCol)

    @property
    def labels(self):
        labels_list = self._spark_model_obj._model.classes_.tolist()
        labels_list.sort()
        return labels_list

    @property
    def pr(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6551
        raise NotImplementedError

    @property
    def precisionByLabel(self):
        """ Returns precision for each label (category). """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true=y_true_df._data, y_pred=y_pred_df._data)
        TP = np.diag(confusion_matrix)
        FP = confusion_matrix.sum(axis=0) - np.diag(confusion_matrix)
        return (TP / (TP + FP)).tolist()

    @property
    def precisionByThreshold(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6551
        raise NotImplementedError

    @property
    def predictions(self):
        return self._predicted_output

    @property
    def recallByLabel(self):
        """ Returns recall for each label (category). """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true=y_true_df._data, y_pred=y_pred_df._data)
        TP = np.diag(confusion_matrix)
        FN = confusion_matrix.sum(axis=1) - np.diag(confusion_matrix)
        return (TP / (TP + FN)).tolist()

    @property
    def recallByThreshold(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6551
        raise NotImplementedError

    @property
    def roc(self):
        """ Returns the receiver operating characteristic (ROC) curve,
        which is a Dataframe having two fields (FPR, TPR). """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        data = []
        fpr, tpr, _ = osml.roc_curve(y_true = y_true_df._data, y_score = y_pred_df._data, pos_label=True)
        for FPR, TPR in zip(fpr, tpr):
            data.append([FPR, TPR])
        return pd.DataFrame(data, columns= ["FPR", "TPR"])

    @property
    def scoreCol(self):
        raise NotImplementedError

    @property
    def truePositiveRateByLabel(self):
        """ Returns true positive rate for each label (category). """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true=y_true_df._data, y_pred=y_pred_df._data)
        FN = confusion_matrix.sum(axis=1) - np.diag(confusion_matrix)
        TP = np.diag(confusion_matrix)
        return (TP/(TP+FN)).tolist()

    @property
    def weightedFalsePositiveRate(self):
        """ Returns weighted false positive rate. """
        FPR = self.falsePositiveRateByLabel
        return self.get_weighted_average(FPR)

    @property
    def weightedPrecision(self):
        """ Returns weighted averaged precision. """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true=y_true_df._data, y_pred=y_pred_df._data)
        FP = confusion_matrix.sum(axis=0) - np.diag(confusion_matrix)
        TP = np.diag(confusion_matrix)
        precision = TP / (TP + FP)
        return self.get_weighted_average(precision)

    @property
    def weightedRecall(self):
        """ Returns weighted averaged recall. """
        y_true_df , y_pred_df = self.get_ytrue_ypred()
        confusion_matrix = osml.confusion_matrix(y_true=y_true_df._data, y_pred=y_pred_df._data)
        TP = np.diag(confusion_matrix)
        FN = confusion_matrix.sum(axis=1) - np.diag(confusion_matrix)
        recall = TP / (TP + FN)
        return self.get_weighted_average(recall)

    @property
    def weightedTruePositiveRate(self):
        """ Returns weighted true positive rate. """
        return self.weightedRecall

class _RegressionMetrics(_ModelSummaryMethods):

    @property
    def coefficientStandardErrors(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        raise NotImplementedError

    @property
    def degreesOfFreedom(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        raise NotImplementedError

    @property
    def devianceResiduals(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        raise NotImplementedError

    @property
    def explainedVariance(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        return self._get_metric('EV')

    @property
    def meanSquaredError(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        return self._get_metric('MSE')

    @property
    def pValues(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6519.
        raise NotImplementedError

    @property
    def r2adj(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        return self._get_metric('AR2')

    @property
    def residuals(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6519.
        raise NotImplementedError

    @property
    def tValues(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6519.
        raise NotImplementedError

    @property
    def meanAbsoluteError(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6518.
        return self._get_metric('MAE')

    @property
    def r2(self):
        # TODO: To be implemented with https://teradata-pe.atlassian.net/browse/ELE-6519.
        return self._get_metric('R2')

    @property
    def rootMeanSquaredError(self):
        return self._get_metric('RMSE')

    def _populate_metrics(self):
        if not self._metrics:
            from teradataml import RegressionEvaluator
            data = self._predicted_output._data
            observation_column = self._spark_model_obj.getlabelCol()
            predicted_column = self._spark_model_obj.getpredictionCol()
            r = RegressionEvaluator(data=data,
                                    observation_column=observation_column,
                                    prediction_column=predicted_column,
                                    freedom_degrees=[1, 2],
                                    independent_features_num=2,
                                    metrics=['RMSE', 'R2', 'MAE', 'MSE', 'MSLE', 'MAPE', 'MPE', 'AR2', 'EV', 'ME', 'MPD'])
            rec = next(r.result.itertuples())._asdict()
            self._metrics = rec

    def _get_metric(self, metric):
        self._populate_metrics()
        return self._metrics[metric]

def chisquaretest(dataset, featureCol, Labelcol, flatten=True):
    result_ = valib.ChiSquareTest(data = dataset._data,
                                  first_columns = Labelcol,
                                  second_columns = featureCol,
                                  style = "chisq")
    params_ = dict([("featureIndex", case({x:i for i,x in enumerate(featureCol)}, value=result_.result.column2)),
                    ("pValue", result_.result.ChiPValue),
                    ("degreesOfFreedom", result_.result.DF),
                    ("statistic", result_.result.Chisq)])
    return DataFrame(result_.result.assign(drop_columns = True, **params_))


class _OneHotEncoder(_FeatureMethods):
    def fit(self, dataset, params=None):
        self._train_data_set = dataset
        osml_func = SPARK_TO_OSML[self.__class__.__name__]["osml_func"]
        osml_args = {}
        # Check if user passed both inputcol and inputCols raise error.
        if self.getInputCol() is not None and self.getInputCols() is not None:
            raise Exception("Exactly one of inputCol, inputCols Params to be set, but both are set.")

        # If user pass inputcol store it else store inpucols
        if self.getInputCol():
            _input_column = [self.getInputCol()]
            _output_column = self.getOutputCol()
            self.setInputCol(self.getInputCol())
        else:
            _input_column = self.getInputCols()
            _output_column = self.getOutputCols()
            self.setinputCols(self.getInputCols())

        df_ = dataset._data.count(distinct=True)
        category_counts = [df_.select('count_'+col).squeeze() for col in _input_column]
        osml_args.update(
            {"data": dataset._data, "target_column": _input_column, "is_input_dense": True, "approach": "auto",
             "category_counts": category_counts, "other_column": "other"})

        self.osml_fitted_model = osml_func(**osml_args)
        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        model_obj._spark_model_obj = self
        model_obj.categorySizes = category_counts

        from teradatamlspk.ml.constants import SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES
        model_attributes = SPARK_ATTRIBUTES_TO_OSML_ATTRIBUTES.get(self.__class__.__name__, {})
        for spark_model_attribute, osml_model_attribute in model_attributes.items():
            setattr(model_obj, spark_model_attribute,
                    getattr(self.osml_fitted_model, osml_model_attribute) if osml_model_attribute else None)
        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        tdml_df = self._model.transform(data=dataset._data, is_input_dense=True)
        return DataFrame(tdml_df.result)

class _UnivariateFeatureSelector(_FeatureMethods):

    def fit(self, dataset, params=None):
        osml_func = {'numTopFeatures': osml.SelectKBest,
                     'percentile': osml.SelectPercentile,
                     'fpr': osml.SelectFpr,
                     'fdr': osml.SelectFdr,
                     'fwe': osml.SelectFwe}
        if self.getFeatureType() == 'categorical' and self.getLabelType() == 'categorical':
            type_ = osml.chi2
        elif self.getFeatureType() == 'continuous' and self.getLabelType() == 'categorical':
            type_ = osml.f_classif
        elif self.getFeatureType() == 'continuous' and self.getLabelType() == 'continuous':
            type_ = osml.f_regression

        selection_threshold = self.getSelectionThreshold()
        if self.getFeatureType() == 'continuous' and self.getLabelType() == 'categorical':
            sklearn_ufs = osml_func[self.getSelectionMode()]()
            if self.getSelectionMode() == 'numTopFeatures':
                sklearn_ufs.set_params(k=selection_threshold)
            elif self.getSelectionMode() == 'percentile':
                sklearn_ufs.set_params(percentile=selection_threshold)
            elif self.getSelectionMode() in ['fpr', 'fdr', 'fwe']:
                sklearn_ufs.set_params(alpha=selection_threshold)
        else:
            if selection_threshold:
                sklearn_ufs = osml_func[self.getSelectionMode()](type_, selection_threshold)
            else:
                sklearn_ufs = osml_func[self.getSelectionMode()](type_)

        self._train_data_set = dataset
        feature_columns = self.getFeaturesCol()
        self.setFeaturesCol(feature_columns)
        label_column = self.getLabelCol()
        self.setLabelCol(label_column)
        output_column = self.getOutputCol()
        X = self._train_data_set._data.select(feature_columns)
        Y = self._train_data_set._data.select(label_column)

        self.osml_fitted_model = sklearn_ufs.fit(X, Y)

        model_obj = _get_reference_class(self.__class__)()
        model_obj._model = self.osml_fitted_model

        # Store the reference of the actual model
        model_obj._spark_model_obj = self
        return model_obj

    def transform(self, dataset):
        from teradatamlspk.sql.dataframe import DataFrame
        X = dataset._data.select(self.getFeaturesCol())
        tdml_df = self._model.transform(X)
        return DataFrame(tdml_df)
