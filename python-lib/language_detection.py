# -*- coding: utf-8 -*-
import logging
from typing import List, AnyStr

from langid.langid import LanguageIdentifier, model
import cld3
import pandas as pd

from language_dict import SUPPORTED_LANGUAGES, LANGUAGE_REMAPPING

# from plugin_io_utils import generate_unique

supported_languages_dict = {k["value"]: k["label"] for k in SUPPORTED_LANGUAGES}


class LanguageDetector:

    LANGID_CLD3_NUM_CHAR_THRESHOLD = 140

    def __init__(
        self,
        language_scope: List = supported_languages_dict.keys(),
        minimum_score: float = 0.0,
        fallback_language: AnyStr = "",
    ):
        self.language_scope = language_scope
        self.minimum_score = float(minimum_score)
        self.fallback_language = fallback_language
        self._langid_identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        self._langid_identifier.set_languages(self.language_scope)

    def _langid_detection(self, doc: AnyStr):
        language_detection_object = self.identifier.classify(doc)
        lang_id = language_detection_object[0][:2]
        lang_probability = language_detection_object[1]
        return lang_id, lang_probability

    def _cld3_detection(self, doc: AnyStr):
        language_detection_object = cld3.get_language(doc)
        lang_id = language_detection_object.language[:2]
        for original_code, new_code in LANGUAGE_REMAPPING.items():  # to make cld3 compatible with langid
            lang_id = lang_id.replace(original_code, new_code)
        lang_probability = language_detection_object.probability
        return lang_id, lang_probability

    def detect_language_doc(self, doc: AnyStr):
        # Route to langid or cld3 depending on number of characters
        if len(doc) <= self.LANGID_CLD3_NUM_CHAR_THRESHOLD:
            lang_id, lang_probability = self._langid_detection(doc)
        else:
            lang_id, lang_probability = self._cld3_detection(doc)
        # Filters for language scope and minimum scores
        if lang_probability < self.minimum_score or lang_id not in self.language_scope:
            logging.warn("[PLUGIN] Problem encountered for document: {}".format(doc))
            if lang_id not in self.language_scope:
                logging.warn(
                    "[PLUGIN] Detected language: {} not within language scope: {}".format(lang_id, self.language_scope)
                )
            else:
                logging.warn(
                    "[PLUGIN] Confidence score: {:.2f} below minimum: {:.2f}".format(
                        lang_probability, self.minimum_score
                    )
                )
            logging.warn("Replacing detected language: {} by fallback: {}".format(lang_id, self.fallback_language))
            lang_id, lang_probability = self.fallback_language, None
        return lang_id, lang_probability

    def detect_languages_df(self, df: pd.DataFrame, text_column: AnyStr):
        # TODO refactoring
        return df
