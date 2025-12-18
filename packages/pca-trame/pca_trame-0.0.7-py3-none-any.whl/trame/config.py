from markdown.extensions.tables import TableExtension

# TODO sel: améliorer le pattern sur l'encoding
ENCODING = "utf-8"

MD_EXTENSIONS = [
    # "abbr",
    # "attr_list",
    "fenced_code",
    "meta",
    TableExtension(use_align_attribute=True),
    # "toc",
]


BS4_HTML_PARSER = "html.parser"
