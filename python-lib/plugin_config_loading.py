# -*- coding: utf-8 -*-
import logging
from typing import Dict

from language_dict import SUPPORTED_LANGUAGES


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
    params["fallback_language"] = recipe_config.get("fallback_language", "")
    if params["fallback_language"] == "":
        logging.info("No fallback language")
    else:
        logging.info("Fallback language: {}".format(params["fallback_language"]))
    return params
