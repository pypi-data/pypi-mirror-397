"""
Configuration models for review forms.

Follows GitHub's form schema structure:
https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema
"""

from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class FormFieldType(str, Enum):
    CHECKBOXES = "checkboxes"
    DROPDOWN = "dropdown"
    INPUT = "input"
    TEXTAREA = "textarea"


class CheckboxOption(BaseModel):
    """A single checkbox option within a checkboxes field."""

    model_config = ConfigDict(extra="forbid")

    label: str = Field(min_length=1)
    required: bool = False
    value: bool = False  # Whether this checkbox is checked


class FormFieldBase(BaseModel):
    """Base class for form fields."""

    model_config = ConfigDict(extra="forbid")

    type: FormFieldType
    label: str = ""
    description: str = ""


class CheckboxesField(FormFieldBase):
    """Multiple attestation checkboxes."""

    type: Literal["checkboxes"]
    label: str = Field(min_length=1)
    options: list[CheckboxOption] = Field(min_length=1)


class DropdownField(FormFieldBase):
    """Single-select dropdown."""

    type: Literal["dropdown"]
    label: str = Field(min_length=1)
    options: list[str] = Field(min_length=1)
    required: bool = False
    value: str | None = None


class InputField(FormFieldBase):
    """Single-line text input."""

    type: Literal["input"]
    label: str = Field(min_length=1)
    placeholder: str = ""
    required: bool = False
    value: str = ""


class TextareaField(FormFieldBase):
    """Multi-line text input."""

    type: Literal["textarea"]
    label: str = Field(min_length=1)
    placeholder: str = ""
    required: bool = False
    value: str = ""


# Union type for all field types
FormField = CheckboxesField | DropdownField | InputField | TextareaField


class ScopeFormModel(BaseModel):
    """Configuration for review forms."""

    model_config = ConfigDict(extra="forbid")

    fields: list[FormField] = Field(min_length=1)

    @field_validator("fields", mode="before")
    @classmethod
    def parse_fields(cls, fields: list[dict[str, Any] | FormField]) -> list[FormField]:
        """Parse field dicts into appropriate field types based on 'type' key."""
        parsed = []
        for field_data in fields:
            # Already a FormField instance, pass through
            if isinstance(
                field_data, CheckboxesField | DropdownField | InputField | TextareaField
            ):
                parsed.append(field_data)
                continue

            field_type = field_data.get("type")
            match field_type:
                case "checkboxes":
                    parsed.append(CheckboxesField(**field_data))
                case "dropdown":
                    parsed.append(DropdownField(**field_data))
                case "input":
                    parsed.append(InputField(**field_data))
                case "textarea":
                    parsed.append(TextareaField(**field_data))
                case _:
                    raise ValueError(f"Unknown form field type: {field_type}")
        return parsed

    def compute_hash(self) -> str:
        """Compute deterministic hash of form definition.

        Only includes semantic attributes that define the "form contract":
        - type, label, required, options
        Excludes presentational attributes:
        - description, placeholder, value
        """
        serialized: list[dict[str, Any]] = []
        for f in self.fields:
            field_dict = f.model_dump() if not isinstance(f, dict) else f
            # Extract only semantic attributes
            semantic: dict[str, Any] = {
                "type": field_dict["type"],
                "label": field_dict["label"],
            }
            if "required" in field_dict:
                semantic["required"] = field_dict["required"]
            if "options" in field_dict:
                # For checkboxes, extract label and required from each option
                if field_dict["type"] == "checkboxes":
                    semantic["options"] = [
                        {"label": opt["label"], "required": opt.get("required", False)}
                        for opt in field_dict["options"]
                    ]
                else:
                    # For dropdown, options is just a list of strings
                    semantic["options"] = field_dict["options"]
            serialized.append(semantic)
        canonical = json.dumps(serialized, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
