import polars as pl
from abc import ABC, abstractmethod

class AbstractRuleCheck(ABC):

    @classmethod
    @abstractmethod
    def check(self):
        pass

    @abstractmethod   
    def __repr__(self):
        pass



class BaseErrorCheck(AbstractRuleCheck):

    @classmethod
    def check(self, df):
        # извлекаем записи с ошибками
        df_errors = df.filter(pl.col("severity").is_in(["Error", "Fatal"]))
        # используем дату из unix, т.к. она более точная
        grouped = df_errors.group_by_dynamic("date_from_unix", every="1m", label="left")
        # группы, количество записей которых больше 10 
        grouped = grouped.having(pl.len() > 10)
        # статистика
        stat = grouped.agg(pl.len().alias("common_error_count"),
                            pl.col("bundle_id").unique().alias("unique_error_bundle_list"),
                            pl.col("log_location").unique().alias("unique_log_location")).sort("common_error_count")
        stat = stat.with_columns(pl.col("date_from_unix").alias("field"))[["field", "unique_log_location","common_error_count"]]
        return stat.to_dicts()

    def __repr__(self):
        return "At least 10 records within 1m-interval"
        




class BaseBundleErrorCheck(AbstractRuleCheck):


    @classmethod
    def check(self, df):
        # извлекаем записи с ошибками
        df_errors = df.filter(pl.col("severity").is_in(["Error", "Fatal"]))
        # используем дату из unix, т.к. она более точная, также учитывая bundle_id
        grouped = df_errors.group_by_dynamic("date_from_unix", every="1h", label="left", group_by="bundle_id")
        # группы, количество записей которых больше 10 
        grouped = grouped.having(pl.len() > 10)
        # статистика
        stat = grouped.agg(pl.len().alias("common_error_count"),
                                    pl.col("bundle_id").unique().alias("unique_error_bundle_list"),
                                    pl.col("log_location").unique().alias("unique_log_location")).sort("common_error_count")

        stat = stat.with_columns(pl.concat_str([pl.col("bundle_id"), 
                                                pl.col("date_from_unix")], 
                                                separator=" ").alias("field"))[["field",
                                                                                 "unique_log_location",
                                                                                 "common_error_count"]]
        return stat.to_dicts()


            

    def __repr__(self):
        return "At least 10 records within 1h-interval inside bundle_id"