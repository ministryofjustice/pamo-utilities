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
        
    # Make sure range column exists
    if not 'value' in df_data_table.columns:        
        raise KeyError("ERROR - Value column missing.")
        return None

    # Work out which columns should be used to group the data
    # Assumes all passed except value column
    group_columns = df_data_table.columns.tolist()
    group_columns.remove('value')

     # Make sure group column exists
    if len(group_columns) == 0:        
        raise KeyError("ERROR - No group columns found in passed dataframe.")
        return None
        
    # Make sure range column only contains numeric values.  If not, warn user and return nothing.
    try:
        df_data_table['value'] = pd.to_numeric(df_data_table['value'], errors='raise')
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
        return None
    
    # Get mean for group
    df_results_table = df_data_table.groupby(group_columns).mean().reset_index()
    # Round results to 2 dp
    df_results_table.value = df_results_table.value.round(2)
    
    return df_results_table, df_data_table


def fn_get_median(df_data_table):
    """
    Function to calculate the median of the values for each group in the passed df_data_table
    
    Parameters:
    df_data_table: a summary table of two columns.  
        group: contains the group name/description
        value: contains the value for the respective group.
    
    Return:
    Results dataframe with columns group, group_median.  
    Data table dataframe returns the original data table with an additional column showing which records form the group median.
    Medians dataframe contains the median record/s.
    """   
    
    # Make sure group column exists
    if not 'group' in df_data_table.columns:        
        raise KeyError("ERROR - Group column missing")
        return None
        
    # Make sure range column exists
    if not 'value' in df_data_table.columns:        
        raise KeyError("ERROR - Value column missing.")
        return None
                    
    # Make sure range column only contains numeric values.  If not, warn user and return nothing.
    try:
        df_data_table['value'] = pd.to_numeric(df_data_table['value'], errors='raise')
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
        return None

    # Get median for group
    df_results_table = df_data_table.groupby(['group']).median().reset_index()

    # Make dataframe of rows that make the median
    df_results_table = df_results_table.rename(columns={'value':'median_value'})
    df_results_diff = df_data_table.merge(df_results_table, on='group', how='left')

    # Calculate the deviation from median for each record
    df_results_diff['deviation'] = abs(df_results_diff.value - df_results_diff.median_value)
    # Group by deviation and get minimum deviation for each group
    df_medians = df_results_diff.groupby(['group'])[['deviation']].min().reset_index()
    # Filter results to get just those on median by merging results
    df_medians = df_results_diff.merge(df_medians, on=['group', 'deviation'], how='inner')
    
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
    try:
        df_data_table['value'] = pd.to_numeric(df_data_table['value'], errors='raise')
        df_data_table['value'] = df_data_table['value'].astype(float)
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
        return None
    
    # Get comparator record
    df_comparator = df_data_table[df_data_table.group == comparator_group]
    # Confirm only one record
    if df_comparator.shape[0] == 1:        
        comparator_group_value = df_data_table[df_data_table.group == comparator_group]['value'].values[0]
        df_data_table['pay_gap'] = np.nan
        # Loop through each group in the df_data_table and calculate the gap
        for row in df_data_table.itertuples():
            # Get value for the gap group
            gap_group_value = df_data_table[df_data_table.group == row.group]['value'].values[0]
            # Calculate the pay gap
            pay_gap = round((comparator_group_value - gap_group_value) / comparator_group_value, 4)
            # Save the pay gap into the dataframe
            mask = (df_data_table.group == row.group)
            df_data_table.loc[mask, 'pay_gap'] = pay_gap
    else:
        raise ValueError("ERROR - More than one record in data table relating to the specified comparator group.")
    
    # Return the dataframe with added pay gap column
    return df_data_table


def fn_get_quantiles(df_data, range_column, bin_count):
    """
    Function to group data in the passed df_data_table into quantiles
    
    Parameters:
    df_data_table: table of data.
    range_column: The column containing the numerical range that forms the basis of quantile grouping
    bin_count: The number of quantiles the data should be grouped into
    
    Return:
    Results dataframe with quantile number, record_count in each quantile, range minimum and range maximum in each quantile.  
    """

    # Make sure range_column exists
    if not range_column in df_data.columns:        
        raise KeyError(range_column + " column missing")
        return None
        
    # Make sure range column only contains numeric values.  If not, warn user and return nothing.
    try:
        df_data[range_column] = pd.to_numeric(df_data[range_column], errors='raise')
    except:
        raise ValueError("ERROR - Value column contains non-numeric values.")
        return None
                                
    # Create a dataframe to hold the results
    df_results_table = pd.DataFrame(columns=['quantile', 'record_count', 'range_min', 'range_max'])
    
    # Sort table by range_column value ascending
    df_data = df_data[[range_column]].sort_values(by=[range_column])
    
    # Split into bins
    split_dfs = np.array_split(df_data, bin_count)

    # Access each part and build the output table
    dict_bins = {}
    for bin_id in range(0, bin_count):
        # Split dataframe into chunks
        dict_bins[bin_id] = split_dfs[bin_id]
        
        # Add chunk details to results table
        new_row = {'quantile': bin_id + 1, 'record_count': dict_bins[bin_id].shape[0], 'range_min': dict_bins[bin_id][range_column].min(), 'range_max': dict_bins[bin_id][range_column].max()}
        df_results_table.loc[len(df_results_table)] = new_row
    
    # Confirm quantile record count matches number of records we started with
    if df_results_table.record_count.sum() != df_data.shape[0]:
        raise ValueError("ERROR - Record count in quantiles doesn't match input data.")
        
    return df_results_table