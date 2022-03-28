#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XML to dict parse."""
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Union

import jira
import yaml

from jira_freeplane.common import AUTOFIELDS, LOG

USER = os.environ.get("JIRA_USER", "")
PASS = os.environ.get("JIRA_PASS", "")
JIRA_TOKEN = os.environ.get("JIRA_TOKEN")
if not any([USER, PASS, JIRA_TOKEN]):
    raise SystemExit("JIRA_USER, JIRA_PASS or JIRA_TOKEN not set")

IGNORE = [
    "attachment",
    "issuelinks",
]

NAME_IGNORE = [
    "Sprint",
]


class Field:
    """Field type logic."""

    def __init__(
        self,
        data: Dict[str, Any],
        project: str,
        issue_type: str,
        merge_values: Dict[str, Any] = None,
    ):
        """Init."""
        self.project = project
        self.issue_type = issue_type
        if merge_values is None:
            self.merge_values = {}
        else:
            self.merge_values = merge_values
        self.name = data["name"]
        self.id = data["fieldId"]
        self.schema = data["schema"]
        self.operations = data["operations"]
        self.required = data["required"]
        self._allowed_values = data.get("allowedValues", [])

    @property
    def allowed_values(self) -> Dict[str, Any]:
        value_dict = {}

        for value in self._allowed_values:
            if "name" in value:
                vname = value["name"]
            elif "value" in value:
                vname = value["value"]
            else:
                raise ValueError("name or value not found")
            try:
                value_dict[vname] = value["id"]
            except KeyError as e:
                LOG.error("!!!!ERROR!!!!", e, value)
                return {}
        return value_dict

    @property
    def is_user(self) -> bool:
        """Check if field is user."""
        return self.schema.get("type") == "user"

    @property
    def valid(self):
        """Validate."""
        mval = self.merge_values.get(self.name, None)
        if mval is None:
            return True
        if self.allowed_values:
            if isinstance(mval, str):
                return mval in self.allowed_values.keys()
            elif isinstance(mval, list):
                for v in mval:
                    if v not in self.allowed_values.keys():
                        return False
                return True
            else:
                return False
        return True

    @property
    def default_value(self) -> Union[str, List[str], int, None]:
        """Get default value."""
        if self.name == "issuetype":
            return self.issue_type
        if self.name == "project":
            return self.project
        if self.name in self.merge_values.keys():
            val = self.merge_values[self.name]
            if self.valid:
                return val
            else:
                raise SystemExit(
                    f'{self.name} value: "{val}" is not in allowed values: {self.allowed_values}'
                )
        if self.schema["type"] == "number":
            return 0
        if len(self.allowed_values) == 1:
            lst = list(self.allowed_values.keys())
            return lst[0]
        if self.is_array and not self.allowed_values:
            return []
        elif self.allowed_values:
            return list(self.allowed_values.keys())
        return ""

    @property
    def all_value(self) -> Union[str, List[str]]:
        """Get all values."""
        if self.is_array:
            return list(self.allowed_values.keys())
        else:
            return ""

    @property
    def is_array(self) -> bool:
        """Is array."""
        if self.schema["type"] == "array":
            return True
        if self.operations == ["set"]:
            return False
        if "add" in self.operations:
            return True
        return False

    @property
    def ignore(self) -> bool:
        """Ignore."""
        _type = self.schema.get("type", "")
        _items = self.schema.get("items", "")
        if self.name in NAME_IGNORE:
            return True
        if _type in IGNORE or _items in IGNORE:
            return True
        return False

    @property
    def out_dict(self) -> Dict[str, Any]:
        """Out dict."""
        LOG.info("out dict, %s", self.name)
        if self.name == "Project":
            return {"Project": self.project}
        if self.name == "Issue Type":
            return {"Issue Type": self.issue_type}
        if self.default_value != "":
            return {self.name: self.default_value}
        return {self.name: self.all_value}

    @property
    def yaml_section(self) -> str:
        """Yaml output."""
        if self.name in AUTOFIELDS:
            return ""
        dct = dict(self.out_dict)
        txt = yaml.dump(dct, Dumper=yaml.SafeDumper, default_flow_style=False).lstrip()
        lines = txt.split("\n")
        if self.is_array:
            lines[0] = f"{lines[0]} # Select Multiple"
        elif (
            self.allowed_values
            and self.default_value != self.allowed_values
            and len(self.allowed_values) != 1
        ):
            first = f"{lines[0]} # Select One"
            lines = [first]
            for i in self.allowed_values:
                lines.append(f"   {i}")
        return "\n".join(lines)

    @property
    def score(self) -> int:
        weight = 1000
        if self.required:
            weight -= 500
        if len(self.allowed_values) == 1:
            weight -= 200
        if (
            self.schema.get("type", "") == "user"
            or self.schema.get("items", "") == "user"
        ):
            weight -= 150
        if self.name in self.merge_values.keys():
            weight -= 100
        return weight


