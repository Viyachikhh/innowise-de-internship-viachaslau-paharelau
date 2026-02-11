import polars as pl

class LogAggregator:

    def __init__(self, *error_type_list):
        self.error_checks = []
        for el in error_type_list:
            self.error_checks.append(el)

    def extract_fields(self, **kw_file_df):
        result = []
        for name, df in kw_file_df.items():
            error_lists = [check.extract_critical(df, name) for check in self.error_checks]
            result.extend(error_lists)
        return pl.concat(result).to_dicts()
    
    def __repr__(self):
        return str(self.error_checks)