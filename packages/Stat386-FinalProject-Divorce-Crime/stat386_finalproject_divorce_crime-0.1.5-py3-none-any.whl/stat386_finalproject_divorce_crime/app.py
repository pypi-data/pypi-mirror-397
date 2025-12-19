import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

from wrangling import load_data, load_offense_mapping
from analysis import national_aggregate, histogram_maker, linear_regression_by_crime_rate, linear_regression_by_marriage_divorce


def select_df(df: pd.DataFrame):
    """
    Sidebar selector for State vs National dataframe
    Returns dataframe and is_national flag
    """
    choice = st.sidebar.radio(
        "Select Data Group",
        ["State", "National"]
    )

    if choice == "State":
        return df, False
    return national_aggregate(df), True

def display_regression_results(model, outcome_name: str):
    st.subheader(f"Regression Results: {outcome_name}")

    coef_table = model.summary2().tables[1]

    # Remove fixed effects
    coef_table = coef_table.loc[
        ~coef_table.index.str.startswith("C(")
    ]

    st.markdown("### Key Coefficients")
    st.dataframe(coef_table.style.format("{:.4f}"))

    # Model stats
    col1, col2, col3 = st.columns(3)
    col1.metric("R²", f"{model.rsquared:.3f}")
    col2.metric("Observations", int(model.nobs))
    col3.metric(
        "Clusters (States)",
        model.cov_kwds["groups"].nunique()
    )

    # Interpretation (automatic)
    st.markdown("### Interpretation")
    for var, row in coef_table.iterrows():
        st.write(
            f"- A one-unit increase in **{var}** is associated with a "
            f"**{row['Coef.']:.3f} change** in {outcome_name}, "
            "holding state and year fixed."
        )

    with st.expander("Full regression output"):
        st.text(model.summary())


def main():
    st.title("Discovering the Relationship Between Divorce and Crime")

    # Load data
    df_state = load_data("src/data/Combined_DF.csv")

    offense_map = load_offense_mapping("src/json/crime_abbr.json")
    name_to_code = {v: k for k, v in offense_map.items()}

    # ---------------- Sidebar controls ----------------
    show_model = st.sidebar.checkbox("Show Regression Model")

    if show_model:
        crime_name = st.sidebar.selectbox(
            "Select Crime",
            sorted(name_to_code.keys())
        )
        crime_code = name_to_code[crime_name]

        metric = st.sidebar.radio(
            "Select Metric",
            ["Actual", "Rate"]
        )
        
        if not crime_code.endswith(metric.lower()):
            crime_col = f"{crime_code}_{metric.lower()}"
        else:
            crime_col = crime_code

        marriage_divorce = st.sidebar.radio(
            "Select to Compare Marriage or Divorce Statistics",
            ['Marriage', 'Divorce']
        )
        model_radio = st.sidebar.radio(
            "Select a Model",
            ["Crime ~ marriage + divorce", "Marriage ~ Crime", "Divorce ~ Crime"]
        )
        if model_radio == "Crime ~ marriage + divorce":
            model = linear_regression_by_crime_rate(
                df=df_state,   # always use full state panel
                crime=crime_col
            )
        elif model_radio == "Marriage ~ Crime":
            model = linear_regression_by_marriage_divorce(
                df=df_state,   # always use full state panel
                marriage_true=True
            )
        elif model_radio == "Divorce ~ Crime":
            model = linear_regression_by_marriage_divorce(
                df=df_state,   # always use full state panel
                marriage_true=False
            )
        display_regression_results(model, crime_name)
    else:

        df, is_national = select_df(df_state)

        plot_type = st.sidebar.radio(
            "Select Plot Type",
            ["Line", "Histogram"]
        )

        marriage_divorce = st.sidebar.radio(
            "Select to Compare Marriage or Divorce Statistics",
            ['Marriage', 'Divorce']
        )

        metric = st.sidebar.radio(
            "Select Metric",
            ["Actual", "Rate"]
        )
        metric_label = "Rate" if metric == "Rate" else "Number"
        if marriage_divorce == "Marriage" and metric == "Actual":
            md_col = f"married_last_year"
            md_name = "Marriages"
        elif marriage_divorce == "Divorce" and metric == "Actual":
            md_col = f"divorced_last_year"
            md_name = "Divorces"
        elif marriage_divorce == "Marriage" and metric == "Rate":
            md_col = f"marriage_rate_per_1000"
            md_name = "Marriages"
        elif marriage_divorce == "Divorce" and metric == "Rate":
            md_col = f"divorce_rate_per_1000"
            md_name = "Divorces"

        crime_name = st.sidebar.selectbox(
            "Select Crime",
            sorted(name_to_code.keys())
        )
        crime_code = name_to_code[crime_name]
        
        if not crime_code.endswith(metric.lower()):
            crime_col = f"{crime_code}_{metric.lower()}"
        else:
            crime_col = crime_code

        state = None
        if not is_national:
            state = st.sidebar.selectbox(
                "Select State",
                sorted(df["state"].dropna().unique())
            )
            df = df[df["state"] == state]

        df = df.sort_values("year")

        # ---------------- Plot logic ----------------
        if plot_type == "Line":
            fig, ax1 = plt.subplots()

            ax1.plot(
                df["year"],
                df[crime_col],
                label=f"{crime_name} ({metric})"
            )
            ax1.set_xlabel("Year")
            ax1.set_ylabel(f"{metric} {crime_name}")

            ax2 = ax1.twinx()
            ax2.plot(
                df["year"],
                df[md_col],
                label=md_name,
                linestyle="-",
                color="red"
            )
            ax2.set_ylabel(f"{metric_label} of {md_name}")

            title_loc = state if state else "United States"
            ax1.set_title(f"{crime_name} vs {md_name} ({title_loc})")

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

        else:  # Histogram
            x_label = "Rate" if metric == "Rate" else "Count"
            t = f"Distribution of {crime_name} ({metric})"
            if not is_national:
                t += f" ({state})"
            else:
                t += " (Nationally)"

            fig = histogram_maker(
                df=df,
                column=crime_col,
                title=t,
                x_label=x_label
            )
        st.pyplot(fig)


if __name__ == "__main__":
    main()
