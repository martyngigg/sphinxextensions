from base import BaseDirective

class PageRef(object):
    """
    Store details of a single page reference
    """
    # Name displayed on listing page
    name = None
    # The link to the named page
    link = None

    def __init__(self, name):
        self.name = name
#endclass

class Category(object):
    """
    Store information about a single category
    """
    # Displayed name of the category page
    name = None
    # Collection of Page objects that link to members of the category 
    pages = []
    # Collection of Category objects that form subcategories of this category
    subcategories = []

    def __init__(self, name):
        self.name = name
#endclass

class CategoriesDirective(BaseDirective):
    """
    Records the page as part of the given categories. Index pages for each
    category are then automatically created after all pages are collected
    together.

    Subcategories can be given using the "\\" separator, e.g. Algorithms\\Transforms
    """

    # requires at least 1 category
    required_arguments = 1
    # it can be in many categories and we put an aribitrary upper limit here
    optional_arguments = 25

    def run(self):
        """
        Called by Sphinx when the ..categories:: directive is encountered.
        """
        env = self.state.document.settings.env

        categories = self._get_categories_list()
        display_name = env.docname.split("/")[-1]
        links = self._create_links_and_track(display_name, categories)

        return self._insert_rest("\n" + links)

    def _get_categories_list(self):
        """
        Returns a list of the category strings

        Returns:
          list: A list of strings containing the required categories
        """
        # Simply all of the arguments as strings
        return self.arguments

    def _create_links_and_track(self, page_name, category_list):
        """
        Return the reST text required to link to the given
        categories. As the categories are parsed they are
        stored within the current environment for use in the
        "html_collect_pages" function.

        Args:
          page_name (str): Name to use to refer to this page on the category index page
          category_list (list): List of category strings

        Returns:
          str: A string of reST that will define the links
        """
        env = self.state.document.settings.env
        if not hasattr(env, "categories"):
            env.categories = {}

        link_rst = ""
        ncategs = 0
        for item in category_list:
            has_subcat = False
            if r"\\" in item:            
                categs = item.split(r"\\")
                has_subcat = True
            else:
                categs = [item]
            # endif

            print 
            for index, categ_name in enumerate(categs):
                if categ_name not in env.categories:
                    category = Category(categ_name)
                    env.categories[categ_name] = category
                else:
                    category = env.categories[categ_name]
                #endif
                category.pages.append(PageRef(page_name))
                if has_subcat and index > 0:
                    category.subcategories.append(PageRef(categ_name))
                #endif
                link_rst += ":ref:`%s` | " % categ_name
                ncategs += 1
            # endfor
        # endfor

        link_rst = "`%s: <categories.html>`_ " + link_rst
        if ncategs == 1:
            link_rst = link_rst % "Category"
        else:
            link_rst = link_rst % "Categories"
        #endif

        return link_rst
    #end def

#---------------------------------------------------------------------------------


#---------------------------------------------------------------------------------

def html_collect_pages(app):
    """
    Callback for the 'html-collect-pages' Sphinx event. Adds category
    pages + a global Categories.html page that lists the pages included.

    Function returns an iterable (pagename, context, html_template),
    where context is a dictionary defining the content that will fill the template

    Arguments:
      app: A Sphinx application object 
    """

    if not hasattr(app.builder.env, "categories"):
        return # nothing to do

    for name, context, template in create_category_pages(app):
        yield (name, context, template)

def create_category_pages(app):
    """
    Returns an iterable of (category_name, context, "category.html")

    Arguments:
      app: A Sphinx application object 
    """
    env = app.builder.env

    template = "category.html"

    categories = env.categories
    for name, category in categories.iteritems():
        context = {}
        context["title"] = category.name
        context["subcategories"] = category.subcategories
        context["pages"] = category.pages

        yield (name, context, template)

#------------------------------------------------------------------------------
def setup(app):
    # Add new directive
    app.add_directive('categories', CategoriesDirective)
    # connect event to handler
    app.connect("html-collect-pages", html_collect_pages)

