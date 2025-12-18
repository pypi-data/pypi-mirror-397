from teradataml.utils.utils import execute_sql
from teradataml.dbutils.dbutils import set_session_param, unset_session_param
from teradatamlspk.sql.utils import _pytz_to_teradataml_string_mapper
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.common.constants import ArrayDefaults


class TeradataConf:
    def __init__(self):
        self._config = {}

    def contains(self, key):
        return key in self._config

    def getAll(self):
        return [(k, v) for k,v in self._config.items()]

    def set(self, key, value):
        if any(key.upper() == e.name for e in ArrayDefaults):
            _InternalBuffer.add(**{key: value})
        self._config[key] = value
        return self
   
    def setAll(self, pairs):
        # Convert pairs to dict for validation
        config_dict = dict(pairs)
        for key, value in config_dict.items():
            self.set(key, value)
        return self

    def get(self, key, defaultValue = None):
        # Get config as a top-level key in the buffer only
        value = _InternalBuffer.get(key)
        if value is not None:
            return value
        return self._config.get(key, defaultValue)

    def setAppName(self, value):
        return self

    def setExecutorEnv(self, key=None, value=None, pairs=None):
        return self

    def setIfMissing(self, key, value):
        if key not in self._config:
            self._config[key] = value

        return self

    def setMaster(self, value):
        return self

    def setSparkHome(self, value):
        return self

    def toDebugString(self):
        return "\n".join(["{}={}".format(k, v) for k,v in self._config.items()])

    def unset(self, key):
        if key in self._config:
            self._config.pop(key)
        if any(key == e.name for e in ArrayDefaults):
            _InternalBuffer.remove_key(key)

class RuntimeConfig(TeradataConf):
    isModifiable = lambda self: False

    def set(self, key, value):
        if key == 'spark.sql.session.timeZone':
            set_session_param('timezone', "\'{}\'".format(_pytz_to_teradataml_string_mapper(value)) if " " not in value else f"'{value}'")
        # Pass array configuration to parent class
        else:
            if any(key.upper() == e.name for e in ArrayDefaults):
                _InternalBuffer.add(**{key: value})
            self._config[key] = value

    def unset(self, key):
        """
        DESCRIPTION:
            Remove a runtime configuration key.
        
        PARAMETERS:
            key: 
                Required Argument.
                The configuration key to remove.
                Type: str

        RETURNS:
            None
        """
        if key == 'spark.sql.session.timeZone':
            unset_session_param("timezone")
        # Pass array configuration to parent class
        else:
            super().unset(key)
