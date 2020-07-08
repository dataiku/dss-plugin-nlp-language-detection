# -*- coding: utf-8 -*-
import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role, get_recipe_config
from input_output_params import load_params
from language_detection import LanguageDetector

# Setup
input_dataset = get_input_names_for_role("input_dataset")[0]
output_dataset = get_output_names_for_role("output_dataset")[0]
recipe_config = get_recipe_config()
params = load_params(recipe_config)

# Run
df = dataiku.Dataset(input_dataset).get_dataframe()
language_detector = LanguageDetector(
    language_scope=params["language_scope"],
    minimum_score=params["minimum_score"],
    fallback_language=params["fallback_language"],
)
output_df = language_detector.detect_languages_df(df, params["text_column"])

# Write output
output = dataiku.Dataset(output_dataset)
output.write_with_schema(output_df)
