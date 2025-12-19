import pandas as pd
import numpy as np
from datetime import datetime



def create_full_calendar_and_interpolate(
        master_data,
        group_columns,
        variable,
        date_column,
        freq
    ):
    """
    Creates a complete weekly date range for each group,
    merges with the master data, marks missing rows,
    and fills missing values using linear interpolation.

    Parameters
    ----------
    master_data : pd.DataFrame
    group_columns : list
        One or multiple columns that define a group.
    date_column : str
        Name of the date column (must be datetime-like)
    missing_check_cols : list
        Columns used to detect missing values.
        If None → ALL numeric columns will be used.
    freq : str
        Frequency for calendar generation (default weekly Mondays).
    """

    # Ensure datetime
    master_data[date_column] = pd.to_datetime(master_data[date_column])

    full_group_data = []

    for group_key, group in master_data.groupby(group_columns):

        # ---- Step 1: Create full calendar for this group ----
        min_date = group[date_column].min()
        max_date = group[date_column].max()

        full_dates = pd.date_range(start=min_date, end=max_date, freq=freq)

        # Build calendar DF dynamically using group_columns
        calendar_dict = {col: group_key[i] if isinstance(group_key, tuple) else group_key
                         for i, col in enumerate(group_columns)}
        calendar_dict[date_column] = full_dates

        full_calendar = pd.DataFrame(calendar_dict)

        # ---- Step 2: Join with actual group data ----
        merged = full_calendar.merge(
            group,
            on=group_columns + [date_column],
            how="left"
        )

        # ---- Step 3: Mark missing rows based on selected columns ----
        merged["is_missing_record"] = merged[variable].isna()
        

        # ---- Step 4: Interpolate numeric columns ----
        numeric_cols = merged.select_dtypes(include=[np.number]).columns

        for col in numeric_cols:
            merged[col] = merged[col].interpolate(method="linear", limit_direction="both")

        full_group_data.append(merged)

    final_df = pd.concat(full_group_data, ignore_index=True)
    print(f"The number of records missing {final_df['is_missing_record'].sum()}")
    return final_df
