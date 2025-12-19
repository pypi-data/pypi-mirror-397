from pathlib import Path
import pandas as pd
from stat386_finalproject_divorce_crime.wrangling import load_data

def load_all_data(census_data_file: str | Path, crime_data_file: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads in marriage and divorce data as well as crime data

    Parameters
    ----------
    census_data_file : str | Path
    crime_data_file : str | Path

    Returns
    ----------
    tuple[pd.DataFrame, pd.DataFrame] # marriage and divorce, and crime respectively
    """
    census_data = load_data(census_data_file)
    crime_data = load_data(crime_data_file)
    return census_data, crime_data


def clean_crime_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans FBI Crime Dataframe

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    ----------
    pd.DataFrame
    """

    df['month_year_dt'] = pd.to_datetime(df['month_year'])
    df['year'] = df['month_year_dt'].dt.year

    # Define which columns are counts vs rates
    count_cols = [col for col in df.columns if "_actual" in col]
    rate_cols = [col for col in df.columns if "_rate" in col or col in ['population','participated_population']]

    agg_dict = {col: 'sum' for col in count_cols}
    agg_dict.update({col: 'mean' for col in rate_cols})

    crime_annual = df.groupby(['state','year']).agg(agg_dict).reset_index()

    return crime_annual

def convert_cols_to_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Converts columns listed in cols to a numeric data type

    Parameters
    ----------
    df: pd.DataFrame
    cols: list[str]

    Return
    ----------
    pd.DataFrame
    """
    df1 = df.copy()
    for col in cols:
        df1[col] = pd.to_numeric(df1[col], errors='coerce')

    return df1

def clean_census_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in the raw census data and cleans it up

    Parameters
    ----------
    df: pd.DataFrame

    Return
    ----------
    pd.DataFrame
    """
    cols_to_convert = [
        "population_over_15",
        "married_males_last_year",
        "married_females_last_year",
        "divorced_males_last_year",
        "divorced_females_last_year"
    ]
    df = convert_cols_to_numeric(df, cols_to_convert)

    # Compute totals
    df["married_last_year"] = (
        df["married_males_last_year"] +
        df["married_females_last_year"]
    )

    df["divorced_last_year"] = (
        df["divorced_males_last_year"] +
        df["divorced_females_last_year"]
    )

    # Marriage rate per 1,000
    df['marriage_rate_per_1000'] = (df['married_last_year'] / df['population_over_15']) * 1000

    # Divorce rate per 1,000
    df['divorce_rate_per_1000'] = (df['divorced_last_year'] / df['population_over_15']) * 1000

    final_df = df[['state','year','married_last_year','marriage_rate_per_1000',
          'divorced_last_year','divorce_rate_per_1000','population_over_15']]
    
    return final_df


def merge_data(census_df : pd.DataFrame, crime_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the census data and the crime data and merges them into one pandas dataframe

    Parameters
    ----------
    census_df : pd.DataFrame
    crime_df : pd.DataFrame

    Returns
    ----------
    pd.DataFrame
    """

    # Only include years that are in marriage/divorce data
    years_to_keep = census_df['year'].unique()
    crime_df = crime_df[crime_df['year'].isin(years_to_keep)].reset_index(drop=True)

    combined_df = pd.merge(
        crime_df,
        census_df,
        on=['state','year'],
        how='inner'  # only keep states & years present in both
    )

    return combined_df

def main(census_file: str | Path, crime_file: str | Path) -> pd.DataFrame:
    """
    Loads in data, cleans it, and merges it

    Parameters
    ----------
    census_data_file : str | Path
    crime_data_file : str | Path

    Return
    ----------
    pd.DataFrame
    """

    census_df, crime_df = load_all_data(census_file, crime_file)
    census_cleaned = clean_census_data(census_df)
    crime_cleaned = clean_crime_data(crime_df)
    df = merge_data(census_cleaned, crime_cleaned)
    return df

# if __name__ == "__main__":
#     df = main("Stat386-FinalProject-Divorce-Crime/src/data/mardiv.csv", "Stat386-FinalProject-Divorce-Crime/src/data/summarized_fbi_data.parquet")
#     print(df.head())