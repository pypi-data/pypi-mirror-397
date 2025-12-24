"""Utility functions for slangweb."""

import ast
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_model_folder(model_name: str) -> str:
    """Get the name of the model folder for the given model name."""
    return f"models--{model_name.replace('/', '--')}"


def available_languages(models_lookup_file: Path, models_folder: Path) -> dict[str, str]:
    """Return a list of available languages based on existing lookup files and model existence."""
    if not models_lookup_file.exists():
        logger.error(
            f"Models lookup file '{models_lookup_file}' does not exist. Create it by running 'slangweb generate-models-lookup-file'."
        )
        return {}
    with open(models_lookup_file, "r", encoding="utf-8") as f:
        models_lookup = json.load(f)
    languages = []
    lang_expanded = []
    for language, data in models_lookup.items():
        file = data.get("model")
        if not file:
            continue
        lang_expanded.append(data.get("name", language))
        model_folder = get_model_folder(file)
        model_path = models_folder / model_folder
        if model_path.exists() and model_path.is_dir():
            languages.append(language)
    return dict(zip(languages, lang_expanded))


def find_translator_usages(py_file: Path, translator_class: str = "SW") -> list[str]:
    """Find usages of the Translator class in the given Python file.

    Args:
        py_file (Path): Path to the Python file to analyze.
        translator_class (str): Name of the translator class to look for. Default is "SW".
    """
    with open(py_file, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=py_file)
    usages = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and hasattr(node.func, "id")
            and node.func.id == translator_class
        ):
            if node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Str):
                    usages.append(str(arg.s))
                elif isinstance(arg, ast.Name):
                    usages.append(str(arg.id))
                else:
                    usages.append(str(ast.dump(arg)))
    return usages
