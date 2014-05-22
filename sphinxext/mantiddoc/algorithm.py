"""Sphinx extension to add a '.. algheader::' extension that
writes out the preamble for an Algorithm documentation page.
It pulls out the algorithm summary and the properties table
"""
from docutils import nodes, statemachine
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive

#------------------------------------------------------------------------------
# The '_%(name)' will be converted to something like _Rebin, which creates an
# item that can be referenced internally using the  sphinx ext :ref:`Rebin`
#
HEADER_TEMPLATE = \
"""
.. _algorithm|%(name)s:

%(name)s
%(underline)s
%(summary)s

Aliases
-------
%(aliases)s

Properties
----------
%(proptable)s
"""

class AlgorithmDirective(Directive):
    """
    Insert additional reST text for an algorithm preamble

    The algorithm name is a the single required argument.
    """

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {'file': directives.path,
                   'url': directives.uri,
                   'encoding': directives.encoding}
    has_content = True

    def run(self):
        """
        Called by the Sphinx framework whenever the ..algorithm::
        directive is encountered
        """
        algname = str(self.arguments[0])
        rawtext = self._create_page_header(algname)
        tab_width = 4
        include_lines = statemachine.string2lines(rawtext, tab_width,
                                                  convert_whitespace=True)
        self.state_machine.insert_input(include_lines, "")
        return []

    def _create_page_header(self, algorithm_name):
        """
        Return the page header for the named algorithm
        """
        from mantid.api import AlgorithmManager # will only happen once
        alg = AlgorithmManager.createUnmanaged(algorithm_name)
        alg.initialize()
        summary = alg.getWikiSummary()
        
        rawtext = HEADER_TEMPLATE % {"name" : algorithm_name,
                                     "underline" : "-" * len(algorithm_name),
                                     "summary" : alg.getWikiSummary(),
                                     "aliases" : alg.alias(),
                                     "proptable" : self._create_prop_table(alg)
                                    }
        return rawtext

    def _create_prop_table(self, alg):
        """
        Return a string containing the properties table
        in reStructeredText format for the given algorithm object
        """
        return ""

#------------------------------------------------------------------------------
def setup(app):
    # Add new directive
    app.add_directive('algorithm', AlgorithmDirective)

