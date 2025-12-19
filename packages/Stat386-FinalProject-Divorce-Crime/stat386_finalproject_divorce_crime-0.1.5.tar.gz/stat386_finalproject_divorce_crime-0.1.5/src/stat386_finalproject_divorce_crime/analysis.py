import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def _plot_hist(df, col, title, x_label):
    fig, ax = plt.subplots()
    ax.hist(df[col].dropna(), bins=40)
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel("Frequency")
    return fig

def national_aggregate(df : pd.DataFrame) -> pd.DataFrame:
    """
    Creates national-level trends:
    - Averages rate variables
    - Sums actual count variables
    """ 
    Rate_vars = [col for col in df.columns if "_rate" in col or col in ['marriage_rate_per_1000','divorce_rate_per_1000']]
    Actual_vars = [col for col in df.columns if "_actual" in col or col in ['married_last_year','divorced_last_year','population','participated_population','population_over_15']]
    
    # Aggregate 
    agg_dict = {var: "mean" for var in Rate_vars}
    agg_dict.update({var: "sum" for var in Actual_vars})

    # Aggregate dataframe
    national_df = (
        df
        .groupby("year", as_index=False)
        .agg(agg_dict)
    )
    
    # Return Dataframe
    return national_df



def linear_regression_by_crime_rate(df: pd.DataFrame, crime: str):

    # Define variables used in model
    vars_needed = [
        crime,
        "marriage_rate_per_1000",
        "divorce_rate_per_1000",
        "state",
        "year"
    ]

    # Drop missing rows FIRST
    df_model = (
        df[vars_needed]
        .dropna()
        .sort_values(["state", "year"])
        .copy()
    )

    model = smf.ols(
        f"{crime} ~ marriage_rate_per_1000 + divorce_rate_per_1000 + C(state) + C(year)",
        data=df_model
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_model["state"]}
    )

    return model


def linear_regression_by_marriage_divorce(
    df: pd.DataFrame,
    marriage_true: bool
):
    if marriage_true:
        outcome = "marriage_rate_per_1000"
        rate_vars = ["LAR_rate", "RPE_rate"]
    else:
        outcome = "divorce_rate_per_1000"
        rate_vars = ["BUR_rate", "ARS_rate"]

    vars_needed = [outcome] + rate_vars + ["state", "year"]

    # DROP NAs FIRST
    df_model = (
        df[vars_needed]
        .dropna()
        .sort_values(["state", "year"])
        .copy()
    )

    rhs = " + ".join(rate_vars + ["C(state)", "C(year)"])
    formula = f"{outcome} ~ {rhs}"

    model = smf.ols(
        formula,
        data=df_model
    ).fit(
        cov_type="cluster",
        cov_kwds={"groups": df_model["state"]}
    )

    return model

# Create Histogram
def histogram_maker(
    df: pd.DataFrame,
    column: str,
    title: str,
    x_label: str,
):
    """
    Create a histogram for a given dataframe column
    """
    return _plot_hist(
        df=df,
        col=column,
        title=title,
        x_label=x_label
    )

def lasso_family_structure_with_state_year(
    df: pd.DataFrame,
    target: str
):
    """
    LASSO regression predicting marriage or divorce rates
    using violent crime rate variables + year + state.
    """


    CRIME_RATE_VARS = [
        "V_rate",
        "HOM_rate",
        "ASS_rate",
        "ROB_rate",
        "RPE_rate",
        "ARS_rate",
        "P_rate"
    ]


    FEATURES_NUMERIC = CRIME_RATE_VARS + ["year"]
    FEATURES_CATEGORICAL = ["state"]


    cols_needed = FEATURES_NUMERIC + FEATURES_CATEGORICAL + [target]
    data = df[cols_needed].dropna()


    X = data[FEATURES_NUMERIC + FEATURES_CATEGORICAL]
    y = data[target]


    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), FEATURES_NUMERIC),
            ("state", OneHotEncoder(drop="first", sparse_output=False),
             FEATURES_CATEGORICAL)
        ]
    )


    model = Pipeline([
        ("prep", preprocessor),
        ("lasso", LassoCV(
            cv=5,
            random_state=42,
            max_iter=10000
        ))
    ])


    model.fit(X, y)


    # Extract coefficients with names
    feature_names = (
        FEATURES_NUMERIC +
        list(model.named_steps["prep"]
             .named_transformers_["state"]
             .get_feature_names_out(["state"]))
    )


    coefs = pd.Series(
        model.named_steps["lasso"].coef_,
        index=feature_names
    )


    return model, coefs[coefs != 0].sort_values(key=abs, ascending=False)
