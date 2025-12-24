"""Translations in Dash applications.

Only translates from English to other languages for now.
"""

import json
import os
from logging import getLogger
from pathlib import Path

from transformers import MarianMTModel, MarianTokenizer

from .constants import (
    DEFAULT_LANGUAGE,
    ENCODING,
    LOOKUPS_FOLDER,
    MODELS_FOLDER,
    MODELS_LOOKUP_FILE,
    SLANG_FOLDER,
)

logger = getLogger(__name__)


def lang_from_path(path: str) -> str | None:
    """Extract the language code from the given URL path."""
    parts = (path or "").strip("/").split("/")
    return parts[0] if parts else DEFAULT_LANGUAGE


class Translator:
    """A simple translator class to manage translations."""

    def __init__(
        self,
        base_folder: str = SLANG_FOLDER,
        models_folder: str = MODELS_FOLDER,
        lookup_folder: str = LOOKUPS_FOLDER,
        models_lookup_file: str = MODELS_LOOKUP_FILE,
    ):
        """Initialize the Translator.

        There are 2 kind of lookup files:
        1. Models lookup file: maps language codes to model names.
        2. Translation lookup files: per-language files that map source texts to translated texts.

        If the model lookup file does not exist, it must be created using the cli tool.

        >slangweb generate-models-lookup-file

        Args:
            base_folder (Path): Base directory for slangweb data.
            models_folder (Path): Directory to store/load translation models.
            lookup_folder (Path): Directory to store/load translation lookups.
            models_lookup_file (Path): Path to the models configuration file.
        """
        here = Path(os.getcwd())
        self.language: str | None = None
        self.base_folder = here / base_folder
        self.models_folder = here / base_folder / models_folder
        self.lookup_folder = here / base_folder / lookup_folder
        self.models_lookup_file = here / base_folder / models_lookup_file
        self._models_lookup: dict | None = None
        self._translation_lookup_file: Path | None = None
        self._model = None
        self._tokenizer = None

    def set_language(self, language: str | None) -> None:
        """Set the current language for translation."""
        language = language.lower() if language else None
        if self.language != language:
            self.language = language
            # reset model and tokenizer
            self._model = None
            self._tokenizer = None

    @property
    def models_lookup(self) -> dict:
        """Load the models configuration from the models file."""
        if not self.models_lookup_file.exists():
            logger.error(f"Models lookup file not found: {self.models_lookup_file}")
            return {}
        if self._models_lookup is None:
            with open(self.models_lookup_file, "r", encoding="utf-8") as f:
                models = json.load(f)
            self._models_lookup = models
        return self._models_lookup | {}

    @property
    def model_name(self) -> str | None:
        """Get the model name for the current language."""
        model_name = self.models_lookup.get(self.language, {}).get("model")
        if not model_name:
            logger.warning(f"Language '{self.language}' not found in models lookup.")
        return model_name

    def is_language_in_lookup(self) -> bool:
        """Check if the current language is in the lookup file."""
        if self.language is None or self.language == DEFAULT_LANGUAGE:
            return False
        is_in_lookup = self.language in self.models_lookup
        if not is_in_lookup:
            logger.error(f"Language '{self.language}' not found in models lookup.")
        return is_in_lookup

    @property
    def model_filename(self) -> Path | None:
        """Get the model directory for the current language."""
        if self.model_name is None:
            return None
        model_fn = self.models_folder / f"models--{self.model_name.replace('/', '--')}"
        return model_fn

    def is_model_available(self) -> bool:
        """Check if the model for the current language is available."""
        model_fn = self.model_filename
        if model_fn is None:
            return False
        return model_fn.is_dir()

    @property
    def translation_lookup_file(self) -> Path:
        """Get the translation lookup file for the current language."""
        fn = self.lookup_folder / f"{self.language}.json"
        if not fn.exists():
            logger.info(f"Creating new lookup file: {fn}")
            fn.parent.mkdir(parents=True, exist_ok=True)
            with open(fn, "w", encoding=ENCODING) as f:
                json.dump({}, f, indent=4, ensure_ascii=False)
        return fn

    @property
    def translation_lookup(self) -> dict:
        """Get the translation lookup for the current language."""
        with open(self.translation_lookup_file, "r", encoding=ENCODING) as f:
            lookup = json.load(f)
        return lookup

    def get_tokenizer(self) -> MarianTokenizer | None:
        """Get the tokenizer for the current language."""
        if self._tokenizer is not None:
            return self._tokenizer

        if self.is_model_available() and self.is_language_in_lookup():
            self._tokenizer = MarianTokenizer.from_pretrained(
                self.model_name, cache_dir=self.models_folder, local_files_only=True
            )
            return self._tokenizer
        else:
            return None

    def get_model(self) -> MarianMTModel | None:
        """Get the translation model for the current language."""
        if self._model is not None:
            return self._model

        if self.is_model_available() and self.is_language_in_lookup():
            import torch

            # Disable low_cpu_mem_usage to avoid meta device
            self._model = MarianMTModel.from_pretrained(
                self.model_name,
                cache_dir=self.models_folder,
                local_files_only=True,
                dtype=torch.float32,
                low_cpu_mem_usage=False,
            )
            return self._model
        else:
            return None

    def can_be_translated(self) -> bool:
        """Check if the current language can be translated."""
        # exit: no language set
        if self.language is None:
            logger.warning("No language set. Make sure to set it using 'set_language' method.")
            return False

        # exit: default language
        if self.language == DEFAULT_LANGUAGE:
            logger.info(f"Default language set ({self.language}), no translation needed.")
            return False

        # exit: model lookup file missing
        if not self.models_lookup_file.exists():
            logger.error(
                f"Models lookup file not found: {self.models_lookup_file}. Create using the CLI application."
            )
            return False

        # exit: model not available
        if not self.is_model_available():
            logger.error(
                f"Model for language '{self.language}' not available. Download it using the CLI application."
            )
            return False

        return True

    def translate(self, text: str) -> str:
        """Translate the given text to the current language, directly using the model.

        Since this is the main function, check related to translation using the model will be performed here.

        Args:
            text (str): The text to translate.
        """
        if not self.can_be_translated():
            return text

        try:
            # translate using model
            tokenizer = self.get_tokenizer()
            model = self.get_model()
            if tokenizer is None or model is None:
                logger.error("Tokenizer or model not available for translation.")
                return text
            if self.model_name == "Helsinki-NLP/opus-mt-en-ROMANCE":
                # for romance languages, lowercase the text to improve results
                tgt_lang = f">>{self.language}<<"
                inputs = tokenizer(f"{tgt_lang} {text}", return_tensors="pt", padding=True)
            else:
                inputs = tokenizer(text, return_tensors="pt", padding=True)
            translated = model.generate(**inputs)
            tgt_text = [tokenizer.decode(t, skip_special_tokens=True) for t in translated]
            translation = tgt_text[0] if tgt_text else ""
            return translation
        except Exception as e:
            logger.error(f"Error during translation: {e}")
            return text

    def get_translation_from_lookup(self, text: str) -> str | None:
        """Get translation from the lookup file.

        Since this is a main function, check related to the lookup file will be performed here.

        Args:
            text (str): The text to translate.
        """
        if not self.can_be_translated():
            return text
        return self.translation_lookup.get(text)

    def save_translation(self, text: str, translated_text: str) -> None:
        """Save the translated text to the lookup file."""
        with open(self.translation_lookup_file, "r", encoding=ENCODING) as f:
            lookup = json.load(f)
        lookup[text] = translated_text
        with open(self.translation_lookup_file, "w", encoding=ENCODING) as f:
            json.dump(lookup, f, indent=4, ensure_ascii=False)

    def get_translation(self, text: str) -> str:
        """Get translation from lookup or translate and save it to lookup.

        Args:
            text (str): The text to translate.
        """
        translation = self.get_translation_from_lookup(text)
        if translation == text:
            return text
        if translation is None:  # not found in lookup
            translation = self.translate(text)
            # update lookup file
            self.save_translation(text, translation)
        return translation

    def __call__(self, text: str) -> str:
        """Translate the given text using the translator instance."""
        logger.debug(f"Translating text: {text}")
        return self.get_translation(text)
