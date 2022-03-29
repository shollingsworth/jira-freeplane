#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XML to dict parse."""
import json
import textwrap
from configparser import ConfigParser
from pathlib import Path
from typing import Iterable

import untangle

from jira_freeplane.common import LOG
from jira_freeplane.mm_settings import MMConfig


class Node:
    """Node class."""

    COLLECTION = {}

    def __init__(
        self,
        config: MMConfig,
        node: untangle.Element,
        depth: int,
        parent: untangle.Element = None, # type: ignore
    ) -> None:
        self.glb = config
        self.depth = depth
        self.id = node["ID"]
        self.node = node
        Node.COLLECTION[self.id] = self
        self.parent_id = parent["ID"] if parent else None
        self.text = node["TEXT"] or ""
        self.link = node["LINK"] or ""
        try:
            rich = node.richcontent.html.body  # type: ignore
            lines = []
            for p in rich.get_elements("p"):
                lines.append(p.cdata.rstrip())
            flat = textwrap.dedent("\n".join(line if line else "\n" for line in lines))
            dat = flat.replace("\n\n", "\n").rstrip()
            self.note = dat
        except AttributeError:
            self.note = ""

        self.cfile = self.glb.data_dir.joinpath(f"{self.id}.ini")
        self.parent_cfile = self.glb.data_dir.joinpath(f"{self.parent_id}.ini")

        self._config = ConfigParser()
        self._parent_config = ConfigParser()

    def children(self) -> Iterable["Node"]:
        """Get subtask children."""
        yield from node_tree_with_depth(self.glb, self.node)

    @property
    def child_text(self) -> str:
        """Get subtask children."""
        if self.link:
            txt = f"[{self.text}|{self.link}]"
        else:
            txt = self.text

        newlinecnt = txt.count("\n")
        if newlinecnt > 1:
            txt = "{code}" + txt + "{code}"
        return self.depth * "*" + " " + txt

    def _load_config(self, config_val: ConfigParser, config_path: Path) -> ConfigParser:
        """Load config."""
        if config_path.exists():
            config_val.read(str(config_path))
            return config_val
        if config_val.sections():
            return config_val
        else:
            config_val.add_section("jira")
            with config_path.open("w") as f:
                config_val.write(f)
            return config_val

    def _save(self, config_val: ConfigParser, config_path: Path) -> None:
        """Load config."""
        with config_path.open("w") as f:
            config_val.write(f)

    @property
    def config(self) -> ConfigParser:
        """Config property."""
        return self._load_config(self._config, self.cfile)

    @property
    def parent_config(self) -> ConfigParser:
        """Parent config property."""
        return self._load_config(self._parent_config, self.parent_cfile)

    def parent_save(self) -> None:
        """Save parent config."""
        self._save(self._parent_config, self.parent_cfile)

    def save(self) -> None:
        """Save config."""
        self._save(self._config, self.cfile)

    def is_task(self) -> bool:
        """Check if node is task."""
        return self.depth <= 3

    @property
    def depth_type(self) -> str:
        """Return depth type."""
        if self.depth == 0:
            return self.glb.TYPE_ROOT
        if self.depth == 1:
            return self.glb.TYPE_EPIC
        if self.depth == 2:
            return self.glb.TYPE_TASK
        if self.depth == 3:
            return self.glb.TYPE_SUBTASK
        else:
            return str(self.depth - 3)


def node_tree_with_depth(config: MMConfig, root: untangle.Element) -> Iterable[Node]:
    """Return a list of nodes with depth."""

    def _vals(node: untangle.Element, depth=0, parent: untangle.Element = None): # type: ignore
        yield node, depth, parent
        children = node.get_elements("node")
        if not children:
            return
        for child in children:
            yield from _vals(child, depth + 1, node)

    for node, depth, parent in _vals(root): # type: ignore
        yield Node(config, node, depth, parent)