class JiraInterface:
    def __init__(
        self,
        cache_dir: Path,
        jira_url: str,
        debug: bool = False,
        merge_values: Dict[str, Any] = None,  # template merge values
    ) -> None:
        if merge_values is None:
            self.merge_values = {}
        else:
            self.merge_values = merge_values
        self.debug = debug
        self.cache_dir = cache_dir
        self.jira_url = jira_url
        self._inst = None

    @property
    def inst(self) -> jira.JIRA:
        if self._inst is None:
            self._inst = jira.JIRA(
                auth=(USER, PASS),
                options={"server": self.jira_url},
            )
        return self._inst

    def to_jira_dct(self, arg: Dict) -> Dict[str, Any]:
        """Convert to jira dict."""
        project = arg.pop("Project")
        issue_type = arg.pop("Issue Type")
        dmap = self.get_field_objects(project, issue_type)
        sub_map = {
            "project": {"key": project},
            "issuetype": {"name": issue_type},
        }
        field_dct = {field.name: field for field in dmap}
        errors = []
        for key, aval in arg.items():
            if not aval:
                errors.append(f"{project} {issue_type} {key} is empty")
        if errors:
            msg = "\n".join(errors)
            raise SystemExit(msg)

        for key, aval in arg.items():
            field = field_dct[key]
            if isinstance(aval, list) and not field.is_array:
                LOG.info("Operations: %s", field.operations)
                LOG.info("Schema: %s", field.schema)
                raise SystemExit(
                    f"{project} {issue_type} {key} is not an array, but {aval}"
                )
            if field.is_array:
                if field.allowed_values:
                    if field.is_user:
                        val = [{"name": v} for v in aval]
                    else:
                        val = [{"id": field.allowed_values[v]} for v in aval]
                else:
                    val = [v for v in aval]
            else:
                if field.allowed_values:
                    val = {"id": field.allowed_values[aval]}  # type: ignore
                else:
                    if field.is_user:
                        val = {"name": aval}
                    else:
                        val = aval
            sub_map[field.id] = val  # type: ignore
        return sub_map

    def submit(self, sub_map: Dict) -> str:
        """Submit."""
        if self.debug:
            LOG.info(
                "JSON Dump:\n%s", json.dumps(sub_map, indent=4, separators=(",", " : "))
            )
        return self.inst.create_issue(fields=sub_map, prefetch=True).key  # type: ignore

    def link_parent_issue(self, key: str, parent: str):
        """Link parent issue."""
        self.inst.create_issue_link(
            type="is parent task of",
            inwardIssue=parent,
            outwardIssue=key,
        )

    def put_spaces(self, text: str) -> str:
        """Put spaces in text."""
        lst = []
        for line in text.splitlines():
            if line.startswith("-"):
                lst.append(f"   {line}")
            else:
                lst.append(line)
        return "\n".join(lst)

    def template(self, project: str, issue_type: str) -> str:
        """Template."""
        dat = self.get_field_objects(project, issue_type)
        required = [f for f in dat if f.required]
        optional = [f for f in dat if not f.required]
        output = []
        output.append(
            "# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )
        output.append(
            "# !!!!!!!!!!!!!!!!! REMOVE THESE LINES AFTER EDIT !!!!!!!!!!!!!!!!!!!!!"
        )
        output.append(
            "# !!!!!!!! THIS IS TO PREVENT INSERTING UNEEDED VALID VALUES !!!!!!!!!!"
        )
        output.append(
            "# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        )
        output.append("# ---------------------------")
        output.append("# Required Fields:")
        output.append("# ---------------------------")
        for val in required:
            output.append(self.put_spaces(val.yaml_section))
        output.append("# ---------------------------")
        output.append("# Optional Fields:")
        output.append("# ---------------------------")
        for val in optional:
            ytxt = val.yaml_section
            for line in ytxt.splitlines():
                output.append(f"# {self.put_spaces(line.rstrip())}")
        return "\n".join(output)

    def get_field_objects(
        self,
        project_name: str,
        issue_name: str,
    ) -> List[Field]:
        """Get raw fields."""
        lst = []
        fpath = self.cache_dir / f"{project_name}_{issue_name}.json"
        if fpath.exists():
            LOG.info("Loading fields from cache from %s", fpath)
            with fpath.open() as f:
                dat = json.load(f)
        else:
            LOG.info("Fetching fields for %s", issue_name)
            dat = self.inst.createmeta(
                projectKeys=project_name,
                issuetypeNames=issue_name,
                expand="projects.issuetypes.fields",
            )
            with fpath.open("w") as f:
                json.dump(dat, f, indent=4)
        project = dat["projects"][0]  # type: ignore
        issuetype = project["issuetypes"][0]  # type: ignore
        fields = issuetype["fields"]  # type: ignore
        for val in fields.values():  # type: ignore
            field = Field(val, project_name, issue_name, self.merge_values)
            if field.ignore:
                continue
            lst.append(Field(val, project_name, issue_name, self.merge_values))
        return sorted(lst, key=lambda x: x.score)

    def __str__(self) -> str:
        return self.__dict__.__str__()
