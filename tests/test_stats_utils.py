'''
Unit tests for stats functions
To run tests 
'''

import pandas as pd
import pytest
import numpy as np

from stats_utils import fn_get_mean
def test_get_mean_valid_input_single_group():
    df = pd.DataFrame({
        'group': ['A', 'A', 'A'],
        'value': [10, 20, 30]
    })
    result, original = fn_get_mean(df)
    expected = pd.DataFrame({'group': ['A'], 'value': [20.0]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_get_mean_valid_input_multiple_groups():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B'],
        'value': [10, 20, 30, 40]
    })
    result, original = fn_get_mean(df)
    expected = pd.DataFrame({
        'group': ['A', 'B'],
        'value': [15.0, 35.0]
    })
    pd.testing.assert_frame_equal(result.sort_values('group').reset_index(drop=True),
                                  expected.sort_values('group').reset_index(drop=True))

def test_get_mean_non_numeric_values():
    df = pd.DataFrame({
        'group': ['A', 'B'],
        'value': ['10', 'abc']
    })

    with pytest.raises(ValueError, match="ERROR - Value column contains non-numeric values."):
        fn_get_mean(df)

def test_get_mean_empty_dataframe():
    df = pd.DataFrame(columns=['group', 'value'])    
    result, original = fn_get_mean(df)
    expected = pd.DataFrame(columns=['group', 'value'])
    expected.value = expected.value.astype(float)
    
    pd.testing.assert_frame_equal(result, expected)

def test_get_mean_missing_value_column():
    df = pd.DataFrame({'group': ['A', 'B']})
    with pytest.raises(KeyError):
        fn_get_mean(df)

def test_get_mean_missing_group_column():
    df = pd.DataFrame({'value': [10, 20]})
    with pytest.raises(KeyError):
        fn_get_mean(df)
        
def test_single_group_get_mean_output():
    # Create test DataFrame
    df_input = pd.DataFrame({
        'group': ['Male', 'Female', 'Male', 'Female', 'Male', 'Male', 'Female'],
        'value': [16, 16.6, 15.8, 16, 16.6, 15.8, 18]
    })
    
    # Expected result
    df_expected = pd.DataFrame({
        'group': ['Female', 'Male'],
        'value': [16.87, 16.05]
    }).reset_index(drop=True)

    # Run function
    df_result, df_data = fn_get_mean(df_input)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected)
    pd.testing.assert_frame_equal(df_data.reset_index(drop=True), df_input)


def test_multiple_group_get_mean_output():
    # Create test DataFrame
    df_input = pd.DataFrame({
        'cost_centre': ['10104000', '10104000', '10104000', '10104000', '10104000', 
                        '10104002', '10104002', '10104002', '10104002', '10104002'],
        'grade': ['PO', 'PO', 'PSO', 'PSO', 'PSO', 
                  'PO', 'PO', 'PSO', 'PSO', 'PSO'],
        'value': [32000, 32400, 26000, 26200, 26300, 
                  32400, 32500, 26000, 26100, 26100]
    })
    
    # Expected result
    df_expected = pd.DataFrame({'cost_centre': ['10104000', '10104000', '10104002', '10104002'],
     'grade': ['PO', 'PSO', 'PO', 'PSO'],
     'value': [32200.0, 26166.67, 32450.0, 26066.67]}).reset_index(drop=True)

    # Run function
    df_result, df_data = fn_get_mean(df_input)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected)
    pd.testing.assert_frame_equal(df_data.reset_index(drop=True), df_input)
    
    
from stats_utils import fn_get_median
def test_median_valid_input_odd_group_size():
    df = pd.DataFrame({
        'group': ['A', 'A', 'A'],
        'value': [10, 20, 30]
    })
    result, updated_df, medians_df = fn_get_median(df)
    expected_result = pd.DataFrame({'group': ['A'], 'median_value': [20.0]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)

    # Check that the correct record is marked with the median
    assert updated_df.loc[updated_df['value'] == 20.0].shape[0] == 1

def test_median_valid_input_even_group_size():
    df = pd.DataFrame({
        'group': ['A', 'A', 'A', 'A'],
        'value': [10, 20, 30, 40]
    })
    result, updated_df, medians_df = fn_get_median(df)
    expected_result = pd.DataFrame({'group': ['A'], 'median_value': [25.0]})
    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected_result)

    # Check that two records are marked with the median
    assert medians_df.shape[0] == 2