def create_subtasks(config: MMConfig, nodes: Iterable[Node]) -> None:
    """Create epic."""
    for node in nodes:
        if node.depth_type != config.TYPE_SUBTASK:
            continue
        if node.config.has_option("jira", "key"):
            key = node.config.get("jira", "key")
            LOG.info(f"{node.cfile} / {key} exists, skipping")
            continue
        parent_key = node.parent_config.get("jira", "key")
        LOG.info(f'running "{node.text}" / linking to "{parent_key}"')
        body = ""
        if node.link:
            body += f"\n\n{node.link}"
        for i in node.children():
            if i.depth == 0:
                continue
            body += f"\n{i.child_text}"
        LOG.info(
            f"Creating parent {node.id}, {node.depth_type}, {node.depth}, {node.text}"
        )
        if node.note:
            body += f"-----------------------------\n\n\n{node.note}"

        try:
            parent_key = node.parent_config.get("jira", "key")
        except Exception:
            LOG.info("Err %s", node.parent_cfile.read_text())
            LOG.info(node.parent_config.get("jira", "key"))
            raise
        working = dict(config.data_dct[config.TYPE_SUBTASK])
        working["Summary"] = node.text
        working["Parent"] = { # type: ignore
            "key": parent_key,
        }
        working["Description"] = body or "---"
        conv = config.jira.to_jira_dct(working)
        key = config.jira.submit(conv)
        LOG.info(f"Created Issue -> {config.jira_url}/browse/{key}")
        node.config.set("jira", "json_body", json.dumps(working))
        node.config.set("jira", "key", key)
        node.config.set("jira", "is_linked", "false")
        LOG.info(f"Writing config file {key}")
        with node.cfile.open("w") as f:
            LOG.info(f"writing {node.text} -> {node.cfile}")
            node.config.write(f)


def create_tasks(config: MMConfig, nodes: Iterable[Node]) -> None:
    """Create epic."""
    for node in nodes:
        if node.depth_type != config.TYPE_TASK:
            continue
        if node.cfile.exists():
            LOG.info(f"{node.cfile} exists, skipping")
            continue

        parent_key = node.parent_config["jira"]["key"]

        working = dict(config.data_dct[config.TYPE_TASK])
        working["Summary"] = node.text
        working["Epic Link"] = parent_key
        working["Description"] = node.note or "---"
        conv = config.jira.to_jira_dct(working)
        key = config.jira.submit(conv)
        LOG.info(f"Created Issue -> {config.jira_url}/browse/{key}")
        node.config.set("jira", "json_body", json.dumps(working))
        node.config.set("jira", "key", key)
        node.config.set("jira", "is_linked", "false")
        LOG.info(f"Writing config file {key}")
        with node.cfile.open("w") as f:
            LOG.info(f"writing {node.text} -> {node.cfile}")
            node.config.write(f)


def create_epics(config: MMConfig, nodes: Iterable[Node]) -> None:
    """Create epic."""
    runlist = []
    for node in nodes:
        if node.depth_type != config.TYPE_EPIC:
            continue
        runlist.append(node)
        if node.cfile.exists():
            LOG.info(f"{node.cfile} exists, skipping")
            continue
        working = dict(config.data_dct[config.TYPE_EPIC])
        working["Summary"] = node.text
        working["Epic Name"] = node.text
        working["Description"] = node.note or "---"
        conv = config.jira.to_jira_dct(working)
        key = config.jira.submit(conv)
        LOG.info(f"Created Issue -> {config.jira_url}/browse/{key}")
        node.config.set("jira", "json_body", json.dumps(working))
        node.config.set("jira", "key", key)
        node.config.set("jira", "is_linked", "false")
        LOG.info(f"Writing config file {key}")
        with node.cfile.open("w") as f:
            LOG.info(f"writing {node.text} -> {node.cfile}")
            node.config.write(f)

    for node in runlist:
        with node.cfile.open() as f:
            node.config.read_file(f)
        if node.config.get("jira", "key") == "None":
            raise ValueError(f"{node.cfile} has no key")
        if node.config.get("jira", "is_linked") == "true":
            LOG.info(f"{node.cfile} is linked, skipping")
            continue
        config.jira.link_parent_issue(
            node.config.get("jira", "key"), config.epic_parent
        )
        node.config.set("jira", "is_linked", "true")
        with node.cfile.open("w") as f:
            LOG.info(f"updating with linked {node.text} -> {node.cfile}")
            node.config.write(f)


def show_summary(config: MMConfig, nodes: Iterable[Node]) -> None:
    """Create epic."""
    for node in nodes:
        if node.depth_type not in [
            config.TYPE_EPIC,
            config.TYPE_TASK,
            config.TYPE_SUBTASK,
        ]:
            continue
        key = node.config.get("jira", "key")
        LOG.info(f"{config.jira_url}/browse/{key} -> {node.text}")
