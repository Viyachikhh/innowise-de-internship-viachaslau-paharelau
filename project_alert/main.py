from pathlib import Path

from src.df_preparation import reading, preparation
from src.rules import BaseErrorCheck, BaseBundleErrorCheck
from src.log_aggregator import LogAggregator


def main():
    folder_elements = list(Path("logs/source/").rglob("*.csv"))
    folder_elements = [str(path) for path in folder_elements]

    names = [path.split('/')[-1] for path in folder_elements]
    dfs = [preparation(reading(path)) for path in folder_elements]
    dicts = dict(zip(names, dfs))
    # print(dicts)
    aggregator = LogAggregator(BaseErrorCheck, BaseBundleErrorCheck)
    # print(aggregator)
    error_list = aggregator.extract_fields(**dicts)

    print(error_list[0])




if __name__ == "__main__":
    main()