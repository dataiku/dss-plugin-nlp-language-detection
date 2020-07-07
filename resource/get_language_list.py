from language_dict import SUPPORTED_LANGUAGES


def do(payload, config, plugin_config, inputs):
    return {"choices": SUPPORTED_LANGUAGES}
