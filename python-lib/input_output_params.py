from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role


def get_input_output():
    input_dataset = get_input_names_for_role("input_dataset")[0]
    output_dataset = get_output_names_for_role("output_dataset")[0]

    return input_dataset, output_dataset


def get_params(recipe_config):
    def _p(param_name, default=None):
        return recipe_config.get(param_name, default)

    params = {}

    # General parameters
    params["text_col_list"] = _p("text_col_list")

    # Language parameters
    params["language"] = _p("language")
    params["detect_language"] = _p("detect_language")

    if _p("expert"):
        params["constrained_languages"] = _p("constrained_languages")

        if len(params["constrained_languages"]) > 0:
            params["constraint_languages"] = True
        else:
            params["constraint_languages"] = False

        params["confidence_level"] = _p("confidence_level")
        params["fallback_output"] = _p("fallback_output")

        params["confidence_level"] = 0
        params["confidence_level_required"] = False

    else:
        params["constrained_languages"] = []
        params["constraint_languages"] = False
        params["confidence_level"] = 0
        params["confidence_level_required"] = False

    return params
