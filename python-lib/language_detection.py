# -*- coding: utf-8 -*-
import logging
from typing import List, AnyStr
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
import cld3
from langid.langid import LanguageIdentifier, model

from language_dict import SUPPORTED_LANGUAGES, SUPPORTED_LANGUAGES_IN_CLD3_NOT_IN_LANGID, LANGUAGE_REMAPPING

from plugin_io_utils import generate_unique

supported_languages_dict = {k["value"]: k["label"] for k in SUPPORTED_LANGUAGES}


class LanguageDetector:
    """
    Language detection wrapper class on top of cld3 and langid, with additional features:
    - Route to cld3 for documents with more than 140 characters, else langid
    - Harmonize small differences between cld3 and langid language scopes
    - Add filter on language scope and minimum confidence score, else replace detection by fallback
    """

    LANGID_CLD3_NUM_CHAR_THRESHOLD = 140
    NUM_THREADS = 4
    COLUMN_DESCRIPTION_DICT = {
        "language_code": "Language code in ISO 639-1 format",
        "language_name": "Language name in ISO 639-1 format",
        "language_score": "Confidence score from 0 to 1",
    }

    def __init__(
        self,
        language_scope: List = supported_languages_dict.keys(),
        minimum_score: float = 0.0,
        fallback_language: AnyStr = "",
    ):
        self.language_scope = language_scope
        self.minimum_score = float(minimum_score)
        self.fallback_language = fallback_language
        self.column_description_dict = self.COLUMN_DESCRIPTION_DICT  # changed when calling detect_languages_df
        self._langid_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        self._langid_identifier.set_languages(
            [l for l in self.language_scope if l not in SUPPORTED_LANGUAGES_IN_CLD3_NOT_IN_LANGID]
        )

    def _langid_detection(self, doc: AnyStr) -> (AnyStr, float):
        language_detection_object = self._langid_identifier.classify(doc)
        lang_id = language_detection_object[0][:2]
        lang_probability = float(language_detection_object[1])
        return (lang_id, lang_probability)

    def _cld3_detection(self, doc: AnyStr) -> (AnyStr, float):
        language_detection_object = cld3.get_language(doc)
        lang_id = language_detection_object.language[:2]
        for original_code, new_code in LANGUAGE_REMAPPING.items():  # make cld3 compatible with langid
            lang_id = lang_id.replace(original_code, new_code)
        lang_probability = float(language_detection_object.probability)
        return (lang_id, lang_probability)

    def _detection_filter(self, doc: AnyStr, lang_id: AnyStr, lang_probability: float) -> (AnyStr, float):
        if lang_probability < self.minimum_score or lang_id not in self.language_scope:
            warning_msg = "Problem encountered for document: '{}'.\n".format(doc)
            if lang_id not in self.language_scope:
                warning_msg += "Detected language: '{}' not within language scope: {}.\n".format(
                    lang_id, self.language_scope
                )
            else:
                warning_msg += "Confidence score: {:.2f} below minimum: {:.2f}.\n".format(
                    lang_probability, self.minimum_score
                )
            warning_msg += "Replacing detected language: '{}' by fallback: '{}'.".format(
                lang_id, self.fallback_language
            )
            logging.warning(warning_msg)
            lang_id, lang_probability = self.fallback_language, None
        return (lang_id, lang_probability)

    def detect_language_doc(self, doc: AnyStr) -> (AnyStr, AnyStr, float):
        # Route to langid or cld3 depending on number of characters
        if doc is None or doc == "":
            return ("", "", None)
        if len(doc) <= self.LANGID_CLD3_NUM_CHAR_THRESHOLD:
            lang_id, lang_probability = self._langid_detection(doc)
        else:
            lang_id, lang_probability = self._cld3_detection(doc)
        # Filters for language scope and minimum scores
        lang_id, lang_probability = self._detection_filter(doc, lang_id, lang_probability)
        # Enrich with language human name
        lang_name = supported_languages_dict.get(lang_id, "")
        return (lang_id, lang_name, lang_probability)

    def detect_languages_df(self, df: pd.DataFrame, text_column: AnyStr) -> pd.DataFrame:
        self.output_column_dict = {
            generate_unique(k, df.keys(), text_column): v for k, v in self.COLUMN_DESCRIPTION_DICT.items()
        }
        doc_iterator = (doc for _, doc in df[text_column].astype(str).iteritems())
        with ThreadPoolExecutor(max_workers=self.NUM_THREADS) as executor:
            lang_output_tuple_list = list(executor.map(self.detect_language_doc, doc_iterator))
        for i, col in enumerate(self.output_column_dict.keys()):
            df[col] = [t[i] for t in lang_output_tuple_list]
        return df
