# -*- coding: utf-8 -*-
from language_dict import SUPPORTED_LANGUAGES


def do(payload, config, plugin_config, inputs):
    language_choices = SUPPORTED_LANGUAGES
    if payload["parameterName"] == "fallback_language":
        language_choices.insert(0, {"label": "None", "value": "None"})
    return {"choices": language_choices}
