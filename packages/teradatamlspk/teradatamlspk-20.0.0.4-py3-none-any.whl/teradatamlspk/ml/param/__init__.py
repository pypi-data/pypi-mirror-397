#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import copy
from teradatamlspk.ml.util import Identifiable
from typing import (
    Any,
    Generic,
    Optional,
    TypeVar,
    Union,
)
from teradatamlspk.ml.constants import ARGUMENT_MAPPER
from teradataml.utils.internal_buffer import _InternalBuffer

T = TypeVar("T")
P = TypeVar("P", bound="Params")

class Param(Generic[T]):
    """
    A param with self-contained documentation.

    .. versionadded:: 1.3.0
    """

    def __init__(
        self,
        parent,
        name,
        doc,
        typeConverter=None,
    ):
        if not isinstance(parent, Identifiable):
            raise TypeError("Parent must be an Identifiable but got type %s." % type(parent))
        self.parent = parent.uid
        self.name = str(name)
        self.doc = str(doc)

        # Add the entry in InternalBuffer to disable the checking of Python version
        # for OSML functions.
        _InternalBuffer.add(_check_py_version=False)

    def __str__(self) -> str:
        return str(self.parent) + "__" + self.name

    def __repr__(self) -> str:
        return "Param(parent=%r, name=%r, doc=%r)" % (self.parent, self.name, self.doc)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Param):
            return self.parent == other.parent and self.name == other.name
        else:
            return False


