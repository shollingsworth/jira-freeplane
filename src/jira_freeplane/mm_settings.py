#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common params."""
import json
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from simple_term_menu import TerminalMenu

from jira_freeplane.common import AUTOFIELDS, LOG
from jira_freeplane.libjira import Field, JiraInterface

# simple-term-menu


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


class MMConfig:
    """Config class."""

    TYPE_ROOT = "root"
    TYPE_EPIC = "epic"
    TYPE_TASK = "task"
    TYPE_SUBTASK = "sub-task"

    def __init__(
        self,
        working_dir: str,
        epic_parent: str,
        jira_url: str,
        project_key: str,
        reporter: str,
        noprompt: bool,
        mm_file: Path,
        debug=False,
    ) -> None:
        self.mm_file = mm_file
        self.debug = debug
        self.no_prompt = noprompt
        self.reporter = reporter
        self.jira_url = jira_url
        self.project_key = project_key
        self.required_dct = {}  # type: Dict[Tuple[str, str], List[str]]
        self.epic_parent = epic_parent
        self.working_dir = Path(working_dir).absolute().joinpath(epic_parent)
        self.cache_dir = self.working_dir.joinpath("cache")
        self.file_settings = self.working_dir.joinpath("settings.yaml")
        make_config = False
        if yesno(f"Do you want to create files if they do not exist?", self.no_prompt):
            make_config = True

        if not self.working_dir.exists():
            if make_config:
                self.working_dir.mkdir(parents=True)
            else:
                raise SystemExit("Working directory does not exist. Exiting...")

        if not self.cache_dir.exists():
            if make_config:
                self.cache_dir.mkdir(parents=True)
            else:
                raise SystemExit("Cache directory does not exist. Exiting...")

        LOG.info(f'Initializing JIRA client for "{self.jira_url}"')
        self.jira = JiraInterface(self.cache_dir, self.jira_url)
        do_create = False
        if self.file_settings.exists():
            self.settings = yaml.load(
                self.file_settings.read_text(), Loader=yaml.FullLoader
            )
        else:
            do_create = True
            self.settings = {
                "Reporter": self.reporter,
                "Project": self.project_key,
            }

        self.data_dir = self.working_dir.joinpath("data")
        # Create directories if they don't exist
        if not self.data_dir.exists():
            LOG.info(f"Creating missing {self.data_dir}")
            self.data_dir.mkdir(parents=True)

        if not self.cache_dir.exists():
            LOG.info(f"Creating missing {self.cache_dir}")
            self.cache_dir.mkdir(parents=True)

        self.field_dct = {}  # type: Dict[str, List[Field]]
        self.files = {}  # type: Dict[str, Path]
        self.data_dct = {}  # type: Dict[str, Dict[str, str]]
        for i in [self.TYPE_EPIC, self.TYPE_TASK, self.TYPE_SUBTASK]:
            self.field_dct[i] = self.jira.get_field_objects(project_key, i.capitalize())

        self.files[self.TYPE_EPIC] = self.working_dir.joinpath(self.TYPE_EPIC + ".yaml")
        self.files[self.TYPE_TASK] = self.working_dir.joinpath(self.TYPE_TASK + ".yaml")
        self.files[self.TYPE_SUBTASK] = self.working_dir.joinpath(
            self.TYPE_SUBTASK + ".yaml"
        )

        LOG.info(f"JIRA URL: {self.jira_url}")
        LOG.info(f"Epic Parent: {self.epic_parent}")
        LOG.info(f"Global Template Settings: {self.settings}")
        if do_create:
            self.select_settings()
            with self.file_settings.open("w") as f:
                f.write(yaml.dump(self.settings, default_flow_style=False))  # type: ignore
        for _type, file in self.files.items():
            if file.exists():
                self.data_dct[_type] = yaml.load(  # type: ignore
                    file.read_text(), Loader=yaml.FullLoader
                )
            else:
                self.data_dct[_type] = {
                    "Project": self.settings["Project"],  # type: ignore
                    "Issue Type": _type.capitalize(),
                }
                for field in self.field_dct[_type]:
                    if field.name in AUTOFIELDS:
                        continue
                    if field.name in self.settings:
                        self.data_dct[_type][field.name] = self.settings[field.name]  # type: ignore
                with file.open("w") as f:
                    f.write(yaml.dump(self.data_dct[_type], default_flow_style=False))  # type: ignore
            print(json.dumps(self.data_dct[_type], indent=4))
        print(json.dumps(self.settings, indent=4, separators=(",", " : ")))

    def get_values(self, field: Field):
        prefix = "Select "
        if field.required:
            prefix = f"{prefix} *Required"
        else:
            prefix = f"{prefix} *Optional"

        if field.allowed_values:
            keys = list(field.allowed_values.keys())
            if field.is_array:
                term = TerminalMenu(
                    field.allowed_values,
                    title=f"{prefix} {field.name}",
                    multi_select=True,
                )
                value = [keys[i] for i in term.show()]  # type: ignore
                self.settings[field.name] = value  # type: ignore
            else:
                term = TerminalMenu(
                    field.allowed_values, title=f"{prefix} {field.name}"
                )
                value = keys[term.show()]  # type: ignore
        else:
            if field.is_array:
                value = []
                while True:
                    _val = input(f"Enter line for {field.name}, blank to terminate: ")
                    if not _val:
                        break
                    else:
                        value.append(_val)
            else:
                value = input(f"TYPE Entry, or enter: {prefix} {field.name}: ")
        return value

    def select_settings(self):
        for issue_type, fields in self.field_dct.items():
            LOG.info(f"Populating {issue_type} fields")

            for field in fields:  # type: List[Field]
                if field.name == "Issue Type":
                    continue
                if field.name in self.settings:
                    LOG.info("Skipping already set value: %s == %s", field.name, self.settings[field.name])  # type: ignore
                    continue
                if (field.default_value != "") and (
                    field.default_value != field.all_value
                ):
                    self.settings[field.name] = field.default_value  # type: ignore
                    LOG.info(
                        "Skipping default value: %s == %s",
                        field.name,
                        field.default_value,
                    )
                    continue
                if field.name in AUTOFIELDS:
                    LOG.info("Skipping Auto-Set Value %s", field.name)
                    continue
                value = self.get_values(field)
                if not value == "":
                    self.settings[field.name] = value  # type: ignore


def main():
    options = ["entry 1", "entry 2", "entry 3"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    print(f"You have selected {options[menu_entry_index]}!")  # type: ignore


if __name__ == "__main__":
    main()
