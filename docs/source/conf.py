# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import re

from sphinx.ext import apidoc

# The following import, although being unused, is needed to fix the max recursions
# depth issue with sphinx. As a result we supress Ruff linter rule F401.
import monkey_wrench  # noqa: F401

# -- Project information -----------------------------------------------------

project = "monkey-wrench"
author = "Pouria Khalaj"

autodoc_mock_imports = [
    "eumdac",
    "fsspec",
    "loguru",
    "numpy",
    "pyresample",
    "requests",
    "satpy",
    "torch",
    "xarray",
    "chimp"
]

# The full version, including alpha/beta/rc tags
# release = __version__

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autosummary"
]

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
include_patterns = ["**"]

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ["_static"]


# Specify which special members have to be kept
special_members_dict = {
    "EumetsatAPI": [],
    "EumetsatQuery": [],
    "List": [],
    "LogMixin": [],
    "Query": [],
}

for v in special_members_dict.values():
    if not v:
        v.append("init")

# Specify which patterns have to be excluded
patterns_to_exclude = {"_abc_impl", "model_config"}

# Add trailing and leading "__" to all the aforementioned members
for cls, methods in special_members_dict.items():
    special_members_dict[cls] = {f"__{method}__" for method in methods}

# Make a set of all allowed special members
all_special_members = set()
for methods in special_members_dict.values():
    all_special_members |= methods

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "private-members": True,
    "special-members": True,
    "undoc-members": False,
}


def is_special_member(member_name: str) -> bool:
    """Checks if the given member is special, i.e. its name has the following format ``__<some-str>__``."""
    return bool(re.compile(r"^__\w+__$").match(member_name))


def skip(app, typ, member_name, obj, flag, options):
    """The filter function to determine whether to keep the member in the documentation.

    ``True`` means skip the member.
    """
    for pattern in patterns_to_exclude:
        if pattern in member_name:
            return True

    if is_special_member(member_name):
        if member_name not in all_special_members:
            return True

        obj_name = obj.__qualname__.split(".")[0]
        if methods_set := special_members_dict.get(obj_name, None):
            if member_name in methods_set:
                return False  # Keep the member
        return True

    return None


def setup(app):
    """Sets up the sphinx app."""
    app.connect("autodoc-skip-member", skip)


root_doc = "index"

output_dir = os.path.join(".")
module_dir = os.path.abspath("../../monkey_wrench")
apidoc.main(["-e", "-q", "-f", "-M", "-H", "API Reference", "-o", output_dir, module_dir])
