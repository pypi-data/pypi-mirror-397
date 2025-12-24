from bs4.element import PageElement


from bs4 import BeautifulSoup
from bs4.element import NavigableString


from trame.config import BS4_HTML_PARSER


def clean_text_nodes(element: PageElement) -> str:
    """Recursively clean \n from text nodes only, preserve HTML structure."""
    if isinstance(element, NavigableString):
        return str(element).replace("\n", " ")

    # Clone and clean recursively
    cleaned = BeautifulSoup(str(element), features=BS4_HTML_PARSER)
    for text_node in cleaned.find_all(string=True):
        text_node.replace_with(text_node.replace("\n", " "))

    # Get the first child and convert to string, then ensure all newlines are removed
    first_child = next(cleaned.children)
    result = str(first_child)
    # Final pass: replace any remaining newlines with spaces
    return result.replace("\n", " ")