def test_median_multiple_groups():
    df = pd.DataFrame({
        'group': ['A', 'A', 'B', 'B', 'B'],
        'value': [10, 30, 5, 15, 25]
    })
    result, updated_df, medians_df = fn_get_median(df)
    expected_result = pd.DataFrame({
        'group': ['A', 'B'],
        'median_value': [20.0, 15.0]
    })
    pd.testing.assert_frame_equal(result.sort_values('group').reset_index(drop=True),
                                  expected_result.sort_values('group').reset_index(drop=True))

def test_median_non_numeric_values():
    df = pd.DataFrame({
        'group': ['A', 'B'],
        'value': ['10', 'abc']
    })

    with pytest.raises(ValueError, match="ERROR - Value column contains non-numeric values."):
        fn_get_median(df)

def test_median_missing_group_column():
    df = pd.DataFrame({'median_value': [10, 20]})
    with pytest.raises(KeyError, match="ERROR - Group column missing"):
        fn_get_median(df)

def test_median_missing_value_column():
    df = pd.DataFrame({'group': ['A', 'B']})
    with pytest.raises(KeyError, match="ERROR - Value column missing."):
        fn_get_median(df)

def test_median_empty_dataframe():
    df = pd.DataFrame(columns=['group', 'value'])

    with pytest.raises(ValueError, match="ERROR - Passed dataframe contains no data."):
        fn_get_median(df)
       
def test_get_median_output():
    # Create test DataFrame
    df_input = pd.DataFrame({
        'group': ['Male', 'Female', 'Male', 'Female', 'Male', 'Male', 'Female'],
        'value': [16, 16.6, 15.8, 16, 16.6, 15.8, 18]
    })
    
    df_input_returned = pd.DataFrame({
        'group': ['Male', 'Female', 'Male', 'Female', 'Male', 'Male', 'Female'],
        'value': [16, 16.6, 15.8, 16, 16.6, 15.8, 18]
    })

    # Expected result
    df_expected = pd.DataFrame({
        'group': ['Female', 'Male'],
        'median_value': [16.6, 15.9]
    }).reset_index(drop=True)

    # Run function
    df_result, df_data, medians_df = fn_get_median(df_input)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected)
    pd.testing.assert_frame_equal(df_data.reset_index(drop=True), df_input_returned)


from stats_utils import fn_get_pay_gap
def test_gap_valid_input_single_comparator():
    df_input = pd.DataFrame({
        'group': ['Male', 'Female'],
        'value': [16, 16.6]
    })

    df_expected = pd.DataFrame({
        'group': ['Male', 'Female'],
        'value': [16.0, 16.6],
        'pay_gap': [0.0, -0.0375]
    })

    df_result = fn_get_pay_gap(df_input.copy(), "Male")
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected.reset_index(drop=True))

def test_gap_multiple_groups():
    df_input = pd.DataFrame({
        'group': ['Male', 'Female', 'Other'],
        'value': [20, 18, 15]
    })

    df_expected = pd.DataFrame({
        'group': ['Male', 'Female', 'Other'],
        'value': [20.0, 18.0, 15.0],
        'pay_gap': [0.0, 0.1, 0.25]
    })

    df_result = fn_get_pay_gap(df_input.copy(), "Male")
    pd.testing.assert_frame_equal(df_result.sort_values('group').reset_index(drop=True),
                                  df_expected.sort_values('group').reset_index(drop=True))

def test_gap_missing_group_column():
    df_input = pd.DataFrame({'value': [10, 20]})
    with pytest.raises(KeyError, match="Group column missing"):
        fn_get_pay_gap(df_input, "Male")

