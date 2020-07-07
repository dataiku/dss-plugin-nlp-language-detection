from language_dict import SUPPORTED_LANGUAGES, LANGUAGE_REMAPPING
from langid.langid import LanguageIdentifier, model
import cld3
import pandas as pd

language_code_dict = {k["value"]: k["label"] for k in SUPPORTED_LANGUAGES}


class LanguageDetector:
    def __init__(self, params):
        self.params = params
        self.identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

        if self.params["constraint_languages"]:
            self.identifier.set_languages(self.params["constrained_languages"])

    def _get_language_name_from_id(self, lang_id):
        return language_code_dict.get(lang_id, "")

    def _confidence_level_check(self, lang_id, lang_probability):

        if lang_probability < self.params["confidence_level"] / 100.0:
            lang_id = self.params["fallback_output"]
            lang_name = self._get_language_name_from_id(self.params["fallback_output"])
            return self._to_pdSeries(lang_id, lang_name, lang_probability)

        else:
            return self._to_pdSeries(lang_id, self._get_language_name_from_id(lang_id), lang_probability)

    def _to_pdSeries(self, lang_id, lang_name, lang_probability):
        # passing to pd.Series enables to create multiple columns with .apply
        return pd.Series(
            {
                self.col + "_lang_id": lang_id,
                self.col + "_lang_name": lang_name,
                self.col + "_lang_confidence": lang_probability,
            }
        )

    def _langid_detection(self, doc):
        language_detection_object = self.identifier.classify(doc)
        lang_id = language_detection_object[0][:2]
        lang_probability = language_detection_object[1]

        return self._confidence_level_check(lang_id, lang_probability)

    def _cld3_detection(self, doc):
        language_detection_object = cld3.get_language(doc)
        lang_id = language_detection_object.language[:2]
        for original_code, new_code in LANGUAGE_REMAPPING.items():
            lang_id = lang_id.replace(original_code, new_code)
        lang_probability = language_detection_object.probability

        return self._confidence_level_check(lang_id, lang_probability)

    def _get_language_from_doc(self, doc):
        if self.params["constraint_languages"]:
            return self._langid_detection(doc)

        if len(doc) <= 140:  # tweet
            return self._langid_detection(doc)
        else:
            return self._cld3_detection(doc)

    def compute(self, df):
        for col in self.params["text_col_list"]:
            self.col = col
            df = pd.concat([df, df[col].apply(lambda x: self._get_language_from_doc(str(x)))], axis=1)

        return df
