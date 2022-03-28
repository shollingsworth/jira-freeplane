#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI / Runtime interface."""
import argparse
from pathlib import Path

import untangle

from common import LOG
from jira_freeplane.mm import (create_epics, create_subtasks, create_tasks,
                               node_tree_with_depth, show_summary)
from jira_freeplane.mm_settings import MMConfig


def mindmap_to_jira(conf: MMConfig):
    """Run main function."""
    args = get_args()
    LOG.info("Starting...")
    LOG.info("Arguments: %s", args)
    LOG.info("Parsing XML...")
    dct = untangle.parse(str(args.mapfile))
    rmap = dct.map  # type untangle.Element
    root = rmap.node  # type: ignore
    LOG.info("Root node: %s", root["TEXT"])
    LOG.info("Loading JIRA metadata...")
    errors = []
    LOG.info("Santity checking config files...")
    for _type, dct in conf.data_dct.items():
        fp = conf.file_dct[_type]
        fields = conf.field_dct[_type]
        fdct = {
            i.name: i
            for i in fields
        }
        LOG.info("Checking %s...", fdct)
        project = dct['Project'] # type: ignore
        issue_type = dct['Issue Type'] # type: ignore
        LOG.info("Loading %s %s...", project, issue_type)
        for key, val in dct.items():
            if key not in fdct:
                errors.append(
                    f"{key} is not a valid field for {_type} in {fp}"
                )
                continue
            if fdct[key].required and not val:
                errors.append(
                    f"{key} is required for {_type} in {fp}"
                )
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


def get_args(test_args=None):
    """Get command line arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__,
    )
    parser.add_argument(
        "mapfile",
        help="freeplane map file (i.e. project.mm)",
        type=Path,
    )
    parser.add_argument(
        "epic_parent",
        help="JIRA epic project issue key (i.e. PROJ-123)",
    )
    parser.add_argument(
        "-d",
        "--directory",
        help="root project directory",
        type=Path,
        default=Path.cwd(),
    )
    parser.add_argument(
        "-p",
        "--epic_project_key",
        type=str,
        help="JIRA epic project key (i.e. OPS)",
        required=True,
    )
    parser.add_argument(
        "-j",
        "--jira_url",
        type=str,
        help="JIRA URL (i.e. https://jira.example.com)",
        required=True,
    )
    parser.add_argument(
        "-r",
        "--reporter",
        type=str,
        help="JIRA reporter (i.e. jsmith)",
        required=True,
    )
    # no prompt boolean
    parser.add_argument(
        "-n",
        "--noprompt",
        help="do not prompt for questions",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "-v",
        "--verbose",
        help="enable debug output",
        action="store_true",
        default=False,
    )
    if test_args:
        return parser.parse_args(test_args)
    return parser.parse_args()


def run_mindmap_to_jira():
    """Run main function."""
    try:
        args = get_args()
        conf = MMConfig(
            working_dir=args.directory.expanduser(),
            epic_parent=args.epic_parent,
            debug=args.verbose,
            project_key=args.epic_project_key,
            jira_url=args.jira_url,
            reporter=args.reporter,
            noprompt=args.noprompt,
        )
        mindmap_to_jira(conf)
    except KeyboardInterrupt:
        LOG.info("Interrupted by user")
        raise SystemExit("Bye!")


if __name__ == "__main__":
    run_mindmap_to_jira()
