#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Common params."""
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

from jira_freeplane.common import LOG, SETTINGS_TEMPLATE
from jira_freeplane.libjira import JiraInterface


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
        make_config = False
        had_prompt = False
        early_exit = False
        if not self.working_dir.exists():
            if yesno(
                f"Working directory {self.working_dir} does not exist. Create it?",
                self.no_prompt,
            ):
                self.working_dir.mkdir(parents=True)
            else:
                raise SystemExit("Working directory does not exist. Exiting...")
        self.file_settings = self.working_dir.joinpath("template", "settings.yaml")
        template_dir = self.working_dir / "template"
        if not self.file_settings.exists():
            if yesno(
                "Would you like to create config files if they don't exist?",
                self.no_prompt,
            ):
                make_config = True
            had_prompt = True
        if make_config:
            if not self.cache_dir.exists():
                self.cache_dir.mkdir(parents=True)
            if not template_dir.exists():
                template_dir.mkdir(parents=True)
            with self.file_settings.open("w") as f:
                f.write(
                    SETTINGS_TEMPLATE.substitute(jira_url=jira_url, reporter=reporter)
                )

        self.file_template_epic = self.working_dir.joinpath(
            "template", f"{self.TYPE_EPIC}.yaml"
        )
        self.file_template_task = self.working_dir.joinpath(
            "template", f"{self.TYPE_TASK}.yaml"
        )
        self.file_template_subtask = self.working_dir.joinpath(
            "template", f"{self.TYPE_SUBTASK}.yaml"
        )

        missing_files = [
            i
            for i in [
                self.file_template_epic,
                self.file_template_task,
                self.file_template_subtask,
            ]
            if not i.exists()
        ]

        LOG.info(f'Initializing JIRA client for "{self.jira_url}"')
        self.jira = JiraInterface(self.cache_dir, self.jira_url)

        if not self.file_settings.exists():
            raise SystemExit(
                f"Settings file does not exist in {self.working_dir}. Exiting..."
            )

        if missing_files:
            if not had_prompt:
                if yesno(
                    "Would you like to create template files if they don't exist?",
                    self.no_prompt,
                ):
                    make_config = True
                had_prompt = True
            if make_config:
                early_exit = True
                LOG.info("Make config enabled, creating config files...")
                for i in missing_files:
                    basename = i.stem
                    issue_type = basename.capitalize()
                    LOG.info(f"Creating Template {i}")
                    with i.open("w") as f:
                        f.write(
                            self.jira.template(
                                project=project_key,
                                issue_type=issue_type,
                            )
                        )
            else:
                raise SystemExit(f"Missing template files: {missing_files}, exiting...")

        if early_exit:
            raise SystemExit(
                "Please edit the config files {} and re-run".format(missing_files)
            )

        self.settings = yaml.load(
            self.file_settings.read_text(), Loader=yaml.FullLoader
        )
        if not self.settings:
            self.settings = {}
        self.data_dir = self.working_dir.joinpath("data")

        # Create directories if they don't exist
        if not self.data_dir.exists():
            LOG.info(f"Creating missing {self.data_dir}")
            self.data_dir.mkdir(parents=True)

        if not self.cache_dir.exists():
            LOG.info(f"Creating missing {self.cache_dir}")
            self.cache_dir.mkdir(parents=True)

        unedited_files = []
        for i in [
            self.file_template_epic,
            self.file_template_task,
            self.file_template_subtask,
        ]:
            if "REMOVE THESE LINES AFTER EDIT" in i.read_text():
                unedited_files.append(i)

        if unedited_files:
            txt = "- {}\n".format("\n- ".join(i.name for i in unedited_files))
            raise SystemExit(
                f"The following files have not been edited\n{txt}.\nPlease edit them and re-run."
            )

        self.data_dct = {
            self.TYPE_EPIC: yaml.load(self.file_template_epic.read_text(), yaml.SafeLoader),
            self.TYPE_TASK: yaml.load(self.file_template_task.read_text(), yaml.SafeLoader),
            self.TYPE_SUBTASK: yaml.load(
                self.file_template_subtask.read_text(), yaml.SafeLoader
            ),
        }
        self.file_dct = {
            self.TYPE_EPIC: self.file_template_epic,
            self.TYPE_TASK: self.file_template_task,
            self.TYPE_SUBTASK: self.file_template_subtask,
        }
        self.field_dct = {
            i: self.jira.get_field_objects(project_key, i.capitalize())
            for i in self.data_dct.keys()
        }

        # Set valid fields for each type taken from settings
        for key, value in self.settings.items():
            for _type in self.data_dct.keys():
                field_list = [i.name for i in self.field_dct[_type]]
                if key in field_list:
                    LOG.info("Merging main settings for %s, %s to %s", _type, key, value)
                    self.data_dct[_type][key] = value

        LOG.info(f"JIRA URL: {self.jira_url}")
        LOG.info(f"Epic Parent: {self.epic_parent}")
        LOG.info(f"Global Template Settings: {self.settings}")
