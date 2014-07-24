"""
    Defines a handler for the Sphinx 'build-finished' event.
    If the builder is doctest then it post-processes the
    output file to produce an XUnit-style XML file that can be
    more easily parse by CI servers such as Jenkins.

    Output file structure
    ~~~~~~~~~~~~~~~~~~~~~

    The following outcomes are possible for a given
    document:
     - all tests pass;
     - all tests fail;
     - and some test pass and some fail.

    Below are examples of the output for each of the above
    outcomes, given a document named 'FooDoc' in a
    directory 'bar'relative to the documentation root.

    - All Passed:
     ============

    Document: bar/FooDoc
    --------------------
    1 items passed all tests:
       2 tests in default
       1 tests in ExForFoo
    2 tests in 1 items.
    2 passed and 0 failed.
    Test passed.

    - All Failed:
     ============

    Document: bar/FooDoc
    --------------------
    **********************************************************************
    File "bar/FooDoc.rst", line 127, in Ex2
    Failed example:
        print "Multi-line failed"
        print "test"
    Expected:
        No match
    Got:
        Multi-line failed
        test
    **********************************************************************
    File "bar/FooDoc.rst", line 111, in Ex1
    Failed example:
        print "Single line failed test"
    Expected:
        No match
    Got:
        Single line failed test
    **********************************************************************
    2 items had failures:
       1 of   1 in Ex1
       1 of   1 in Ex2
    2 tests in 2 items.
    0 passed and 2 failed.
    ***Test Failed*** 2 failures.


    - Some pass some fail:
      ====================

    Document: bar/FooDoc
    --------------------
    **********************************************************************
    File "bar/FooDoc.rst", line 127, in default
    Failed example:
        print "A failed test"
    Expected:
        Not a success
    Got:
        A failed test
    **********************************************************************
    File "bar/FooDoc.rst", line 143, in Ex1
    Failed example:
        print "Second failed test"
    Expected:
        Not a success again
    Got:
        Second failed test
    **********************************************************************
    2 items had failures:
       1 of   1 in Ex1
       1 of   2 in default
    3 tests in 2 items.
    1 passed and 2 failed.
    ***Test Failed*** 2 failures.

"""
import re

# Name of file produced by doctest target. It is assumed that it is created
# in app.outdir
DOCTEST_OUTPUT = "output.txt"
# Name of output file that the resultant XUnit output is saved
# @todo make this a configuration variable
XUNIT_OUTPUT = "doctest.xml"

#-------------------------------------------------------------------------------
# Defining text
DOCTEST_DOCUMENT_BEGIN = "Document:"
DOCTEST_SUMMARY_TITLE = "Doctest summary"

# Regexes
ALLPASS_SUMMARY_RE = re.compile(r"^(\d+) items passed all tests:$")
ALLPASS_TEST_NAMES_RE = re.compile(r"^\s+(\d+) tests in (.+)$")

#-------------------------------------------------------------------------------
class TestSuite(object):

    def __init__(self, fullname, cases):
        self.fullname = fullname
        self.testcases = cases

#-------------------------------------------------------------------------------
class TestCase(object):

    Success = 0
    Failed = 1

    def __init__(self, name, status):
        self.name = name
        self.status = status

#-------------------------------------------------------------------------------
class DocTestOutputParser(object):
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
                    suites.append(self.__parse_suite(document_txt))
                document_txt = [line]
                in_doc = True
                continue
            if line.startswith(DOCTEST_SUMMARY_TITLE):
                in_doc = False
            if in_doc and line != "":
                document_txt.append(line)
        # endif
        return suites

    def __parse_suite(self, result_txt):
        """
        Create a TestSuite object for this document

        Args:
          result_txt (str): String containing doctest output for
                            document
        Returns:
          str: Fullname of test
        """
        fullname = self.__extract_fullname(result_txt[0])
        if not result_txt[1].startswith("-"):
            raise ValueError("Invalid second line of output: '%s'. "\
                             "Expected a title underline."
                             % result_txt[1])

        result_txt = result_txt[2:] # trim of top two lines
        if result_txt[0].startswith("*"):
            print "TODO: Failure cases"
            testcases = []
        else:
            # assume all passed
            testcases = self.__parse_success(result_txt)

        return TestSuite(fullname, testcases)

    def __extract_fullname(self, first_line):
        """
        Extract the document name from the line of text.

        Args:
          first_line (str): Line to test for title
        """
        if not first_line.startswith(DOCTEST_DOCUMENT_BEGIN):
            raise ValueError("First line of output text should be a line "
                             "beginning '%s'" % DOCTEST_DOCUMENT_BEGIN)
        return first_line.replace(DOCTEST_DOCUMENT_BEGIN, "").strip()

    def __parse_success(self, result_txt):
        """
        Parse text for success cases for a single document

        Args:
          result_txt (str): String containing doctest output for
                            document
        """
        match = ALLPASS_SUMMARY_RE.match(result_txt[0])
        if not match:
            raise ValueError("All passed line incorrect: '%s'"
                             % result_txt[0])
        nitems = int(match.group(1))
        cases = []
        for line in result_txt[1:1+nitems]:
            match = ALLPASS_TEST_NAMES_RE.match(line)
            if not match:
                raise ValueError("Unexpected information line in "
                                 "all pass case: %s" % line)
            ntests, name = int(match.group(1)), match.group(2)
            for idx in range(ntests):
                cases.append(TestCase(name, TestCase.Success))
        #endfor
        return cases

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
    doctests = DocTestOutputParser(doctest_file)
    #xunit_file = os.path.join(app.builder.outdir, XUNIT_OUTPUT)
    #doctests.to_xunit()

#-------------------------------------------------------------------------------

def setup(app):
    """
    Connect the 'build-finished' event to the handler function.
    """
    app.connect('build-finished', doctest_to_xunit)