class Params(Identifiable):
    """
    Components that take parameters. This also provides an internal
    param map to store parameter values attached to the instance.

    .. versionadded:: 1.3.0
    """

    def __init__(self, **kwargs) -> None:

        self._kwargs = kwargs
        params_ = {}
        for param in ARGUMENT_MAPPER[self.__class__.__name__]:
            params_[param.name] = kwargs.get(param.name, param.default_value)

        super(Params, self).__init__()
        #: internal param map for user-supplied values param map
        self._paramMap = {}

        #: internal param map for default values
        self._defaultParamMap = {}

        #: value returned by :py:func:`params`
        self._params = None

        self.args_ = params_
        for reference_param in ARGUMENT_MAPPER.get(self.__class__.__name__, []):

            # Check default value. If default value is same as user passed value,
            # push it to _defaultParamMap by defdault. Update param map if the value
            # is different from default value.
            param = Param(parent=self, name=reference_param.name, doc="")
            self._defaultParamMap[param] = reference_param.default_value
            if self.args_[param.name] != reference_param.default_value:
                self._paramMap[param] = self.args_[param.name]

    @property
    def params(self):
        """
        Returns all params ordered by name. The default implementation
        uses :py:func:`dir` to get all attributes of type
        :py:class:`Param`.
        """
        return list(self._defaultParamMap.keys())

    def explainParam(self, param: Union[str, Param]) -> str:
        """
        Explains a single param and returns its name, doc, and optional
        default value and user-supplied value in a string.
        """
        param = self._resolveParam(param)
        values = []
        if self.isDefined(param):
            if param in self._defaultParamMap:
                values.append("default: %s" % self._defaultParamMap[param])
            if param in self._paramMap:
                values.append("current: %s" % self._paramMap[param])
        else:
            values.append("undefined")
        valueStr = "(" + ", ".join(values) + ")"
        return "%s: %s %s" % (param.name, param.doc, valueStr)

    def explainParams(self) -> str:
        """
        Returns the documentation of all params with their optionally
        default values and user-supplied values.
        """
        return "\n".join([self.explainParam(param) for param in self.params])

    def getParam(self, paramName: str) -> Param:
        """
        Gets a param by its name.
        """
        param = getattr(self, paramName)
        if isinstance(param, Param):
            return param
        else:
            raise ValueError("Cannot find param with name %s." % paramName)

    def isSet(self, param: Union[str, Param[Any]]) -> bool:
        """
        Checks whether a param is explicitly set by user.
        """
        param = self._resolveParam(param)
        return param in self._paramMap

    def hasDefault(self, param: Union[str, Param[Any]]) -> bool:
        """
        Checks whether a param has a default value.
        """
        param = self._resolveParam(param)
        return param in self._defaultParamMap

    def isDefined(self, param: Union[str, Param[Any]]) -> bool:
        """
        Checks whether a param is explicitly set by user or has
        a default value.
        """
        return self.isSet(param) or self.hasDefault(param)

    def hasParam(self, paramName: str) -> bool:
        """
        Tests whether this instance contains a param with a given
        (string) name.
        """
        if isinstance(paramName, str):
            p = getattr(self, paramName, None)
            return isinstance(p, Param)
        else:
            raise TypeError("hasParam(): paramName must be a string")

    def getOrDefault(self, param: Union[str, Param[T]]) -> Union[Any, T]:

        """
        Gets the value of a param in the user-supplied param map or its
        default value. Raises an error if neither is set.
        """
        param = self._resolveParam(param)
        if param in self._paramMap:
            return self._paramMap[param]
        else:
            return self._defaultParamMap[param]

    def extractParamMap(self, extra: Optional["ParamMap"] = None) -> "ParamMap":
        """
        Extracts the embedded default param values and user-supplied
        values, and then merges them with extra values from input into
        a flat param map, where the latter value is used if there exist
        conflicts, i.e., with ordering: default param values <
        user-supplied values < extra.

        Parameters
        ----------
        extra : dict, optional
            extra param values

        Returns
        -------
        dict
            merged param map
        """
        if extra is None:
            extra = dict()
        paramMap = self._defaultParamMap.copy()
        paramMap.update(self._paramMap)
        paramMap.update(extra)
        return paramMap

    def set(self, param: Param, value: Any) -> None:
        """
        Sets a parameter in the embedded param map.
        """
        self._shouldOwn(param)
        self._paramMap[param] = value

    def _shouldOwn(self, param: Param) -> None:
        """
        Validates that the input param belongs to this Params instance.
        """
        if not (self.uid == param.parent and self.hasParam(param.name)):
            raise ValueError("Param %r does not belong to %r." % (param, self))

    def _resolveParam(self, param: Union[str, Param]) -> Param:
        """
        Resolves a param and validates the ownership.

        Parameters
        ----------
        param : str or :py:class:`Param`
            param name or the param instance, which must
            belong to this Params instance

        Returns
        -------
        :py:class:`Param`
            resolved param instance
        """
        if isinstance(param, Param):
            self._shouldOwn(param)
            return param
        elif isinstance(param, str):
            return self.getParam(param)
        else:
            raise TypeError("Cannot resolve %r as a param." % param)

    def _testOwnParam(self, param_parent: str, param_name: str) -> bool:
        """
        Test the ownership. Return True or False
        """
        return self.uid == param_parent and self.hasParam(param_name)

    @staticmethod
    def _dummy() -> "Params":
        """
        Returns a dummy Params instance used as a placeholder to
        generate docs.
        """
        dummy = Params()
        dummy.uid = "undefined"
        return dummy

    def _set(self: P, **kwargs: Any) -> P:
        """
        Sets user-supplied params.
        """
        for param, value in kwargs.items():
            p = getattr(self, param)
            self._paramMap[p] = value
        return self

    def clear(self, param: Param) -> None:
        """
        Clears a param from the param map if it has been explicitly set.
        """
        if self.isSet(param):
            del self._paramMap[param]

    def _setDefault(self: P, **kwargs: Any) -> P:
        """
        Sets default params.
        """
        for param, value in kwargs.items():
            p = getattr(self, param)
            self._defaultParamMap[p] = value
        return self

    def _copyValues(self, to: P, extra: Optional["ParamMap"] = None) -> P:
        """
        Copies param values from this instance to another instance for
        params shared by them.

        Parameters
        ----------
        to : :py:class:`Params`
            the target instance
        extra : dict, optional
            extra params to be copied

        Returns
        -------
        :py:class:`Params`
            the target instance with param values copied
        """
        paramMap = self._paramMap.copy()
        if isinstance(extra, dict):
            for param, value in extra.items():
                if isinstance(param, Param):
                    paramMap[param] = value
                else:
                    raise TypeError(
                        "Expecting a valid instance of Param, but received: {}".format(param)
                    )
        elif extra is not None:
            raise TypeError(
                "Expecting a dict, but received an object of type {}.".format(type(extra))
            )
        for param in self.params:
            # copy default params
            if param in self._defaultParamMap and to.hasParam(param.name):
                to._defaultParamMap[to.getParam(param.name)] = self._defaultParamMap[param]
            # copy explicitly set params
            if param in paramMap and to.hasParam(param.name):
                to._set(**{param.name: paramMap[param]})
        return to

    def _resetUid(self: P, newUid: Any) -> P:
        """
        Changes the uid of this instance. This updates both
        the stored uid and the parent uid of params and param maps.
        This is used by persistence (loading).

        Parameters
        ----------
        newUid
            new uid to use, which is converted to unicode

        Returns
        -------
        :py:class:`Params`
            same instance, but with the uid and Param.parent values
            updated, including within param maps
        """
        newUid = str(newUid)
        self.uid = newUid
        newDefaultParamMap = dict()
        newParamMap = dict()
        for param in self.params:
            newParam = copy.copy(param)
            newParam.parent = newUid
            if param in self._defaultParamMap:
                newDefaultParamMap[newParam] = self._defaultParamMap[param]
            if param in self._paramMap:
                newParamMap[newParam] = self._paramMap[param]
            param.parent = newUid
        self._defaultParamMap = newDefaultParamMap
        self._paramMap = newParamMap
        return self


    def __getattr__(self, item):
        for param in self._paramMap:
            if param.name == item:
                return param

        for param in self._defaultParamMap:
            if param.name == item:
                return param

        # Getters.
        _param_name = str(item).lstrip("get")
        _param_name = _param_name[0].lower() + _param_name[1:]
        if _param_name in self.args_:
            return lambda : self.getOrDefault(getattr(self, _param_name))

        # Setters.
        _param_name = str(item).lstrip("set")
        _param_name = _param_name[0].lower() + _param_name[1:]
        if _param_name in self.args_:
            return self._setter(_param_name)

        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'.")

    def model_getattr(self, item):
        """
        DESCRIPTION:
            Function to get or set the attributes of the Spark model object.
        PARAMETERS:
            item:
                Required Argument.
                Specifies the attribute to be retrieved from the Spark model object.
                Types: str
        RETURNS:
            Spark model object.
        RAISES:
            AttributeError: If the attribute is not present in the Spark model object.
        Example:
            >>> Params.model_getattr(StandardScalerModel, std)
        """
        # Check if the attribute is present in the Spark model object
        if hasattr(self._spark_model_obj, item):
            return getattr(self._spark_model_obj, item)

        # If not, raise an AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'.")
        
    def _setter(self, param_name):
        def _param_setter(value):
            param = getattr(self, param_name)
            self._paramMap[param] = value
            return self
        return _param_setter

    def setParams(self, **kwargs):
        for key, value in kwargs.items():
            self._paramMap[getattr(self, key)] = value
