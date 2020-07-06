from language_dict import language_dict

def do(payload, config, plugin_config, inputs):
    choices = language_dict()
    return {"choices": choices}