# -*- coding: utf-8 -*-
import logging
import math
from typing import List, Dict, AnyStr, Callable
from tqdm import tqdm

import dataiku


def generate_unique(name: AnyStr, existing_names: List[AnyStr], prefix: AnyStr = None) -> AnyStr:
    """
    Generate a unique name among existing ones by suffixing a number. Can also add a prefix.
    """
    new_name = "{}_{}".format(prefix, name)
    for i in range(1001):
        if new_name not in existing_names:
            return new_name
        new_name = "{}_{}_{}".format(prefix, name, i)
    raise Exception("Failed to generated a unique name")


def count_records(dataset: dataiku.Dataset) -> int:
    """
    Count the number of records of a dataset by streaming the first column.
    Not the most efficient implementation but simpler than the dataset metrics API.
    """
    first_column_name = dataset.read_schema()[0]["name"]
    df = dataset.get_dataframe(columns=[first_column_name], infer_with_pandas=False)
    count_records = len(df.index)
    assert count_records > 0
    return count_records


def process_dataset_chunks(
    input_dataset: dataiku.Dataset, output_dataset: dataiku.Dataset, func: Callable, chunksize: float = 10000, **kwargs
) -> None:
    """
    Read a dataset by chunks, process each dataframe chunk with a function and write back to another dataset.
    Automatically adds a tqdm progress bar and generic logging.
    """
    logging.info("Processing dataframe chunks of size {:d})...".format(chunksize))
    with output_dataset.get_writer() as writer:
        df_iterator = input_dataset.iter_dataframes(chunksize=chunksize, infer_with_pandas=False)
        len_iterator = math.ceil(count_records(input_dataset) / chunksize)
        for i, df in tqdm(enumerate(df_iterator), total=len_iterator):
            output_df = func(df=df, **kwargs)
            if i == 0:
                output_dataset.write_schema_from_dataframe(output_df, dropAndCreate=True)
            writer.write_dataframe(output_df)
    logging.info("Processing dataframe chunks: Done!")


def set_column_description(
    input_dataset: dataiku.Dataset, output_dataset: dataiku.Dataset, column_description_dict: Dict,
) -> None:
    """
    Set column descriptions of the output dataset based on a dictionary of column descriptions
    and retains the column descriptions from the input dataset if the column name matches
    """
    input_dataset_schema = input_dataset.read_schema()
    output_dataset_schema = output_dataset.read_schema()
    input_columns_names = [col["name"] for col in input_dataset_schema]
    for output_col_info in output_dataset_schema:
        output_col_name = output_col_info.get("name", "")
        output_col_info["comment"] = column_description_dict.get(output_col_name)
        if output_col_name in input_columns_names:
            matched_comment = [
                input_col_info.get("comment", "")
                for input_col_info in input_dataset_schema
                if input_col_info.get("name") == output_col_name
            ]
            if len(matched_comment) != 0:
                output_col_info["comment"] = matched_comment[0]
    output_dataset.write_schema(output_dataset_schema)
