# -*- coding: utf-8 -*-
import dataiku
from dataiku.customrecipe import get_input_names_for_role, get_output_names_for_role, get_recipe_config
from input_output_params import load_params
from language_detection import LanguageDetector
from plugin_io_utils import process_dataset_chunks, set_column_description

# Setup
input_dataset = dataiku.Dataset(get_input_names_for_role("input_dataset")[0])
output_dataset = dataiku.Dataset(get_output_names_for_role("output_dataset")[0])
params = load_params(get_recipe_config())
detector = LanguageDetector(
    language_scope=params["language_scope"],
    minimum_score=params["minimum_score"],
    fallback_language=params["fallback_language"],
)

# Run
process_dataset_chunks(
    input_dataset=input_dataset,
    output_dataset=output_dataset,
    func=detector.detect_languages_df,
    text_column=params["text_column"],
)
set_column_description(
    input_dataset=input_dataset, output_dataset=output_dataset, column_description_dict=detector.output_column_dict,
)
