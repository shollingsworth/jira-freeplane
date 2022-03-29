#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI / Runtime interface."""
from configparser import ConfigParser
from pathlib import Path
import argparse

import untangle

from jira_freeplane.common import LOG
from jira_freeplane.mm import (
    create_epics,
    create_subtasks,
    create_tasks,
    node_tree_with_depth,
    show_summary,
)
from jira_freeplane.mm_settings import MMConfig


def mindmap_to_jira(conf: MMConfig):
    """Run main function."""
    LOG.info("Starting...")
    LOG.info("Arguments: %s", conf)
    LOG.info("Parsing XML...")
    dct = untangle.parse(str(conf.mm_file))
    rmap = dct.map  # type untangle.Element
    root = rmap.node  # type: ignore
    LOG.info("Root node: %s", root["TEXT"])
    LOG.info("Loading JIRA metadata...")
    errors = []
    LOG.info("Santity checking config files...")
    for _type, dct in conf.data_dct.items():
        fp = conf.files[_type]
        fields = conf.field_dct[_type]
        fdct = {i.name: i for i in fields}
        project = dct["Project"]  # type: ignore
        issue_type = dct["Issue Type"]  # type: ignore
        LOG.info("Loading %s %s...", project, issue_type)
        for key, val in dct.items():
            if key not in fdct:
                errors.append(f"{key} is not a valid field for {_type} in {fp}")
                continue
            if fdct[key].required and not val:
                errors.append(f"{key} is required for {_type} in {fp}")
    if errors:
        for msg in errors:
            LOG.error(msg)
        raise SystemExit("Missing required fields")
    nodes = list(node_tree_with_depth(conf, root))
    if conf.debug:
        for node in nodes:
            LOG.info(f"Node: {node.depth_type}, {node.depth}, {node.text}")
    LOG.info(
        f"Conf type: epic:{conf.TYPE_EPIC}, task:{conf.TYPE_TASK}, sub-task:{conf.TYPE_SUBTASK}"
    )
    # Start the stuffs
    LOG.info("Creating Epics...")
    create_epics(conf, nodes)
    LOG.info("Creating Tasks...")
    create_tasks(conf, nodes)
    LOG.info("Creating Subtasks...")
    create_subtasks(conf, nodes)
    LOG.info("Done!")
    show_summary(conf, nodes)


def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument(
        "ini_file",
        help="Path to the project.ini file",
        type=str,
    )
    parser.add_argument(
        "mm_file",
        help="Path to the mindmap file",
        type=str,
    )
    return parser.parse_args()


def run_mindmap_to_jira():
    """Run main function."""
    args = get_args()
    ini = ConfigParser()
    ini.read(Path(args.ini_file))
    conf = MMConfig(
        working_dir=ini.get("jira", "working_dir"),
        epic_parent=ini.get("jira", "epic_parent"),
        debug=ini.getboolean("jira", "debug"),
        project_key=ini.get("jira", "project_key"),
        jira_url=ini.get("jira", "url"),
        reporter=ini.get("jira", "reporter"),
        noprompt=ini.getboolean("jira", "no_prompt"),
        mm_file=Path(args.mm_file),
    )
    try:
        mindmap_to_jira(conf)
    except KeyboardInterrupt:
        LOG.info("Interrupted by user")
        raise SystemExit("Bye!")
