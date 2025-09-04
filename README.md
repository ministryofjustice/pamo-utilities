#Handy utility functions

##fn_get_mean(df_data_table):

    Function to calculate the mean of the values for each group in the passed df_data_table
    
    Parameters:
    df_data_table: a summary table containing a value column plus one or more grouping columns.
        value: contains the value for the respective group.
        other columns: contains the group name/description.  These are used to group the data and calculate means.      
    
    Return:
    Results dataframe with group columns, group_mean.  
    Data table dataframe returns the original data table with no changes made.

