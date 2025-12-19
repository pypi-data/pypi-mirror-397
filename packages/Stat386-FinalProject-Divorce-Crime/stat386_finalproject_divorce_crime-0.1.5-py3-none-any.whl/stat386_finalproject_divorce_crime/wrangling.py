from pathlib import Path
import pandas as pd
import json
from dotenv import load_dotenv
import os
import re
from datetime import datetime
import requests
import time

def save_to_csv(df: pd.DataFrame, location: str, file_name: str) -> None:
    """
    Saves a pandas dataframe to a csv file

    Parameters
    ----------
    df: pd.DataFrame
    location: str
    file_name: str

    Return
    ----------
    None
    """
    if not file_name.endswith(".csv"):
        raise ValueError("File_name must end in .csv")
    if location.endswith("/"):
        key = f"{location}{file_name}"
    else:
        key = f"{location}/{file_name}"
    df.to_csv(key)

def save_to_parquet(df: pd.DataFrame, location: str, file_name: str) -> None:
    """
    Saves a pandas dataframe to a parquet file

    Parameters
    ----------
    df: pd.DataFrame
    location: str
    file_name: str

    Return
    ----------
    None
    """
    if not file_name.endswith(".parquet"):
        raise ValueError("File_name must end in .parquet")
    if location.endswith("/"):
        key = f"{location}{file_name}"
    else:
        key = f"{location}/{file_name}"
    df.to_parquet(key)

def load_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load data from a file

    Parameters
    ----------
    file_path : str or Path

    Returns 
    ----------
    pd.DataFrame
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix == ".parquet":
        return pd.read_parquet(path)
    else:
        raise ValueError("File must be a .csv or .parquet file")


def load_offense_mapping(json_path: str | Path) -> dict:
    """
    Load crime offense mapping json

    Parameters
    ----------
    json_path : str or Path

    Returns 
    ----------
    dict
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, 'r') as file:
            crime_json = json.load(file)
            offense_map = crime_json["offenses"]
            return offense_map
    else:
        raise ValueError("File must be a .json file")

def load_json(json_path: str | Path) -> dict:
    """
    Load json

    Parameters
    ----------
    json_path : str or Path

    Returns 
    ----------
    dict
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    
    suffix = path.suffix.lower()
    if suffix == ".json":
        with open(path, 'r') as file:
            data = json.load(file)
            return data
    else:
        raise ValueError("File must be a .json file")
    
def validate_period(start: str, end: str):
    """
    Validate that start and end are in mm-yyyy format,
    start is after 01-1985, and end is no later than today.
    """
    pattern = r"^(0[1-9]|1[0-2])-\d{4}$"

    # Format check
    for label, value in [("start", start), ("end", end)]:
        if not re.match(pattern, value):
            raise ValueError(f"{label} must be in mm-yyyy format, got {value}")

    # Parse into datetime (first day of month)
    start_dt = datetime.strptime(start, "%m-%Y")
    end_dt = datetime.strptime(end, "%m-%Y")

    # Constraint checks
    cutoff = datetime(1985, 1)
    if start_dt <= cutoff:
        raise ValueError(f"Start {start} must be after cutoff {cutoff.strftime('%m-%Y')}")

    today = datetime.today().replace(day=1)  # normalize to month start
    if end_dt > today:
        raise ValueError(f"End {end} must be no later than {today.strftime('%m-%Y')}")

    return True

