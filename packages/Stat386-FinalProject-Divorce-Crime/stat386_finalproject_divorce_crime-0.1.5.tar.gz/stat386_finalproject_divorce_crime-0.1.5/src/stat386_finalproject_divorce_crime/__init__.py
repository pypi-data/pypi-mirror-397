from stat386_finalproject_divorce_crime import wrangling, clean_data, analysis
from .wrangling import load_data, load_offense_mapping, get_census_data, get_fbi_data, save_to_csv, save_to_parquet
from .clean_data import main
from .analysis import national_aggregate, linear_regression_by_crime_rate, linear_regression_by_marriage_divorce, histogram_maker