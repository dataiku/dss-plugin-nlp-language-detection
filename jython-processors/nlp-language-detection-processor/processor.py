# -*- coding: utf-8 -*-

"""
Need to define all classes, functions directly here, because
a processor component cannot load python-lib modules in DSS 7.0.
This issue is fixed in DSS 8.0.
"""

import logging
from typing import Dict, List, AnyStr
from collections import OrderedDict

import cld3
from langid.langid import LanguageIdentifier, model

SUPPORTED_LANGUAGES = [
    {"label": "Afrikaans", "value": "af"},
    {"label": "Albanian", "value": "sq"},
    {"label": "Amharic", "value": "am"},
    {"label": "Arabic", "value": "ar"},
    {"label": "Aragonese", "value": "an"},
    {"label": "Armenian", "value": "hy"},
    {"label": "Assamese", "value": "as"},
    {"label": "Azerbaijani", "value": "az"},
    {"label": "Basque", "value": "eu"},
    {"label": "Belarusian", "value": "be"},
    {"label": "Bengali", "value": "bn"},
    {"label": "Bosnian", "value": "bs"},
    {"label": "Breton", "value": "br"},
    {"label": "Bulgarian", "value": "bg"},
    {"label": "Burmese", "value": "my"},
    {"label": "Catalan", "value": "ca"},
    {"label": "Central Khmer", "value": "km"},
    {"label": "Chinese", "value": "zh"},
    {"label": "Croatian", "value": "hr"},
    {"label": "Czech", "value": "cs"},
    {"label": "Danish", "value": "da"},
    {"label": "Dutch", "value": "nl"},
    {"label": "Dzongkha", "value": "dz"},
    {"label": "English", "value": "en"},
    {"label": "Esperanto", "value": "eo"},
    {"label": "Estonian", "value": "et"},
    {"label": "Faroese", "value": "fo"},
    {"label": "Finnish", "value": "fi"},
    {"label": "French", "value": "fr"},
    {"label": "Galician", "value": "gl"},
    {"label": "Georgian", "value": "ka"},
    {"label": "German", "value": "de"},
    {"label": "Greek", "value": "el"},
    {"label": "Gujarati", "value": "gu"},
    {"label": "Haitian", "value": "ht"},
    {"label": "Hausa", "value": "ha"},
    {"label": "Hebrew", "value": "he"},
    {"label": "Hindi", "value": "hi"},
    {"label": "Hungarian", "value": "hu"},
    {"label": "Icelandic", "value": "is"},
    {"label": "Igbo", "value": "ig"},
    {"label": "Indonesian", "value": "id"},
    {"label": "Irish", "value": "ga"},
    {"label": "Italian", "value": "it"},
    {"label": "Japanese", "value": "ja"},
    {"label": "Javanese", "value": "jv"},
    {"label": "Kannada", "value": "kn"},
    {"label": "Kazakh", "value": "kk"},
    {"label": "Kinyarwanda", "value": "rw"},
    {"label": "Kirghiz", "value": "ky"},
    {"label": "Korean", "value": "ko"},
    {"label": "Kurdish", "value": "ku"},
    {"label": "Lao", "value": "lo"},
    {"label": "Latin", "value": "la"},
    {"label": "Latvian", "value": "lv"},
    {"label": "Lithuanian", "value": "lt"},
    {"label": "Luxembourgish", "value": "lb"},
    {"label": "Macedonian", "value": "mk"},
    {"label": "Malagasy", "value": "mg"},
    {"label": "Malay", "value": "ms"},
    {"label": "Malayalam", "value": "ml"},
    {"label": "Maltese", "value": "mt"},
    {"label": "Maori", "value": "mi"},
    {"label": "Marathi", "value": "mr"},
    {"label": "Mongolian", "value": "mn"},
    {"label": "Nepali", "value": "ne"},
    {"label": "Northern Sami", "value": "se"},
    {"label": "Norwegian Bokmål", "value": "nb"},
    {"label": "Norwegian Nynorsk", "value": "nn"},
    {"label": "Norwegian", "value": "no"},
    {"label": "Nyanja", "value": "ny"},
    {"label": "Occitan", "value": "oc"},
    {"label": "Oriya", "value": "or"},
    {"label": "Panjabi", "value": "pa"},
    {"label": "Persian", "value": "fa"},
    {"label": "Polish", "value": "pl"},
    {"label": "Portuguese", "value": "pt"},
    {"label": "Pushto", "value": "ps"},
    {"label": "Quechua", "value": "qu"},
    {"label": "Romanian", "value": "ro"},
    {"label": "Russian", "value": "ru"},
    {"label": "Samoan", "value": "sm"},
    {"label": "Scottish Gaelic", "value": "gd"},
    {"label": "Serbian", "value": "sr"},
    {"label": "Shona", "value": "sn"},
    {"label": "Sindhi", "value": "sd"},
    {"label": "Sinhala", "value": "si"},
    {"label": "Slovak", "value": "sk"},
    {"label": "Slovenian", "value": "sl"},
    {"label": "Somali", "value": "so"},
    {"label": "Southern Sotho", "value": "st"},
    {"label": "Spanish", "value": "es"},
    {"label": "Sundanese", "value": "su"},
    {"label": "Swahili", "value": "sw"},
    {"label": "Swedish", "value": "sv"},
    {"label": "Tagalog", "value": "tl"},
    {"label": "Tajik", "value": "tg"},
    {"label": "Tamil", "value": "ta"},
    {"label": "Telugu", "value": "te"},
    {"label": "Thai", "value": "th"},
    {"label": "Turkish", "value": "tr"},
    {"label": "Uighur", "value": "ug"},
    {"label": "Ukrainian", "value": "uk"},
    {"label": "Urdu", "value": "ur"},
    {"label": "Uzbek", "value": "uz"},
    {"label": "Vietnamese", "value": "vi"},
    {"label": "Volapük", "value": "vo"},
    {"label": "Walloon", "value": "wa"},
    {"label": "Welsh", "value": "cy"},
    {"label": "Western Frisian", "value": "fy"},
    {"label": "Xhosa", "value": "xh"},
    {"label": "Yiddish", "value": "yi"},
    {"label": "Yoruba", "value": "yo"},
    {"label": "Zulu", "value": "zu"},
]

