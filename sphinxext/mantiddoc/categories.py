"""Sphinx extension to add a '.. categories::' extension that
writes out the preamble for an Algorithm documentation page.
It pulls out the algorithm summary and the properties table
"""
from docutils import nodes, statemachine
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive

class CategoriesDirective(Directive):
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
        rawtext = "\n" + self._create_category_links(algname)
        tab_width = 4
        include_lines = statemachine.string2lines(rawtext, tab_width,
                                                  convert_whitespace=True)
        self.state_machine.insert_input(include_lines, "")
        return []

    def _create_category_links(self, algorithm_name):
        categories = ["Algorithms", "Transforms"]

        env = self.state.document.settings.env
        if not hasattr(env, "categories"):
            env.categories = {}

        for categ in categories:
            if categ not in env.categories:
                env.categories[categ] = []
            env.categories[categ].append((algorithm_name, env.docname))
        #######
        
        text = "`Categories: <categories.html>`_ " + " Algorithms | Tranforms"
        return text

#------------------------------------------------------------------------------

def html_collect_pages(app):
    '''
    Collect html pages and emit event
    '''
    for name, context, template in create_categories(app):
        yield (name, context, template)

def create_categories(app):
    env = app.builder.env

    categories = env.categories
    subcategories = ["CorrectionFunctions", "Crystal", "DataHandling",
                     "Arithmetic", "Deprecated", "Analog", "Errors"]
    subcategories.sort()

    template = "category.html"

    for category_name, members in categories.iteritems():
        context = {}
        context["title"] = category_name
        context["subcategories"] = subcategories

        algorithm_and_links = []
        for algorithm_name, link in members:
            link += ".html"  
            algorithm_and_links.append((algorithm_name,link))
        # end for
        context["algorithms"] = algorithm_and_links
        yield (category_name, context, template)

#------------------------------------------------------------------------------
def setup(app):
    # Add new directive
    app.add_directive('categories', CategoriesDirective)
    app.connect("html-collect-pages", html_collect_pages)

