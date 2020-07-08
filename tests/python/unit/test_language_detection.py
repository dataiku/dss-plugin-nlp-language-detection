# -*- coding: utf-8 -*-
# This is a test file intended to be used with pytest
# pytest automatically runs all the function starting with "test_"
# see https://docs.pytest.org for more information

import os
import sys
from pathlib import Path


# Add python-lib to the path to enable exec outside of DSS
plugin_root_path = Path(__file__).parents[3]
sys.path.append(os.path.join(plugin_root_path, "python-lib"))
from language_detection import LanguageDetector  # noqa

# TODO
