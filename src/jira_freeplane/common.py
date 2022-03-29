#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common variables."""
import logging

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
