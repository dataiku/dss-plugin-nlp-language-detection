# -*- coding: utf-8 -*-
from plugin_config_loading import load_plugin_config
from language_detection import LanguageDetector

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
