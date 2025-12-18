import time
from teradataml import configure
from teradataml.context.context import create_context, _get_user, remove_context, get_context
from teradatamlspk.conf import TeradataConf
from teradatamlspk.sql.dataframe import DataFrame



class TeradataContext:
    """ Entry point to connect Teradata Vantage. """
    PACKAGE_EXTENSIONS = ""
    applicationId = 0
    defaultMinPartitions = None
    defaultParallelism = None
    resources = None
    uiWebUrl = ""

    @property
    def version(self):
        return configure.database_version

    @property
    def startTime(self):
        return self.__time

    def __init__(self, **kwargs):
        self.__time = None
        context = get_context()
        if not context:
            create_context(**kwargs)
            self.__time = time.time()

    def accumulator(self, value, accum_param):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def addFile(self, path, recursive=False):
        return

    def addPyFile(self, path):
        return

    def binaryFiles(self, path, minPartitions=None):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def binaryRecords(self, path, recordLength):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def broadcast(self, value):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def cancelAllJobs(self):
        return

    def cancelJobGroup(self, groupId):
        return

    def dump_profiles(self, path):
        return

    def emptyRDD(self):
        return

    def getCheckpointDir(self):
        return

    def getConf(self):
        conf = TeradataConf()
        return conf

    def getLocalProperty(self, key):
        return

    @classmethod
    def getOrCreate(cls, **kwargs):
        create_context(**kwargs)
        return cls()

    def hadoopFile(self, path, inputFormatClass, keyClass, valueClass, keyConverter=None,
                   valueConverter=None, conf=None, batchSize=0):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def hadoopRDD(self, inputFormatClass, keyClass, valueClass, keyConverter=None,
                  valueConverter=None, conf=None, batchSize=0):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def newAPIHadoopFile(self, path, inputFormatClass, keyClass, valueClass, keyConverter=None,
                         valueConverter=None, conf=None, batchSize=0):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def newAPIHadoopRDD(self, inputFormatClass, keyClass, valueClass, keyConverter=None,
                        valueConverter=None, conf=None, batchSize=0):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def parallelize(self, c, numSlices=None):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def pickleFile(self, name, minPartitions=None):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def range(self, start, end=None, step=1, numPartitions = None):
        """ Creates a DataFrame with a range of numbers. """
        from teradataml import td_range
        return DataFrame(td_range(start, end, step))

    def runJob(self, rdd, partitionFunc, partitions=None, allowLocal=False):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def sequenceFile(self, path, keyClass=None, valueClass=None, keyConverter=None,
                     valueConverter=None, minSplits=None, batchSize=0):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def setCheckpointDir(self, dirName):
        return

    def setJobDescription(self, value):
        return

    def setJobGroup(self, groupId, description, interruptOnCancel=False):
        return

    def setLocalProperty(self, key, value):
        return

    def setLogLevel(self, logLevel):
        return

    @classmethod
    def setSystemProperty(cls, key, value):
        return

    def show_profiles(self):
        return

    def teradataUser(self):
        return _get_user()

    def statusTracker(self):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def stop(self):
        remove_context()

    def textFile(self, name, minPartitions=None, use_unicode=True):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def union(self, rdds):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

    def wholeTextFiles(self, path, minPartitions=None, use_unicode=True):
        raise NotImplemented("Not Applicable for Teradata Vantage.")

