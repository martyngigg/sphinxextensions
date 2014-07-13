"""
    Defines a handler for the Sphinx 'build-finished' event.
    If the builder is doctest then it post-processes the 
    output file to produce an XUnit-style XML file that can be
    more easily parse by CI servers such as Jenkins.
"""
# Name of file produced by doctest target. It is assumed that it is created
# in app.outdir
DOCTEST_OUTPUT = "output.txt"
# Name of output file that the resultant XUnit output is saved
XUNIT_OUTPUT = "doctest.xml"

DOCTEST_DOCUMENT_BEGIN = "Document:"
DOCTEST_SUMMARY_TITLE = "Doctest summary"

TESTSUITE_SUMMARY_RE = "\d items passed all tests:"

#-------------------------------------------------------------------------------
class TestSuite(object):

    

    def __init__(self, result_txt):
        """
        Initialize the object with the ASCII output text for a single
        document
        """
        first_line = result_txt[0]
        if not first_line.startswith(DOCTEST_DOCUMENT_BEGIN):
            raise ValueError("First line of output text should be a line "
                             "beginning '%s'" % DOCTEST_DOCUMENT_BEGIN)
        self.fullname = first_line.replace(DOCTEST_DOCUMENT_BEGIN, "").strip()
        
        
#-------------------------------------------------------------------------------
class DocTestOutput(object):
    """
    Process a doctest output file and convert it
    to a different format
    """
    
    def __init__(self, filename):
        with open(filename,'r') as result_file:
            self.testsuites = self.__parse(result_file)

    def __parse(self, result_file):
        """
        Parse a doctest output file and produce a set
        of TestSuite objects that describe the results
        of the all tests on a single document

        Arguments:
          result_file (File): File-like object

        Returns:
          list: List of TestSuite objects
        """
        in_doc = False
        document_txt = []
        suites = []
        for line in result_file:
            if line.startswith(DOCTEST_DOCUMENT_BEGIN):
                # parse previous results
                if document_txt:
                    suites.append(TestSuite(document_txt))
                document_txt = [line]
                in_doc = True
            if line.startswith(DOCTEST_SUMMARY_TITLE):
                in_doc = False
            if in_doc and line != "":
                document_txt.append(line)                    

        return suites
    
#-------------------------------------------------------------------------------

def doctest_to_xunit(app, exception):
    """
    If the runner was 'doctest'then parse the "output.txt" 
    file and produce an XUnit-style XML file, otherwise it does
    nothing.
    
    Arguments:
      app (Sphinx.application): Sphinx application object
      exception: (Exception): If an exception was raised then it is given here
    """
    if app.builder.name != "doctest":
        return
    import os

    doctest_file = os.path.join(app.builder.outdir, DOCTEST_OUTPUT)
    doctests = DocTestOutput(doctest_file)
    #xunit_file = os.path.join(app.builder.outdir, XUNIT_OUTPUT)
    #doctests.to_xunit()

#-------------------------------------------------------------------------------

def setup(app):
    """
    Connect the 'build-finished' event to the handler function.
    """
    app.connect('build-finished', doctest_to_xunit)
