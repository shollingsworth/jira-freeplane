#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common variables."""
import logging

logging.basicConfig()
LOG = logging.getLogger("JIRA Mindmap CLI")
LOG.setLevel(logging.INFO)

def prompt_line(prompt):
    """Prompt user for input."""
    return input(f'Input {prompt}: ').strip()

def prompt_multiline(prompt):
    value = []
    while True:
        _val = input(prompt)
        if not _val:
            break
        else:
            value.append(_val)
    return value

def yesno(question, noprompt=False):
    """Simple Yes/No Function."""
    if noprompt:
        return True
    prompt = f"{question} ? (y/n): "
    ans = input(prompt).strip().lower()
    if ans not in ["y", "n"]:
        print(f"{ans} is invalid, please try again...")
        return yesno(question)
    if ans == "y":
        return True
    return False

AUTOFIELDS = [
    "Summary",
    "Description",
    "Epic Link",
    "Epic Name",
    "Parent",
]