def test_gap_missing_value_column():
    df_input = pd.DataFrame({'group': ['Male', 'Female']})
    with pytest.raises(KeyError, match="Value column missing"):
        fn_get_pay_gap(df_input, "Male")

def test_gap_non_numeric_values():
    df_input = pd.DataFrame({
        'group': ['Male', 'Female'],
        'value': ['20', 'abc']
    })

    with pytest.raises(ValueError, match="ERROR - Value column contains non-numeric values."):
        fn_get_pay_gap(df_input, "Male")

def test_multiple_comparator_records():
    df_input = pd.DataFrame({
        'group': ['Male', 'Male', 'Female'],
        'value': [20, 20, 18]
    })

    with pytest.raises(ValueError, match="ERROR - More than one record in data table relating to the specified comparator group."):
        fn_get_pay_gap(df_input.copy(), "Male")
    
    
from stats_utils import fn_get_quantiles
def test_get_quantiles_valid_input_even_bins():
    df_input = pd.DataFrame({'value': [10, 20, 30, 40]})
    result = fn_get_quantiles(df_input.copy(), 'value', 2)

    expected = pd.DataFrame({
        'quantile': [1, 2],
        'record_count': [2, 2],
        'range_min': [10, 30],
        'range_max': [20, 40]
    })

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_quantiles_valid_input_uneven_bins():
    df_input = pd.DataFrame({'value': [10, 20, 30, 40, 50]})
    result = fn_get_quantiles(df_input.copy(), 'value', 3)

    assert result['record_count'].sum() == 5
    assert result.shape[0] == 3
    assert result['range_min'].iloc[0] == 10
    assert result['range_max'].iloc[-1] == 50

def test_quantiles_missing_column():
    df_input = pd.DataFrame({'other': [1, 2, 3]})
    with pytest.raises(KeyError, match="value column missing"):
        fn_get_quantiles(df_input, 'value', 2)

def test_quantiles_non_numeric_values():
    df_input = pd.DataFrame({'value': ['10', 'abc', '30']})

    with pytest.raises(ValueError, match="ERROR - Value column contains non-numeric values."):
        fn_get_quantiles(df_input, 'value', 2)

def test_quantiles_fewer_records_than_bins():
    df_input = pd.DataFrame({'value': [100]})
    result = fn_get_quantiles(df_input.copy(), 'value', 3)

    assert result['record_count'].sum() == 1
    assert result.shape[0] == 3
    assert result['record_count'].iloc[0] == 1
    assert result['record_count'].iloc[1] == 0
    assert result['record_count'].iloc[2] == 0

def test_fn_get_quantiles_output():
    # Create test DataFrame
    df_input = pd.DataFrame({
        'GRSSAL': [23250.0,  41712.1,  27840.0,  41711.84,  31995.0,  26474.59,  26474.59,  26474.59,  26474.59,  26474.59,  26474.59,  26474.25,  26474.96,  31664.4,  30724.56,  36629.16,  
                   27039.96,  50303.04,  35948.04,  26474.25,  31995.0,  23250.0, 31995.0, 26474.25, 26475.06],
    })

    # Expected result
    df_expected_deciles = pd.DataFrame({
        'quantile': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'record_count': [3, 3, 3, 3, 3, 2, 2, 2, 2, 2],
        'range_min': [23250.0, 26474.25, 26474.59, 26474.59, 26475.06, 30724.56, 31995.0, 31995.0, 36629.16, 41712.1],
        'range_max': [26474.25, 26474.59, 26474.59, 26474.96, 27840.0, 31664.4, 31995.0, 35948.04, 41711.84, 50303.04]
    }).reset_index(drop=True)
    
        # Expected result
    df_expected_quartiles = pd.DataFrame({
        'quantile': [1, 2, 3, 4],
        'record_count': [7, 6, 6, 6],
        'range_min': [23250.0, 26474.59, 27039.96, 31995.00],
        'range_max': [26474.59, 26475.06, 31995.0, 50303.04]
    }).reset_index(drop=True)

    # Run function for deciles
    df_result = fn_get_quantiles(df_input, 'GRSSAL', 10)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected_deciles)
    
    # Run function for quartiles
    df_result = fn_get_quantiles(df_input, 'GRSSAL', 4)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected_quartiles)


