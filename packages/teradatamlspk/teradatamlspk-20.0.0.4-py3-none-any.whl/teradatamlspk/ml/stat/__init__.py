from teradatamlspk.ml.util import chisquaretest, _SummarizerMethods

ChiSquareTest = type("ChiSquareTest", (), {"test": staticmethod(chisquaretest)})

Summarizer = type("Summarizer", (_SummarizerMethods, ), {})
SummaryBuilder = type("SummaryBuilder", (_SummarizerMethods, ), {})