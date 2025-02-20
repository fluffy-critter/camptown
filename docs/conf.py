import os
import sys

import sphinx_rtd_theme

project = "camptown"
master_doc = "index"
extensions = ["sphinx.ext.autodoc"]
autoclass_content = "both"
autodoc_member_order = "groupwise"
autodoc_inherit_docstrings = False
html_logo = "logo.png"


html_theme = 'sphinx_rtd_theme'

sys.path.insert(0, os.path.abspath('..'))
