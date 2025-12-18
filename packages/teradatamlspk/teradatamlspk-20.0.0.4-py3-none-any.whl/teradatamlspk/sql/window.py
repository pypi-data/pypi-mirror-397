# ##################################################################
#
# Copyright 2023 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Pradeep Garre(pradeep.garre@teradata.com)
# Secondary Owner: Adithya Avvaru(adithya.avvaru@teradata.com)
#
#
# Version: 1.0
#
# ##################################################################
class WindowSpec:
    """
    Utility functions for defining window in DataFrames.
    """
    def __init__(self):
        self._params = {
            "window_start_point": None,
            "window_end_point": None,
            "partition_columns": None,
            "order_columns": None
        }

    def orderBy(self, *cols):
        window = WindowSpec()
        window._params.update(self._params)
        window._params["order_columns"] = list(cols)
        return window

    def partitionBy(self, *cols):
        window = WindowSpec()
        window._params.update(self._params)
        window._params["partition_columns"] = list(cols)
        return window

    def rowsBetween(self, start, end):
        window = WindowSpec()
        window._params.update(self._params)
        window._params["window_start_point"] = start
        window._params["window_end_point"] = end
        return window

    def rangeBetween(self, start, end):
        return self.rowsBetween(start, end)

    def get_params(self):
        _params = {**self._params}

        # PySpark by default generates RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW if
        # window starting point and ending point is not defined. However, teradataml
        # generates it as RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING.
        # Hence convert it.
        if _params["window_start_point"] is None and _params["window_end_point"] is None:
            _params["window_end_point"] = 0
        return _params


class Window:
    """
    A window specification that defines the partitioning, ordering,
    and frame boundaries.

    Use the static methods in :class:`Window` to create a :class:`WindowSpec`.
    """
    unboundedPreceding = None

    unboundedFollowing = None

    currentRow = 0

    @staticmethod
    def partitionBy(*cols):
        window = WindowSpec()
        window._params["partition_columns"] = list(cols)
        return window

    @staticmethod
    def orderBy(*cols):
        window = WindowSpec()
        window._params["order_columns"] = list(cols)
        return window

    @staticmethod
    def rowsBetween(start, end):
        window = WindowSpec()
        window._params["window_start_point"] = start
        window._params["window_end_point"] = end
        return window

    @staticmethod
    def rangeBetween(start, end):
        return Window.rowsBetween(start, end)
