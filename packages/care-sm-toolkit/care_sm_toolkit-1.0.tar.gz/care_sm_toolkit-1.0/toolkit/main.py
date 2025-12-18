import pandas as pd
import os
import logging
from datetime import datetime
from .template import TEMPLATE_MAP_OBO, TEMPLATE_MAP_SNOMED

logging.basicConfig(level=logging.INFO, force=True)


class Toolkit:
    # GLOBAL REMOVAL COUNTER
    removed_rows_total = 0

    keywords_OBO = {
        "Birthdate", "Birthyear", "Deathdate", "Sex", "Birthplace", "Status", "First_visit",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Examination", "Laboratory",
        "Genetic", "Disability", "Medication", "Surgery", "Hospitalization",
        "Consent", "Biobank", "Clinical_trial", "Cohort"
    }

    keywords_SNOMED = {
        "Birthdate", "Birthyear", "Deathdate", "Sex", "Birthplace", "Status", "First_visit",
        "Questionnaire", "Diagnosis", "Phenotype", "Symptoms_onset", "Examination", "Laboratory",
        "Genetic", "Disability", "Medication", "Surgery", "Hospitalization",
        "Biobank", "Clinical_trial", "Cohort"
    }

    columns = [
        "model", "pid", "event_id", "value", "age", "value_datatype", "valueIRI", "activity",
        "unit", "input", "target", "protocol_id", "specification", "frequency_type",
        "frequency_value", "agent", "startdate", "enddate", "comments", "organisation"
    ]

    drop_columns = ["value", "valueIRI", "target", "agent", "input", "activity", "unit"]

    columns_to_check = [
        "valueIRI", "activity", "unit", "input", "target",
        "frequency_type", "agent", "specification", "organisation"
    ]

    # UTILITIES
    @staticmethod
    def milisec():
        return datetime.now().strftime('%Y%m%d%H%M%S%f')

    def get_template(self, template_type):
        if template_type == "OBO":
            return TEMPLATE_MAP_OBO
        elif template_type == "SNOMED":
            return TEMPLATE_MAP_SNOMED
        raise ValueError(f"Template type '{template_type}' not recognized.")

    # CENTRALIZED REMOVAL LOGGER
    def _mark_row_for_removal(self, filepath, idx, reason, columns=None):
        self.removed_rows_total += 1
        col_info = f" | columns: {columns}" if columns else ""
        logging.info(
            f"[{os.path.basename(filepath)}] "
            f"Row {idx} removed | reason: {reason}{col_info}"
        )

    # MAIN PIPELINE
    def whole_method(self, folder_path, template_type):
        matching_files = self._find_matching_files(folder_path, template_type)
        processed = [self._process_file(file, template_type) for file in matching_files]
        final_df = pd.concat(processed, ignore_index=True) if processed else pd.DataFrame(columns=self.columns)
        final_df = self.delete_extra_columns(final_df)
        final_df.to_csv(os.path.join(folder_path, "CARE.csv"), index=False)

    def _find_matching_files(self, folder_path, template_type):
        keywords = self.keywords_OBO if template_type == "OBO" else self.keywords_SNOMED
        return [
            os.path.join(folder_path, file)
            for file in os.listdir(folder_path)
            if file.endswith(".csv") and any(k in file for k in keywords)
        ]

    def _process_file(self, filepath, template_type):
        df = self.import_your_data_from_csv(filepath)
        if df is None:
            return pd.DataFrame(columns=self.columns)

        df = self.check_status_column_names(df)
        df = self.add_columns_from_template(df, template_type)
        df = self.iri_validation(df, filepath)
        df = self.value_edition(df)
        df = self.time_edition(df)
        df = self.clean_empty_rows(df, filepath)
        df = self.unique_id_generation(df)
        df = self.normalize_numeric_columns(df)

        logging.info(f"Transformed: {os.path.basename(filepath)}")
        logging.info(f"TOTAL ROWS REMOVED ACROSS ALL FILES: {self.removed_rows_total}\n")
        self.removed_rows_total = 0

        return df

    # CSV HANDLING
    def import_your_data_from_csv(self, filepath):
        try:
            df = pd.read_csv(
                filepath,
                dtype={c: str for c in self.columns_to_check if c in pd.read_csv(filepath, nrows=0).columns}
            )
            logging.info(f"Imported CSV: {os.path.basename(filepath)}")
            return df
        except Exception as e:
            logging.error(f"Error loading CSV {filepath}: {e}")
            return None

    def check_status_column_names(self, df):
        extra = set(df.columns) - set(self.columns)
        if extra:
            raise ValueError(f"Unexpected columns: {extra}")
        for col in self.columns:
            if col not in df.columns:
                df[col] = pd.Series(dtype=object)
        return df

    def add_columns_from_template(self, df, template_type):
        template = self.get_template(template_type)
        rows = []
        for _, row in df.iterrows():
            base = {"model": row["model"]}
            base.update(template.get(row["model"], {}))
            base.update({k: v for k, v in row.items() if pd.notnull(v)})
            rows.append(base)
        return pd.DataFrame(rows)

    # IRI VALIDATION AND ROW REMOVAL
    def iri_validation(self, df, filepath):
        def is_valid_iri(v):
            return isinstance(v, str) and (v.startswith("http://") or v.startswith("https://"))

        rows_to_drop = []

        for idx, row in df.iterrows():
            for col in self.columns_to_check:
                val = row.get(col)
                if pd.isna(val) or str(val).strip() == "":
                    continue
                if not is_valid_iri(str(val).strip()):
                    self._mark_row_for_removal(
                        filepath, idx,
                        "Non-IRI value detected",
                        {col: val}
                    )
                    rows_to_drop.append(idx)
                    break

        return df.drop(index=rows_to_drop).reset_index(drop=True)
        
    def value_edition(self, df):
        def apply_value_types(row):
            model = row.get("model")
            val = row.get("value")
            dtype = row.get("value_datatype")

            # ---------- Literal values ----------
            if pd.notnull(val):
                if dtype == "xsd:string":
                    if model in [
                        "Diagnosis", "Phenotype", "Birthplace", "Genetic",
                        "Clinical_trial", "Cohort", "Biobank"
                    ]:
                        row["value_id_string"] = val
                    else:
                        row["value_string"] = val

                elif dtype == "xsd:float":
                    row["value_float"] = val

                elif dtype == "xsd:integer":
                    row["value_integer"] = val

                elif dtype == "xsd:date":
                    row["value_date"] = val

            # ---------- Dispatch maps ----------
            expected_valueIRI_models = {
                "attribute_type": ["Sex", "Status", "Examination"],
                "output_id": ["Diagnosis", "Phenotype", "Birthplace", "Genetic", "Clinical_trial", "Cohort", "Biobank"],
                "cause_id": ["Deathdate"],
                "output_type": ["Consent", "Medication"],
            }

            expected_target_models = {
                "target_id": ["Symptoms_onset", "Clinical_trial", "Cohort"],
                "target_type": ["Examination", "Laboratory", "Surgery", "Diagnosis", "Phenotype"],
            }

            expected_input_models = {
                "input_type": ["Laboratory", "Genetic", "Biobank"],
                "input_id": ["Questionnaire", "Disability"],
            }

            expected_agent_models = {
                "attribute_type": ["Genetic"],
                "input_id": ["Medication"],
            }

            expected_activity_models = {
                "specific_method_type": [
                    "Examination", "Laboratory", "Genetic",
                    "Medication", "Hospitalization", "Surgery"
                ]
            }

            expected_unit_models = {
                "unit_type": self.keywords_OBO
            }

            # ---------- Dispatcher ----------
            def dispatch(column, value, expected_map):
                if pd.isnull(value):
                    return

                for new_col, valid_models in expected_map.items():
                    if model in valid_models:
                        row[new_col] = value
                        return

                logging.info(
                    f"Unexpected value in '{column}' for model '{model}': {value}"
                )

            # ---------- Apply dispatchers ----------
            dispatch("valueIRI", row.get("valueIRI"), expected_valueIRI_models)
            dispatch("target", row.get("target"), expected_target_models)
            dispatch("input", row.get("input"), expected_input_models)
            dispatch("agent", row.get("agent"), expected_agent_models)
            dispatch("activity", row.get("activity"), expected_activity_models)
            dispatch("unit", row.get("unit"), expected_unit_models)

            return row

        return df.apply(apply_value_types, axis=1)


    # EMPTY ROWS AND ROW REMOVAL
    def clean_empty_rows(self, df, filepath):
        required = ["value", "valueIRI", "activity", "target", "agent"]
        rows_to_drop = []

        for idx, row in df.iterrows():
            if row[required].isnull().all():
                self._mark_row_for_removal(
                    filepath, idx,
                    "Insufficient data (all required columns empty)"
                )
                rows_to_drop.append(idx)

        return df.drop(index=rows_to_drop).reset_index(drop=True)

    # FINAL STEPS
    def time_edition(self, df):
        if "startdate" in df and "enddate" in df:
            df["enddate"] = df["enddate"].where(df["enddate"].notna(), df["startdate"])
        return df

    def delete_extra_columns(self, df):
        return df.drop(columns=[c for c in self.drop_columns if c in df.columns], errors="ignore")

    def unique_id_generation(self, df):
        ts = self.milisec()
        df["uniqid"] = [f"{ts}{i}" for i in range(len(df))]
        return df
    
    def normalize_numeric_columns(self, df):
        """
        Force integer-like columns to use pandas nullable Int64 dtype
        to avoid 30 -> 30.0 caused by NaN values.
        """
        int_columns = [
            "age",
            "value_integer",
            "frequency_value",
            "pid",
            "event_id"
        ]

        for col in int_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

        return df