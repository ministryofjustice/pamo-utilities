# Handy utility functions

---
## Pvenv
An automated way to create and use a virtual environment.  Uses the Poetry packaging tools.
### How to use
Copy the file *pvenv_setup.py* into your project working folder and then run it from the command line, following the prompts.
Commonly used packages are already included but further packages can be added by editing the script.
```python
python pvenv_setup.py
```
---
## Stats
Some useful stats functions.
### How to use
The pamo-utilities should be installed automtaically by pvenv_setup but if this doesn't happen or if you don't want to use pvenv_setup you can install using the following Python code.
```python
!pip install git+https://github.com/ministryofjustice/pamo-utilities.git
```
Once installed you can import the utilites as per the example below.
```python
from stats_utils import stats_utils
```
Then use the functions as per the example below.
```python
df_out = stats_utils.fn_get_mean(df_in)
```

### fn_get_mean(df_data_table):

    Function to calculate the mean of the values for each group in the passed df_data_table
    
    Parameters:
    df_data_table: a summary table containing a value column plus one or more grouping columns.
        value: contains the value for the respective group.
        other columns: contains the group name/description.  These are used to group the data and calculate means.      
    
    Return:
    Results dataframe with group columns, group_mean.  
    Data table dataframe returns the original data table with no changes made.

### fn_get_median(df_data_table):

    Function to calculate the median of the values for each group in the passed df_data_table
    
    Parameters:
    df_data_table: a summary table of two columns.  
        group: contains the group name/description
        value: contains the value for the respective group.
    
    Return:
    Results dataframe with columns group, group_median.  
    Data table dataframe returns the original data table with an additional column showing which records form the group median.
    Medians dataframe contains the median record/s.

### fn_get_pay_gap(df_data_table, comparator_group):

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

### fn_get_quantiles(df_data, range_column, bin_count):

    Function to group data in the passed df_data_table into quantiles
    
    Parameters:
    df_data_table: table of data.
    range_column: The column containing the numerical range that forms the basis of quantile grouping
    bin_count: The number of quantiles the data should be grouped into
    
    Return:
    Results dataframe with quantile number, record_count in each quantile, range minimum and range maximum in each quantile.  
---
