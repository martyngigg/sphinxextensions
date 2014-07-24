"""
    Defines a handler for the Sphinx 'build-finished' event.
    If the builder is doctest then it post-processes the
    output file to produce an XUnit-style XML file that can be
    more easily parse by CI servers such as Jenkins.
"""
# -------------- Output file structure ------------------
# The following outcomes are possible for a given
# document:
#  - all tests pass;
#  - all tests fail;
#  - and some test pass and some fail.
#
# Below are examples of the output for each of the above
# outcomes, given a document named 'FooDoc' in a
# directory 'bar'relative to the documentation root.
#
# - All Passed:
#  ============
#
# Document: bar/FooDoc
# --------------------
# 1 items passed all tests:
#    2 tests in default
#    1 tests in ExForFoo
# 2 tests in 1 items.
# 2 passed and 0 failed.
# Test passed.
#
# - All Failed:
#  ============
#
# Document: bar/FooDoc
# --------------------
# **********************************************************************
# File "bar/FooDoc.rst", line 127, in Ex2
# Failed example:
#     print "Multi-line failed"
#     print "test"
# Expected:
#     No match
# Got:
#     Multi-line failed
#     test
# **********************************************************************
# File "bar/FooDoc.rst", line 111, in Ex1
# Failed example:
#     print "Single line failed test"
# Expected:
#     No match
# Got:
#     Single line failed test
# **********************************************************************
# 2 items had failures:
#    1 of   1 in Ex1
#    1 of   1 in Ex2
# 2 tests in 2 items.
# 0 passed and 2 failed.
# ***Test Failed*** 2 failures.
#
#
# - Some pass some fail:
#   ====================
#
# Document: bar/FooDoc
# --------------------
# **********************************************************************
# File "bar/FooDoc.rst", line 127, in default
# Failed example:
#     print "A failed test"
# Expected:
#     Not a success
# Got:
#     A failed test
# **********************************************************************
# File "bar/FooDoc.rst", line 143, in Ex1
# Failed example:
#     print "Second failed test"
# Expected:
#     Not a success again
# Got:
#     Second failed test
# **********************************************************************
# 2 items had failures:
#    1 of   1 in Ex1
#    1 of   2 in default
# 3 tests in 2 items.
# 1 passed and 2 failed.
# ***Test Failed*** 2 failures.
#

#-------------------------------------------------------------------------------

# Name of file produced by doctest target. It is assumed that it is created
# in app.outdir
DOCTEST_OUTPUT = "output.txt"
# Name of output file that the resultant XUnit output is saved
# @todo make this a configuration variable
XUNIT_OUTPUT = "doctest.xml"

#-------------------------------------------------------------------------------
# Regexes
DOCTEST_DOCUMENT_BEGIN = "Document:"
DOCTEST_SUMMARY_TITLE = "Doctest summary"
ALL_PASS_SUMMARY_RE = "\d items passed all tests:"


#-------------------------------------------------------------------------------
class TestSuite(object):

    def __init__(self, result_txt):
        """
        Initialize the object with the ASCII output text for a single
        document. Creates TestCase objects

        Args:
          result_txt (str): String containing doctest output for
                            document
        """
        self.fullname, self.testcases = self.__parse(result_txt)

    def __parse(self, result_txt):
        """
        Create TestCase objects for each test

        Args:
          result_txt (str): String containing doctest output for
                            document
        Returns:
          str: Fullname of test
        """
        fullname = self.__extract_fullname(result_txt[0])
        return fullname, []

    def __extract_fullname(first_line):
        """
        Extract the document name from the line of text.

        Args:
          first_line (str): Line to test for title
        """
        if not first_line.startswith(DOCTEST_DOCUMENT_BEGIN):
            raise ValueError("First line of output text should be a line "
                             "beginning '%s'" % DOCTEST_DOCUMENT_BEGIN)
        return first_line.replace(DOCTEST_DOCUMENT_BEGIN, "").strip()


#-------------------------------------------------------------------------------
class TestCase(object):

    def __init__(self):
        pass

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
