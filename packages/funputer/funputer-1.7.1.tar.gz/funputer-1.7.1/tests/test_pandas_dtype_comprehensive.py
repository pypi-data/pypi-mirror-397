"""
Comprehensive tests for pandas_dtype field functionality and edge case handling.

Tests the robust pandas dtype detection and normalization across all supported
pandas data types, including edge cases, extension types, and future-proofing.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime
import tempfile
import os

from funputer.metadata_inference import _get_normalized_pandas_dtype, infer_metadata_from_dataframe
from funputer.models import ColumnMetadata


class TestPandasDtypeNormalization:
    """Test the _get_normalized_pandas_dtype function with all edge cases."""
    
    def test_standard_numeric_types(self):
        """Test standard numeric pandas dtypes."""
        # Integer types
        int_series = pd.Series([1, 2, 3], dtype='int64')
        assert _get_normalized_pandas_dtype(int_series) == 'int64'
        
        int32_series = pd.Series([1, 2, 3], dtype='int32')
        assert _get_normalized_pandas_dtype(int32_series) == 'int32'
        
        # Float types
        float_series = pd.Series([1.1, 2.2, 3.3], dtype='float64')
        assert _get_normalized_pandas_dtype(float_series) == 'float64'
        
        float32_series = pd.Series([1.1, 2.2, 3.3], dtype='float32')
        assert _get_normalized_pandas_dtype(float32_series) == 'float32'
    
    def test_nullable_integer_types(self):
        """Test pandas nullable integer types (Int64, Int32, etc.)."""
        # Nullable integers
        nullable_int_series = pd.Series([1, 2, None], dtype='Int64')
        assert _get_normalized_pandas_dtype(nullable_int_series) == 'nullable_int64'
        
        nullable_int32_series = pd.Series([1, 2, None], dtype='Int32')
        assert _get_normalized_pandas_dtype(nullable_int32_series) == 'nullable_int32'
        
        nullable_int16_series = pd.Series([1, 2, None], dtype='Int16')
        assert _get_normalized_pandas_dtype(nullable_int16_series) == 'nullable_int16'
        
        nullable_int8_series = pd.Series([1, 2, None], dtype='Int8')
        assert _get_normalized_pandas_dtype(nullable_int8_series) == 'nullable_int8'
    
    def test_nullable_boolean_type(self):
        """Test pandas nullable boolean type."""
        nullable_bool_series = pd.Series([True, False, None], dtype='boolean')
        assert _get_normalized_pandas_dtype(nullable_bool_series) == 'nullable_boolean'
    
    def test_string_dtype(self):
        """Test pandas string dtype (pandas >= 1.0)."""
        string_series = pd.Series(['a', 'b', 'c'], dtype='string')
        assert _get_normalized_pandas_dtype(string_series) == 'string_dtype'
    
    def test_categorical_dtype(self):
        """Test pandas categorical dtype with various underlying types."""
        # Categorical with object categories
        cat_series = pd.Categorical(['a', 'b', 'c', 'a'])
        cat_df_series = pd.Series(cat_series)
        result = _get_normalized_pandas_dtype(cat_df_series)
        assert result.startswith('category[')
        assert 'object' in result
        
        # Categorical with integer categories
        int_cat_series = pd.Categorical([1, 2, 3, 1])
        int_cat_df_series = pd.Series(int_cat_series)
        result = _get_normalized_pandas_dtype(int_cat_df_series)
        assert result.startswith('category[')
    
    def test_datetime_types(self):
        """Test datetime types including timezone-aware."""
        # Basic datetime
        dt_series = pd.Series([datetime.now(), datetime.now()])
        result = _get_normalized_pandas_dtype(dt_series)
        assert 'datetime64' in result
        
        # Timezone-aware datetime
        tz_dt_series = pd.to_datetime(['2021-01-01', '2021-01-02']).tz_localize('UTC')
        tz_series = pd.Series(tz_dt_series)
        result = _get_normalized_pandas_dtype(tz_series)
        assert 'datetime64[ns, UTC]' in result
    
    def test_timedelta_types(self):
        """Test timedelta types."""
        td_series = pd.Series([pd.Timedelta('1 day'), pd.Timedelta('2 days')])
        result = _get_normalized_pandas_dtype(td_series)
        assert 'timedelta' in result
    
    def test_complex_types(self):
        """Test complex number types."""
        complex_series = pd.Series([1+2j, 3+4j], dtype='complex128')
        result = _get_normalized_pandas_dtype(complex_series)
        assert 'complex' in result
    
    def test_object_dtype(self):
        """Test object dtype (mixed types)."""
        obj_series = pd.Series(['a', 1, True], dtype='object')
        assert _get_normalized_pandas_dtype(obj_series) == 'object'
    
    def test_period_dtype(self):
        """Test period dtype."""
        period_series = pd.Series(pd.period_range('2021-01', periods=3, freq='M'))
        result = _get_normalized_pandas_dtype(period_series)
        assert 'period' in result and 'M' in result
    
    def test_interval_dtype(self):
        """Test interval dtype."""
        interval_series = pd.Series(pd.interval_range(start=0, end=3))
        result = _get_normalized_pandas_dtype(interval_series)
        # Interval dtype should be detected correctly - check for actual pandas interval dtype string
        assert 'interval' in result or 'Interval' in result
    
    def test_empty_series(self):
        """Test empty series handling."""
        empty_series = pd.Series([], dtype='object')
        result = _get_normalized_pandas_dtype(empty_series)
        assert result == 'object'
    
    def test_error_handling(self):
        """Test error handling for malformed data."""
        # This should not raise an error but fall back gracefully
        class BadSeries:
            @property
            def dtype(self):
                raise Exception("Simulated error")
        
        bad_series = BadSeries()
        result = _get_normalized_pandas_dtype(bad_series)
        assert result == "unknown_dtype"
    
    def test_future_proofing_unknown_dtype(self):
        """Test handling of unknown future dtypes."""
        # Test with a mock dtype that has unknown characteristics
        class MockDtype:
            def __str__(self):
                return "future_dtype_v2.0"
            
            def __repr__(self):
                return "future_dtype_v2.0"
        
        class MockSeries:
            def __init__(self):
                self.dtype = MockDtype()
        
        mock_series = MockSeries()
        
        # Should not crash and return the string representation
        result = _get_normalized_pandas_dtype(mock_series)
        # Should handle gracefully and return the string representation
        assert isinstance(result, str)
        assert "future_dtype_v2.0" in result


class TestMetadataInferenceWithPandasDtype:
    """Test metadata inference includes pandas_dtype field correctly."""
    
    def test_inference_includes_pandas_dtype(self):
        """Test that metadata inference includes pandas_dtype field."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'bool_col': [True, False, True]
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        # Check that all metadata objects have pandas_dtype field
        for metadata in metadata_list:
            assert hasattr(metadata, 'pandas_dtype')
            assert metadata.pandas_dtype is not None
            assert isinstance(metadata.pandas_dtype, str)
        
        # Check specific dtypes
        int_meta = next(m for m in metadata_list if m.column_name == 'int_col')
        assert int_meta.pandas_dtype == 'int64'
        assert int_meta.data_type == 'integer'  # Semantic type
        
        float_meta = next(m for m in metadata_list if m.column_name == 'float_col')
        assert float_meta.pandas_dtype == 'float64'
        assert float_meta.data_type == 'float'
        
        str_meta = next(m for m in metadata_list if m.column_name == 'str_col')
        assert str_meta.pandas_dtype == 'object'
        assert str_meta.data_type == 'categorical'  # Semantic classification
        
        bool_meta = next(m for m in metadata_list if m.column_name == 'bool_col')
        assert bool_meta.pandas_dtype == 'bool'
        assert bool_meta.data_type == 'boolean'
    
    def test_inference_with_categorical_data(self):
        """Test pandas_dtype vs data_type distinction with categorical data."""
        # String data that should be classified as categorical
        df = pd.DataFrame({
            'category_col': ['cat', 'dog', 'cat', 'bird', 'dog'] * 20,  # Low unique ratio
            'id_col': list(range(100)),  # High unique ratio
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        cat_meta = next(m for m in metadata_list if m.column_name == 'category_col')
        assert cat_meta.pandas_dtype == 'object'  # Storage type
        assert cat_meta.data_type == 'categorical'  # Semantic type
        
        id_meta = next(m for m in metadata_list if m.column_name == 'id_col')
        assert id_meta.pandas_dtype == 'int64'  # Storage type
        assert id_meta.data_type == 'integer'  # Semantic type
    
    def test_inference_with_pandas_categorical(self):
        """Test inference with actual pandas Categorical dtype."""
        df = pd.DataFrame({
            'pandas_cat': pd.Categorical(['A', 'B', 'C', 'A', 'B'])
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        cat_meta = metadata_list[0]
        
        # Check storage type is categorical
        assert cat_meta.pandas_dtype.startswith('category[')
        # Note: The semantic classification depends on the inference logic
        # which may classify pandas categorical as 'string' or 'categorical'
        assert cat_meta.data_type in ['categorical', 'string']
    
    def test_inference_fallback_with_pandas_dtype(self):
        """Test that fallback metadata includes pandas_dtype."""
        df = pd.DataFrame({
            'good_col': [1, 2, 3],
            'problem_col': [1, 2, 3]  # We'll simulate a problem
        })
        
        # Mock the inference to fail for one column
        original_infer = pd.DataFrame.__getitem__
        def mock_getitem(self, key):
            if key == 'problem_col':
                raise Exception("Simulated inference error")
            return original_infer(self, key)
        
        pd.DataFrame.__getitem__ = mock_getitem
        
        try:
            metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
            
            # Should still have metadata for both columns
            assert len(metadata_list) == 2
            
            # Problem column should have fallback with pandas_dtype
            problem_meta = next(m for m in metadata_list if m.column_name == 'problem_col')
            assert hasattr(problem_meta, 'pandas_dtype')
            assert problem_meta.pandas_dtype in ['object', 'int64']  # Fallback value
        finally:
            # Restore original method
            pd.DataFrame.__getitem__ = original_infer
    
    def test_nullable_types_inference(self):
        """Test inference with nullable pandas types."""
        df = pd.DataFrame({
            'nullable_int': pd.Series([1, 2, None], dtype='Int64'),
            'nullable_bool': pd.Series([True, False, None], dtype='boolean'),
            'nullable_str': pd.Series(['a', 'b', None], dtype='string')
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        int_meta = next(m for m in metadata_list if m.column_name == 'nullable_int')
        assert int_meta.pandas_dtype == 'nullable_int64'
        assert int_meta.data_type == 'integer'
        
        bool_meta = next(m for m in metadata_list if m.column_name == 'nullable_bool')
        assert bool_meta.pandas_dtype == 'nullable_boolean'
        assert bool_meta.data_type == 'boolean'
        
        str_meta = next(m for m in metadata_list if m.column_name == 'nullable_str')
        assert str_meta.pandas_dtype == 'string_dtype'


class TestPandasDtypeCSVOutput:
    """Test that pandas_dtype field is properly included in CSV output."""
    
    def test_csv_output_includes_pandas_dtype(self):
        """Test CSV output includes pandas_dtype column."""
        df = pd.DataFrame({
            'test_col': [1, 2, 3]
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        # Convert to DataFrame (simulating CSV output)
        metadata_dict = []
        for m in metadata_list:
            metadata_dict.append({
                'column_name': m.column_name,
                'pandas_dtype': m.pandas_dtype,
                'data_type': m.data_type,
                'description': m.description
            })
        
        metadata_df = pd.DataFrame(metadata_dict)
        
        # Check that pandas_dtype column exists
        assert 'pandas_dtype' in metadata_df.columns
        assert metadata_df['pandas_dtype'].iloc[0] == 'int64'
        assert metadata_df['data_type'].iloc[0] == 'integer'
    
    def test_backward_compatibility(self):
        """Test that existing CSV files without pandas_dtype can still be loaded."""
        # Create a CSV without pandas_dtype field
        metadata_content = """column_name,data_type,description
test_col,integer,Test column"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(metadata_content)
            f.flush()
            
            try:
                from funputer.io import load_metadata
                metadata_list = load_metadata(f.name)
                
                # Should load successfully with default pandas_dtype
                assert len(metadata_list) == 1
                assert metadata_list[0].column_name == 'test_col'
                assert metadata_list[0].data_type == 'integer'
                assert metadata_list[0].pandas_dtype == 'object'  # Default fallback
            finally:
                os.unlink(f.name)


class TestEdgeCasesAndRobustness:
    """Test edge cases and robustness of pandas dtype handling."""
    
    def test_mixed_dtypes_dataframe(self):
        """Test DataFrame with mixed dtypes."""
        df = pd.DataFrame({
            'int_col': [1, 2, 3],
            'float_col': [1.1, 2.2, 3.3],
            'str_col': ['a', 'b', 'c'],
            'cat_col': pd.Categorical(['x', 'y', 'x']),
            'dt_col': pd.to_datetime(['2021-01-01', '2021-01-02', '2021-01-03']),
            'bool_col': [True, False, True],
            'nullable_int': pd.Series([1, 2, None], dtype='Int64')
        })
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        # Check that all different dtypes are handled correctly
        pandas_dtypes = [m.pandas_dtype for m in metadata_list]
        
        assert 'int64' in pandas_dtypes
        assert 'float64' in pandas_dtypes
        assert 'object' in pandas_dtypes
        assert any('category[' in dt for dt in pandas_dtypes)
        assert any('datetime64' in dt for dt in pandas_dtypes)
        assert 'bool' in pandas_dtypes
        assert 'nullable_int64' in pandas_dtypes
    
    def test_very_large_column_count(self):
        """Test with many columns (performance and memory test)."""
        # Create DataFrame with many columns
        data = {}
        for i in range(100):
            data[f'col_{i}'] = [1, 2, 3] if i % 2 == 0 else ['a', 'b', 'c']
        
        df = pd.DataFrame(data)
        
        # Should handle many columns without issues
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        assert len(metadata_list) == 100
        for metadata in metadata_list:
            assert hasattr(metadata, 'pandas_dtype')
            assert isinstance(metadata.pandas_dtype, str)
    
    def test_empty_dataframe(self):
        """Test with empty DataFrame."""
        df = pd.DataFrame()
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        assert metadata_list == []
    
    def test_single_column_dataframe(self):
        """Test with single column DataFrame."""
        df = pd.DataFrame({'single_col': [1, 2, 3]})
        
        metadata_list = infer_metadata_from_dataframe(df, warn_user=False)
        
        assert len(metadata_list) == 1
        assert metadata_list[0].pandas_dtype == 'int64'
        assert metadata_list[0].data_type == 'integer'


if __name__ == "__main__":
    pytest.main([__file__])