import dataiku
from dataiku.customrecipe import get_recipe_config
from input_output_params import get_input_output, get_params
from language_detection import LanguageDetector

# Setup
input_dataset, output_dataset = get_input_output()
recipe_config = get_recipe_config()
params = get_params(recipe_config)

# Run
df = dataiku.Dataset(input_dataset).get_dataframe()
language_detector = LanguageDetector(params)
output_df = language_detector.compute(df)

# Write output
output = dataiku.Dataset(output_dataset)
output.write_with_schema(output_df)
