#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common variables."""
import logging
from string import Template

logging.basicConfig()
LOG = logging.getLogger("JIRA Mindmap CLI")
LOG.setLevel(logging.INFO)

AUTOFIELDS = [
    "Summary",
    "Description",
    "Epic Link",
    "Epic Name",
    "Parent",
]

SETTINGS_TEMPLATE = Template(
    f"""
# -------------------
# The below field names should mirror human readable field names in JIRA
# if it only accepts valid values, you'll need to look up as well.
# If a field accepts multiple values, you can use a list.
# otherwise you can use a string.
# -------------------
# This is the main Settings template, so a field is defined here and exists in
# one of the templates it will use the value here in all subsequent templates.
# The following is an example of what this would look like
# The templates come pre-populated after first run, so you can use those values
# in this template as well.
# -------------------
#  Labels:
#    - Existing-Label
#  Array Custom Field:
#    - Valid-Value 1
#    - Valid-Value 2
# If a field name has brackets, quote them as keys
# i.e.
# "[inside] Fieldname": "Value"

Reporter: ${{reporter}}
""".lstrip()
)
