import pandas as pd
import numpy as np


def fn_get_mean(df_data_table):
    """
    Function to calculate the mean of the values for each group in the passed df_data_table
    
    Parameters:
    df_data_table: a summary table containing a value column plus one or more grouping columns.
        value: contains the value for the respective group.
        other columns: contains the group name/description.  These are used to group the data and calculate means.      
    
    Return:
    Results dataframe with group columns, group_mean.  
    Data table dataframe returns the original data table with no changes made.
    """

    # Make sure value column exists
    if 'value' not in df_data_table.columns:
        raise KeyError("ERROR - Value column missing.")

    # Work out grouping columns
    group_columns = df_data_table.columns.tolist()
    group_columns.remove('value')

    # Make sure group columns exist
    if len(group_columns) == 0:
        raise KeyError("ERROR - No group columns found in passed dataframe.")

    # Ensure value is numeric
    try:
        df_data_table['value'] = pd.to_numeric(df_data_table['value'], errors='raise')
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")

    # Calculate mean and round to 2 decimal places
    df_results_table = (
        df_data_table
        .groupby(group_columns)['value']
        .mean()
        .round(2)
        .reset_index()
    )

    return df_results_table, df_data_table
    

def fn_get_median(df_data_table):
    """
    Function to calculate the median of the values for each group in the passed df_data_table

    Parameters:
    df_data_table: a summary table of two columns.
        group: contains the group name/description
        value: contains the value for the respective group.

    Return:
    Results dataframe with columns group, median_value.
    Data table dataframe returns the original data table.
    Medians dataframe contains the actual median record(s):
        - one record for odd-sized groups
        - two records for even-sized groups
    """

    # Make sure group column exists
    if 'group' not in df_data_table.columns:
        raise KeyError("ERROR - Group column missing")

    # Make sure value column exists
    if 'value' not in df_data_table.columns:
        raise KeyError("ERROR - Value column missing.")

    # Make sure passed dataframe contains some data
    if len(df_data_table) == 0:
        raise ValueError("ERROR - Passed dataframe contains no data.")

    # Make sure value column only contains numeric values
    try:
        df_data_table['value'] = pd.to_numeric(
            df_data_table['value'],
            errors='raise'
        )
    except Exception:
        raise ValueError("ERROR - Value column contains non-numeric values.")

    # Calculate median value for each group
    df_results_table = (
        df_data_table
        .groupby('group', as_index=False)['value']
        .median()
        .rename(columns={'value': 'median_value'})
    )

    # Identify the actual median record(s)
    median_rows = []

    for group, grp in df_data_table.groupby('group'):

        grp = grp.sort_values('value').copy()
        n = len(grp)

        if n % 2 == 1:
            # Odd number of records - single median row
            median_rows.append(grp.iloc[[n // 2]])

        else:
            # Even number of records - two rows define median
            median_rows.append(grp.iloc[[n // 2 - 1, n // 2]])

    df_medians = pd.concat(median_rows, ignore_index=True)

    return df_results_table, df_data_table, df_medians

    
# Pay gap function
def fn_get_pay_gap(df_data_table, comparator_group):
    """
    Function to calculate the pay gap between a comparator group and all other groups in the passed df_data_table
    In gender pay gap reporting the comparator group is male.
    In ethnicity pay gap reporting the comparator group is white.
    In disability pay gap reporting the comparator group is non-disabled.
    
    Parameters:
    df_data_table: a summary table of two columns.  
        group: contains the group name/description
        value: contains the mean or median hourly pay rate for the respective group.
    
    Return:
    Dataframe with columns group, hourly_rate, pay_gap.  
    If mean hourly rates are used as input the pay gap will be the mean pay gap.
    If median hourly rates are used as input the pay gap will be the median pay gap.
    """

    # Make sure group column exists
    if not 'group' in df_data_table.columns:        
        raise KeyError("Group column missing")
        return None
        
    # Make sure range column exists
    if not 'value' in df_data_table.columns:        
        raise KeyError("Value column missing")
        return None
        
    # Make sure range column only contains numeric values.  If not, warn user and return nothing.
    df_data = df_data_table.copy()
    try:
        df_data['value'] = pd.to_numeric(df_data['value'], errors='raise')
        df_data['value'] = df_data['value'].astype(float)
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
        return None
    
    # Get comparator record
    df_comparator = df_data[df_data.group == comparator_group]
    # Confirm only one record
    if df_comparator.shape[0] == 1:        
        comparator_group_value = df_data[df_data.group == comparator_group]['value'].values[0]
        df_data['pay_gap'] = np.nan
        # Loop through each group in the df_data_table and calculate the gap
        for row in df_data_table.itertuples():
            # Get value for the gap group
            gap_group_value = df_data[df_data.group == row.group]['value'].values[0]
            # Calculate the pay gap
            pay_gap = round((comparator_group_value - gap_group_value) / comparator_group_value, 4)
            # Save the pay gap into the dataframe
            mask = (df_data.group == row.group)
            df_data.loc[mask, 'pay_gap'] = pay_gap
    else:
        raise ValueError("ERROR - More than one record in data table relating to the specified comparator group.")
    
    # Return the dataframe with added pay gap column
    return df_data


def fn_get_quantiles(df_data, range_column, bin_count=4):
    """
    Function to group data in the passed df_data_table into quantiles
    
    Parameters:
    df_data_table: table of data.
    range_column: The column containing the numerical range that forms the basis of quantile grouping
    bin_count: The number of quantiles the data should be grouped into
    
    Return:
    Results dataframe with quantile number, record_count in each quantile, range minimum and range maximum in each quantile.  
    """

    # Confirm input is a DataFrame
    if not isinstance(df_data, pd.DataFrame):
        raise TypeError(
            f"df_data must be a pandas DataFrame, got {type(df_data).__name__}"
        )

    # Make sure range_column exists
    if not range_column in df_data.columns:        
        raise KeyError(range_column + " column missing")
        
    # Make sure range column only contains numeric values.  If not, warn user and return nothing.
    try:
        df_data[range_column] = pd.to_numeric(df_data[range_column], errors='raise')
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
                                
    # Create a dataframe to hold the results
    df_results_table = pd.DataFrame(columns=['quantile', 'record_count', 'range_min', 'range_max'])
    
    # Sort table by range_column value ascending
    df_data = df_data[[range_column]].sort_values(by=[range_column])
            
    # Split into bins
    split_indices = np.array_split(df_data.index, bin_count)
    split_dfs = [df_data.loc[idx] for idx in split_indices]

    # Access each part and build the output table
    for bin_id in range(0, bin_count):
        # Split dataframe into chunks
        df = split_dfs[bin_id]
        # Add chunk details to results table
        new_row = {'quantile': bin_id + 1, 'record_count': df.shape[0], 'range_min': df[range_column].min(), 'range_max': df[range_column].max()}
        df_results_table.loc[len(df_results_table)] = new_row
    
    # Confirm quantile record count matches number of records we started with
    if df_results_table.record_count.sum() != df_data.shape[0]:
        raise ValueError("ERROR - Record count in quantiles doesn't match input data.")
        
    return df_results_table


def fn_get_pay_gap_quantiles(df_data, range_column, bin_count=4):
    """
    Cabinet Office compliant quantile calculation.

    Function to group data in the passed df_data_table into quantiles
    Handles tied values fairly at quantile boundaries rather than
    arbitrarily splitting tied records.

    Parameters
    ----------
    df_data : pandas.DataFrame
        Input data.

    range_column : str
        Numeric column used to determine quantiles.

    bin_count : int
        Number of quantiles required.

    Returns
    -------
    pandas.DataFrame

    quantile
    record_count
    range_min
    range_max
    """

    import pandas as pd
    import numpy as np

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    if range_column not in df_data.columns:
        raise KeyError(f"{range_column} column missing.")

    try:
        df_data = df_data.copy()
        df_data[range_column] = pd.to_numeric(
            df_data[range_column],
            errors="raise"
        )
    except Exception:
        raise ValueError(
            f"ERROR - {range_column} column contains non-numeric values."
        )

    df_data = (
        df_data[[range_column]]
        .dropna()
        .sort_values(range_column)
        .reset_index(drop=True)
    )

    if len(df_data) == 0:
        raise ValueError("No records available")

    # ------------------------------------------------------------------
    # Cabinet Office allocation
    # ------------------------------------------------------------------

    n = len(df_data)

    quantile_capacity = np.repeat(
        n / bin_count,
        bin_count
    ).astype(float)

    results = []

    current_quantile = 0

    # Process equal-pay groups together
    for pay_value, pay_group in df_data.groupby(range_column):

        group_size = len(pay_group)

        remaining_group = float(group_size)

        while (
            remaining_group > 1e-10
            and current_quantile < bin_count
        ):

            capacity = quantile_capacity[current_quantile]

            allocation = min(
                remaining_group,
                capacity
            )

            results.append({
                "quantile": current_quantile + 1,
                "pay_value": pay_value,
                "allocated_count": allocation
            })

            quantile_capacity[current_quantile] -= allocation
            remaining_group -= allocation

            if quantile_capacity[current_quantile] <= 1e-10:
                current_quantile += 1

    allocation_df = pd.DataFrame(results)

    # ------------------------------------------------------------------
    # Build summary table
    # ------------------------------------------------------------------

    summary_rows = []

    for quantile in range(1, bin_count + 1):

        tmp = allocation_df[
            allocation_df["quantile"] == quantile
        ]

        summary_rows.append({
            "quantile": quantile,
            "record_count": tmp["allocated_count"].sum(),
            "range_min": tmp["pay_value"].min(),
            "range_max": tmp["pay_value"].max()
        })

    df_results_table = pd.DataFrame(summary_rows)

    # QA check
    if not np.isclose(
        df_results_table["record_count"].sum(),
        n
    ):
        raise ValueError(
            "Quantile record counts do not reconcile to input data"
        )

    return df_results_table.round(2)
