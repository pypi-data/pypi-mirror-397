"""Pylint checker for Django model scanning."""

from typing import Any, Dict, Optional
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter
from astroid import nodes

from .ast_utils import is_django_model
from .model_parser import parse_model, merge_abstract_fields
from .export import export_to_yaml


class DjangoModelChecker(BaseChecker):
    """Pylint checker that scans Django models and exports to YAML.

    This checker visits all class definitions, identifies Django models,
    parses their structure, and exports the collected data to YAML.

    Usage:
        pylint project_path --load-plugins=django_model_scanner.checker --disable=all
    """

    name = "django-model-scanner"
    priority = -1  # Run last to ensure all files are processed

    # No messages - we're only collecting data, not reporting issues
    msgs: Dict[str, Any] = {
        "C8888": (
            "Scanned Django models and exported to YAML",
            "django-model-scanner",
            "Used to scan Django models and export their structure to a YAML file.",
        ),
    }

    options = (
        (
            "django-models-output",
            {
                "default": "django_models.yaml",
                "type": "string",
                "metavar": "<file>",
                "help": "Output file path for Django models YAML",
            },
        ),
        (
            "django-models-verbose",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Enable verbose output for debugging",
            },
        ),
    )

    def __init__(self, linter: Optional[PyLinter] = None) -> None:
        """Initialize the checker.

        Args:
            linter: Pylint linter instance
        """
        super().__init__(linter)
        self.models: Dict[str, Dict[str, Any]] = {}
        self.class_nodes: Dict[str, nodes.ClassDef] = {}

    def visit_classdef(self, node: nodes.ClassDef) -> None:
        """Visit a class definition node.

        If the class is a Django model, parse it and store in the models dict.

        Args:
            node: Astroid ClassDef node
        """
        # Check if this is a Django model
        if not is_django_model(node):
            return

        # Get the fully qualified name
        model_qname = node.qname()

        if self.linter and self.linter.config.django_models_verbose:
            print(f"Found Django model: {model_qname}")

        try:
            # Parse the model
            model_data = parse_model(node)
            self.models[model_qname] = model_data
            self.class_nodes[model_qname] = node
        except Exception as e:
            if self.linter and self.linter.config.django_models_verbose:
                print(f"Error parsing model {model_qname}: {e}")

    def close(self) -> None:
        """Called after all files have been processed.

        Performs second pass to merge abstract inheritance and exports to YAML.
        """
        if not self.models:
            if self.linter and self.linter.config.django_models_verbose:
                print("No Django models found")
            return

        # Second pass: merge abstract inheritance
        if self.linter and self.linter.config.django_models_verbose:
            print(f"\nProcessing {len(self.models)} models for inheritance...")

        for model_qname, model_data in self.models.items():
            try:
                merge_abstract_fields(model_data, self.models)
            except Exception as e:
                if self.linter and self.linter.config.django_models_verbose:
                    print(f"Error merging inheritance for {model_qname}: {e}")

        # Export to YAML
        output_path = "django_models.yaml"
        if self.linter and hasattr(self.linter.config, "django_models_output"):
            output_path = self.linter.config.django_models_output

        try:
            export_to_yaml(self.models, output_path)
            if self.linter and self.linter.config.django_models_verbose:
                print(f"\nExported {len(self.models)} models to {output_path}")
            else:
                print(f"Django models exported to {output_path}")
        except Exception as e:
            print(f"Error exporting models: {e}")


def register(linter: PyLinter) -> None:
    """Register the checker with pylint.

    Args:
        linter: Pylint linter instance
    """
    linter.register_checker(DjangoModelChecker(linter))