from stats_utils import fn_get_pay_gap_quantiles
def test_get_pay_gap_quantiles_valid_input_even_bins():
    df_input = pd.DataFrame({'value': [10, 20, 30, 40]})
    result = fn_get_pay_gap_quantiles(df_input.copy(), 'value', 2)
    
    expected = pd.DataFrame({
        'quantile': [1, 2],
        'record_count': [2.0, 2.0],
        'range_min': [10, 30],
        'range_max': [20, 40]
    })

    pd.testing.assert_frame_equal(result.reset_index(drop=True), expected)

def test_pay_gap_quantiles_valid_input_uneven_bins():
    df_input = pd.DataFrame({'value': [10, 20, 30, 40, 50]})
    result = fn_get_pay_gap_quantiles(df_input.copy(), 'value', 3)

    assert result['record_count'].sum() == 5.01
    assert result.shape[0] == 3
    assert result['range_min'].iloc[0] == 10
    assert result['range_max'].iloc[-1] == 50

def test_pay_gap_quantiles_missing_column():
    df_input = pd.DataFrame({'other': [1, 2, 3]})
    with pytest.raises(KeyError, match="value column missing"):
        fn_get_pay_gap_quantiles(df_input, 'value', 2)

def test_pay_gap_quantiles_non_numeric_values():
    df_input = pd.DataFrame({'value': ['10', 'abc', '30']})

    with pytest.raises(ValueError, match="ERROR - value column contains non-numeric values."):
        fn_get_pay_gap_quantiles(df_input, 'value', 2)

def test_pay_gap_quantiles_fewer_records_than_bins():
    df_input = pd.DataFrame({'value': [100]})
    result = fn_get_pay_gap_quantiles(df_input.copy(), 'value', 3)

    assert result['record_count'].sum() == 0.99
    assert result.shape[0] == 3
    assert result['record_count'].iloc[0] == 0.33
    assert result['record_count'].iloc[1] == 0.33
    assert result['record_count'].iloc[2] == 0.33

def test_fn_get_pay_gap_quantiles_output():
    # Create test DataFrame
    df_input = pd.DataFrame({
        'GRSSAL': [23250.0,  41712.1,  27840.0,  41711.84,  31995.0,  26474.59,  26474.59,  26474.59,  26474.59,  26474.59,  26474.59,  26474.25,  26474.96,  31664.4,  30724.56,  36629.16,  
                   27039.96,  50303.04,  35948.04,  26474.25,  31995.0,  23250.0, 31995.0, 26474.25, 26475.06],
    })

    # Expected result
    df_expected_deciles = pd.DataFrame({
        'quantile': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'record_count': [2.50] * 10,
        'range_min': [23250.00, 26474.25, 26474.59, 26474.59, 26474.59, 26475.06, 30724.56, 31995.00, 35948.04, 41711.84],
        'range_max': [26474.25, 26474.25, 26474.59, 26474.59, 26475.06, 27840.00, 31995.00, 31995.00, 41711.84, 50303.04]
    }).reset_index(drop=True)
    
        # Expected result
    df_expected_quartiles = pd.DataFrame({
        'quantile': [1, 2, 3, 4],
        'record_count': [6.25] * 4,
        'range_min': [23250.00, 26474.59, 26475.06, 31995.00],
        'range_max': [26474.59, 26475.06, 31995.00, 50303.04]
    }).reset_index(drop=True)

    # Run function for deciles
    df_result = fn_get_pay_gap_quantiles(df_input, 'GRSSAL', 10)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected_deciles)
    
    # Run function for quartiles
    df_result = fn_get_pay_gap_quantiles(df_input, 'GRSSAL', 4)

    # Assert equality
    pd.testing.assert_frame_equal(df_result.reset_index(drop=True), df_expected_quartiles)