SUPPORTED_LANGUAGES_IN_CLD3_NOT_IN_LANGID = [
    "fy",
    "gd",
    "ha",
    "ig",
    "mi",
    "my",
    "ny",
    "sd",
    "sm",
    "sn",
    "so",
    "st",
    "su",
    "tg",
    "uz",
    "yi",
    "yo",
]

# Rare cases of ISO code replacements and oddities
LANGUAGE_REMAPPING = {"iw": "he", "co": "it", "ji": "yi", "in": "id"}


def load_plugin_config(recipe_config: Dict) -> Dict:
    """
    Helper function to load plugin recipe config into a clean parameter dictionary.
    Applies assertion checks for correct input config.
    """
    params = {}
    # Text column
    params["text_column"] = recipe_config.get("text_column")
    assert params["text_column"] is not None and params["text_column"] != ""
    logging.info("Text column: {}".format(params["text_column"]))
    # Language scope
    params["language_scope"] = recipe_config.get("language_scope", [])
    if len(params["language_scope"]) == 0:
        params["language_scope"] = [l.get("value") for l in SUPPORTED_LANGUAGES]
    assert len(params["language_scope"]) != 0
    logging.info("Scope of {:d} languages: {}".format(len(params["language_scope"]), params["language_scope"]))
    # Minimum score
    params["minimum_score"] = float(recipe_config.get("minimum_score"))
    assert params["minimum_score"] >= 0 and params["minimum_score"] <= 1
    if params["minimum_score"] == 0:
        logging.info("No minimum score for detection")
    else:
        logging.info("Minimum score for detection: {:.2f}".format(params["minimum_score"]))
    # Fallback language
    params["fallback_language"] = recipe_config.get("fallback_language")
    if params["fallback_language"] is None or params["fallback_language"] == "None":
        logging.info("No fallback language")
        params["fallback_language"] = ""
    else:
        logging.info("Fallback language: {}".format(params["fallback_language"]))
    return params


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
    COLUMN_DESCRIPTION_DICT = OrderedDict(
        [
            ("language_code", "Language code in ISO 639-1 format"),
            ("language_name", "Language name in ISO 639-1 format"),
            ("language_score", "Confidence score from 0 to 1"),
        ]
    )

    def __init__(
        self,
        language_scope: List = supported_languages_dict.keys(),
        minimum_score: float = 0.0,
        fallback_language: AnyStr = "",
    ):
        self.language_scope = language_scope
        self.minimum_score = float(minimum_score)
        self.fallback_language = fallback_language
        self.column_description_dict = self.COLUMN_DESCRIPTION_DICT  # may be changed by detect_languages_df
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
        # Round probability to 3 decimals
        lang_probability = round(lang_probability, 3) if lang_probability else None
        return (lang_id, lang_name, lang_probability)


# Setup
params = load_plugin_config(params)  # noqa
detector = LanguageDetector(
    language_scope=params["language_scope"],
    minimum_score=params["minimum_score"],
    fallback_language=params["fallback_language"],
)


def process(row):
    text_column = params["text_column"]
    doc = str(row[text_column])
    new_cols = ["{}_{}".format(text_column, k) for k in detector.COLUMN_DESCRIPTION_DICT.keys()]
    (lang_id, lang_name, lang_probability) = detector.detect_language_doc(doc)
    row[new_cols[0]] = lang_id
    row[new_cols[1]] = lang_name
    row[new_cols[2]] = lang_probability
    return row
