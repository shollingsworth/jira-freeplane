#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI / Runtime interface."""
import argparse
from configparser import ConfigParser
from pathlib import Path

import untangle

from jira_freeplane.common import LOG, prompt_line, yesno
from jira_freeplane.mm import (create_epics, create_subtasks, create_tasks,
                               node_tree_with_depth, show_summary)
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
    if conf.dry_run:
        LOG.info("Dry run enabled, not creating issues")
    else:
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
        "--config",
        "-c",
        help="Path to the project.ini file",
        type=str,
    )
    parser.add_argument(
        "--interactive",
        "-i",
        help="Run in interactive mode",
        action="store_true",
    )
    parser.add_argument(
        "mm_file",
        help="Path to the mindmap file",
        type=str,
    )
    return parser.parse_args()


def set_ini_file(ini, wd, dest_ini):
    """Set the ini file."""

    ini.set("jira", "dry_run", "true" if yesno("Dry run (don't actually create issues)") else "false")
    ini.set("jira", "skip_optional", "true" if yesno("Skip optional fields") else "false")
    ini.set("jira", "url", prompt_line("JIRA URL (i.e. https://jira.example.com)"))
    ini.set("jira", "reporter", prompt_line("JIRA Reporter (i.e. rsmith)"))
    ini.set(
        "jira",
        "project_parent_issue_key",
        prompt_line("JIRA Project Parent Issue Key (i.e. PROJ-123)"),
    )
    ini.set(
        "jira", "project_key", prompt_line("JIRA Actionable Tasks Project, i.e. OPS")
    )
    ini.set("jira", "working_dir", str(wd))
    ini.set(
        "jira", "debug", "true" if yesno("Enable Debug? (verbose output)") else "false"
    )
    ini.set(
        "jira",
        "no_prompt",
        "true" if yesno("Disable Prompts? (no user interaction)") else "false",
    )
    if yesno(f"Create {dest_ini} ?"):
        with open(dest_ini, "w") as f:
            ini.write(f)
        LOG.info("Created %s", dest_ini)
    else:
        LOG.info("Not creating project.ini file")


def run_mindmap_to_jira():
    """Run main function."""
    args = get_args()
    mmfile = Path(args.mm_file)
    if not mmfile.exists():
        raise SystemExit(f"{mmfile} does not exist")

    ini = ConfigParser()
    if args.interactive:
        ini.add_section("jira")
        wd = Path.cwd().absolute()
        dest_ini = wd / "project.ini"
        if dest_ini.exists():
            LOG.info("%s already exists, using that", dest_ini)
            ini.read(dest_ini)
        else:
            set_ini_file(ini, wd, dest_ini)
        args.config = dest_ini

    elif args.config:
        ini.read(Path(args.ini_file))
    else:
        raise SystemExit("No config file specified, or interactive mode not selected")

    dest_ini = Path(args.config)

    wd = ini.get("jira", "working_dir")
    errors = []
    if not Path(wd).exists():
        errors.append(f"working directory {wd} does not exist")
    project_parent_issue_key = ini.get("jira", "project_parent_issue_key")
    if not project_parent_issue_key:
        errors.append("project_parent_issue_key is required in {dest_ini}")
    pkey = ini.get("jira", "project_key")
    if not pkey:
        errors.append("project_key is required in {dest_ini}")

    jira_url = ini.get("jira", "url")
    if not jira_url:
        errors.append("jira_url is required in {dest_ini}")

    jira_reporter = ini.get("jira", "reporter")
    if not jira_reporter:
        errors.append("jira_reporter is required in {dest_ini}")

    if errors:
        for msg in errors:
            LOG.error(msg)
        raise SystemExit(f"Missing {ini} required fields")

    conf = MMConfig(
        working_dir=str(wd),
        project_parent_issue_key=project_parent_issue_key,
        debug=ini.getboolean("jira", "debug") or False,
        project_key=pkey,
        jira_url=jira_url,
        reporter=jira_reporter,
        noprompt=ini.getboolean("jira", "no_prompt") or False,
        skip_optional=ini.getboolean("jira", "skip_optional") or False,
        dry_run=ini.getboolean("jira", "dry_run") or False,
        mm_file=Path(args.mm_file),
    )
    try:
        mindmap_to_jira(conf)
    except KeyboardInterrupt:
        LOG.info("Interrupted by user")
        raise SystemExit("Bye!")


def main():
    """Run main function."""
    run_mindmap_to_jira()


if __name__ == "__main__":
    main()