def flatten_crime_json_with_clearances(data, crime, states=None):
    """
    Flatten FBI CDE JSON into a DataFrame including state clearance rates and actuals.
    """
    # Extract blocks
    rates_all = data["offenses"]["rates"]
    actuals_all = data["offenses"]["actuals"]
    population_all = data["populations"]["population"]
    participated_all = data["populations"]["participated_population"]
    
    rows = []
    
    # Filter states: ignore US totals, keep real states
    if not states:
        states = [s for s in rates_all.keys() if "Clearances" not in s and s != "United States"]
    
    for state in states:
        rates = rates_all.get(state, {})
        actuals = actuals_all.get(state, {})
        rates_clear = rates_all.get(f"{state} Clearances", {})
        actuals_clear = actuals_all.get(f"{state} Clearances", {})
        pop = population_all.get(state, {})
        part_pop = participated_all.get(state, {})
        
        for month_year in rates.keys():
            row = {
                "state": state,
                "month_year": pd.to_datetime(month_year, format="%m-%Y"),
                f"{crime}_rate": rates.get(month_year),
                f"{crime}_actual": actuals.get(month_year),
                f"{crime}_clearance_rate": rates_clear.get(month_year),
                f"{crime}_clearance_actual": actuals_clear.get(month_year),
                "population": pop.get(month_year),
                "participated_population": part_pop.get(month_year)
            }
            rows.append(row)
    
    df = pd.DataFrame(rows)
    return df


def get_fbi_data(key_name: str, start: str, end: str) -> pd.DataFrame:
    """
    Calls the FBI Crime Data Explorer API and collects data into a parquet file, starting at start and ending at end
    This function requires that you have an API Key registered with the FBI and stored in a .env file
    
    Parameters
    ----------
    key_name : str
    start : str
    end : str
    
    Returns
    ----------
    pd.DataFrame
    """
    validate_period(start, end)

    load_dotenv() # Looks for a .env file in the current directory
    api_key = os.getenv(key_name)
    if api_key is None:
        raise EnvironmentError(f"Environment file not found: {api_key}")

    states = load_json("../json/states.json")['states']
    statenames = load_json("../json/state_names.json")['states']
    crimes = load_json("../json/crime_abbr.json")['offenses']
    crime_abbrs = crimes.keys()

    df = pd.DataFrame()
    first = True
    for st, state_name in zip(states, statenames):
        for crime in crime_abbrs:
            url = f"https://api.usa.gov/crime/fbi/cde/summarized/state/{st}/{crime}?from={start}&to={end}&API_KEY={api_key}"
            response = requests.get(url)
            response_json = response.json()
            df_state = flatten_crime_json_with_clearances(response_json, crime, states=[state_name])
            if first:
                df = df_state.copy()
                first = False
            else:
                df_combined = pd.merge(
                    df,
                    df_state,
                    on=["state", "month_year", "population", "participated_population"],
                    how="outer"  # use outer if some months exist in one but not the other
                )
                df = df_combined.copy()

            time.sleep(2)

    return df
    
def get_census_data(key_name: str, start: int, end: int) -> pd.DataFrame:
    """
    Calls the US Census Data API and collects data into a csv file, starting at start and ending at end
    This function requires that you have an API Key registered with the US Census Bureau and stored in a .env file
    
    Parameters
    ----------
    key_name : str
    start : int
    end : sinttr
    
    Returns
    ----------
    pd.DataFrame
    """
    load_dotenv() # Looks for a .env file in the current directory
    api_key = os.getenv(key_name)
    if api_key is None:
        raise EnvironmentError(f"Environment file not found: {api_key}")

    years = range(start, end)
    all_data = []
    for year in years:
        url = f"https://api.census.gov/data/{year}/acs/acs1"
        params = {
            "get": "NAME,B12501_001E,B12501_005E,B12501_010E,B12503_005E,B12503_010E",
            "for": "state:*",
            "key": api_key
        }

        response = requests.get(url, params=params)

        try:
            data = response.json()
        except ValueError:
            print(f"{year}: JSON failed -- skipped")
            continue

        df = pd.DataFrame(data[1:], columns=data[0])
        df['year'] = year

        all_data.append(df)

    final_df = pd.DataFrame()
    final_df = pd.concat(all_data, ignore_index=True)
    final_df = final_df.rename(columns={
        "state": "state_num",
        "NAME": "state",
        "B12501_001E": "population_over_15",
        "B12501_005E": "married_males_last_year",
        "B12501_010E": "married_females_last_year",
        "B12503_005E": "divorced_males_last_year",
        "B12503_010E": "divorced_females_last_year"
    })

    return final_df

