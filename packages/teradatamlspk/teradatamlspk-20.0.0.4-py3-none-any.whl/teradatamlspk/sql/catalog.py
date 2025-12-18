from teradataml.context.context import _get_current_databasename
from teradataml import db_drop_view, get_connection, db_list_tables, db_drop_table


def _notAvailable(self, *args, **kwargs):
    raise NotImplementedError(Catalog._exp_msg)


def _dropGlobalTempView(self, viewName):
    try:
        # Check if it is a view or table.
        pdf_t = db_list_tables(object_type='table')
        table_names = list(pdf_t['TableName'].values)
        if viewName in table_names:
            db_drop_table(viewName)
            return True

        # Else, it must be a view.
        db_drop_view(viewName)
        return True
    except Exception as e:
        print(str(e))
        return False

class Catalog:
    _exp_msg = "API is not available in Teradata Vantage."
    cacheTable = lambda *args, **kwargs: None
    clearCache = lambda *args, **kwargs: None
    currentCatalog = lambda self: "teradata_catalog"
    currentDatabase = lambda self: _get_current_databasename()
    databaseExists = lambda self, dbName: dbName in get_connection().dialect._get_database_names(
        get_connection(), self.currentDatabase())
    dropTempView = _dropGlobalTempView
    dropGlobalTempView = _dropGlobalTempView
    getFunction = _notAvailable
    getTable = _notAvailable
    listCatalogs = _notAvailable
    listColumns = _notAvailable
    isCached = lambda *args, **kwargs: False
    listDatabases = _notAvailable
    listFunctions = _notAvailable
    listTables = _notAvailable
    createExternalTable = _notAvailable
    createTable = _notAvailable
    functionExists = _notAvailable
    getDatabase = _notAvailable
    recoverPartitions = lambda *args, **kwargs: None
    refreshByPath = lambda *args, **kwargs: None
    refreshTable = lambda *args, **kwargs: None
    registerFunction = _notAvailable
    setCurrentCatalog = lambda *args, **kwargs: None
    setCurrentDatabase = lambda *args, **kwargs: None
    tableExists = lambda self, tableName, dbName=None: tableName in db_list_tables(schema_name=dbName)['TableName'].values
    uncacheTable = lambda self, tableName: None
