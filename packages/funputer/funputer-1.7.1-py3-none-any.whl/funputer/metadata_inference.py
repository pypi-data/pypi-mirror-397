"""
Automatic metadata inference from pandas DataFrames.

Simplified functional approach for intelligent column metadata detection
when no explicit metadata file is provided.
"""

import pandas as pd
import numpy as np
import logging
import warnings
from typing import List, Dict, Optional, Tuple, Set
from datetime import datetime
import re
import sys

from .models import ColumnMetadata, FIELD_DEFAULTS

# Suppress pandas warnings for cleaner output
warnings.filterwarnings("ignore", category=pd.errors.DtypeWarning)
warnings.filterwarnings("ignore", message="Could not infer format")
warnings.filterwarnings("ignore", message=".*falling back to `dateutil`.*")

logger = logging.getLogger(__name__)


# Configuration constants
CATEGORICAL_THRESHOLD_RATIO = 0.1
CATEGORICAL_THRESHOLD_ABSOLUTE = 50
DATETIME_SAMPLE_SIZE = 100
MIN_ROWS_FOR_STATS = 10
MIN_UNIQUE_THRESHOLD = 20
SEQUENTIAL_ID_THRESHOLD = 0.8

# Pattern recognition constants
DATETIME_PATTERNS = [
    r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
    r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
    r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
    r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
]

ID_INDICATORS = ["id", "key", "pk", "uuid", "guid", "_id", "identifier"]
TIME_INDICATORS = ["time", "date", "timestamp", "created", "updated", "modified"]
GROUP_INDICATORS = ["category", "group", "type", "class", "status", "state", "region", "department"]


def _get_normalized_pandas_dtype(column_data: pd.Series) -> str:
    """
    Get normalized pandas dtype string with robust handling of all edge cases.
    
    This function provides a consistent, future-proof representation of the actual
    pandas storage dtype, handling platform differences, nullable types, extensions,
    and unknown future dtypes.
    
    Args:
        column_data: Pandas Series to analyze
        
    Returns:
        Normalized string representation of pandas dtype
    """
    try:
        # Get the raw pandas dtype
        raw_dtype = column_data.dtype
        dtype_str = str(raw_dtype)
        
        # Handle pandas categorical dtype (special case)
        if hasattr(raw_dtype, 'name') and raw_dtype.name == 'category':
            # For categorical, also capture the underlying categories dtype
            try:
                cat_dtype = str(raw_dtype.categories.dtype)
                return f"category[{cat_dtype}]"
            except:
                return "category[object]"
        
        # Handle nullable integer types (Int64, Int32, etc.)
        if hasattr(raw_dtype, 'name') and raw_dtype.name in ['Int8', 'Int16', 'Int32', 'Int64']:
            return f"nullable_{raw_dtype.name.lower()}"
        
        # Handle nullable boolean
        if hasattr(raw_dtype, 'name') and raw_dtype.name == 'boolean':
            return "nullable_boolean"
        
        # Handle string dtype (pandas >= 1.0)
        if hasattr(raw_dtype, 'name') and raw_dtype.name == 'string':
            return "string_dtype"
        
        # Handle datetime with timezone
        if hasattr(raw_dtype, 'tz') and raw_dtype.tz is not None:
            return f"datetime64[ns, {raw_dtype.tz}]"
        
        # Handle interval dtype (before subtype check since intervals have subtype too)
        if 'interval' in dtype_str.lower():
            return dtype_str
        
        # Handle period dtype
        if hasattr(raw_dtype, 'freq') and 'period' in dtype_str.lower():
            return f"period[{raw_dtype.freq}]"
        
        # Handle sparse arrays (after interval check)
        if hasattr(raw_dtype, 'subtype'):
            return f"sparse[{raw_dtype.subtype}]"
        
        # Handle extension dtypes (GeoPandas, etc.)
        if hasattr(raw_dtype, '_name'):
            return raw_dtype._name
        
        # Platform normalization for standard dtypes
        dtype_mappings = {
            # Integer types - normalize platform differences
            'int': f'int{sys.maxsize.bit_length() + 1}',  # Platform default int
            'uint': f'uint{sys.maxsize.bit_length() + 1}',  # Platform default uint
            # Keep specific bit widths as-is
        }
        
        # Apply platform normalization
        for pattern, replacement in dtype_mappings.items():
            if dtype_str == pattern:
                return replacement
        
        # Handle complex dtypes
        if 'complex' in dtype_str:
            return dtype_str
        
        # Handle timedelta
        if 'timedelta' in dtype_str:
            return dtype_str
        
        # Default: return the string representation as-is
        # This handles standard dtypes (int64, float64, object, etc.)
        # and provides forward compatibility for unknown future dtypes
        return dtype_str
        
    except Exception as e:
        # Ultimate fallback for any unexpected errors
        logger.warning(f"Failed to normalize pandas dtype: {e}")
        try:
            # Try simple string conversion as last resort
            return str(column_data.dtype)
        except:
            # Absolute fallback
            return "unknown_dtype"


def infer_metadata_from_dataframe(
    df: pd.DataFrame, warn_user: bool = True, config=None, **kwargs
) -> List[ColumnMetadata]:
    """
    Infer metadata for all columns in a DataFrame with optional configuration.
    
    Args:
        df: Input DataFrame
        warn_user: Whether to warn user about inference limitations
        config: Optional AnalysisConfig for percentile configuration
        **kwargs: Additional arguments (maintained for compatibility)
        
    Returns:
        List of ColumnMetadata objects
    """
    if df.empty:
        logger.warning("Empty DataFrame provided - no metadata to infer")
        return []

    if warn_user:
        logger.info(f"Inferring metadata for {len(df.columns)} columns from {len(df)} rows")

    metadata_list = []
    
    for column_name in df.columns:
        try:
            metadata = _infer_column_metadata(df, column_name, config)
            metadata_list.append(metadata)
        except Exception as e:
            logger.warning(f"Failed to infer metadata for column '{column_name}': {e}")
            # Create fallback metadata with both storage and semantic types
            try:
                fallback_pandas_dtype = _get_normalized_pandas_dtype(df[column_name])
            except:
                fallback_pandas_dtype = 'object'  # Ultimate fallback
            
            metadata = ColumnMetadata(
                column_name=column_name,
                pandas_dtype=fallback_pandas_dtype,
                data_type='string',
                description=f'Failed inference for {column_name}'
            )
            metadata_list.append(metadata)

    if warn_user and metadata_list:
        logger.info(f"Successfully inferred metadata for {len(metadata_list)} columns")

    return metadata_list


def _infer_column_metadata(df: pd.DataFrame, column_name: str, config=None) -> ColumnMetadata:
    """Infer metadata for a single column with optional configuration.
    
    Args:
        df: DataFrame containing the column
        column_name: Name of the column to analyze
        config: Optional AnalysisConfig for percentile configuration
        
    Returns:
        ColumnMetadata object with inferred properties including both
        actual pandas storage dtype and semantic data type classification
    """
    column_data = df[column_name]
    
    # Get actual pandas storage dtype (NEW: foolproof storage type detection)
    pandas_dtype = _get_normalized_pandas_dtype(column_data)
    
    # Get semantic data type classification (existing logic)
    data_type = _infer_data_type(column_data)
    
    # Constraints and properties
    constraints = _infer_constraints(column_data, data_type, config)
    
    # Column characteristics
    unique_flag = _infer_uniqueness(column_data)
    role = _infer_role(column_name, column_data, unique_flag)
    
    # Infer other boolean flags
    do_not_impute = _infer_do_not_impute(role, unique_flag)
    time_index = _infer_time_index(column_name, data_type)
    group_by = _infer_group_by(column_name, data_type, column_data)
    
    # Create metadata object with both storage and semantic types
    return ColumnMetadata(
        column_name=column_name,
        pandas_dtype=pandas_dtype,     # NEW: Actual pandas storage type
        data_type=data_type,           # Semantic type classification  
        description=_generate_description(column_name, data_type),
        role=role,
        do_not_impute=do_not_impute,
        time_index=time_index,
        group_by=group_by,
        unique_flag=unique_flag,
        nullable=True,  # Default to nullable
        **constraints
    )


def _infer_data_type(column_data: pd.Series) -> str:
    """Infer the data type of a column."""
    # Handle empty or all-null columns
    if column_data.isna().all():
        return 'string'
    
    # Get pandas dtype
    dtype = column_data.dtype
    
    # Numeric types
    if pd.api.types.is_integer_dtype(dtype):
        return 'integer'
    elif pd.api.types.is_float_dtype(dtype):
        return 'float'
    elif pd.api.types.is_bool_dtype(dtype):
        return 'boolean'
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return 'datetime'
    
    # Object dtype - need deeper analysis
    if dtype == 'object':
        return _infer_object_type(column_data)
    
    # Default fallback
    return 'string'


def _infer_object_type(column_data: pd.Series) -> str:
    """Infer type for object columns."""
    non_null = column_data.dropna()
    
    if len(non_null) == 0:
        return 'string'
    
    # Try datetime detection
    if _is_datetime_column(non_null):
        return 'datetime'
    
    # Try boolean detection
    if _is_boolean_column(non_null):
        return 'boolean'
    
    # Try integer detection
    if _could_be_integer(non_null):
        return 'integer'
    
    # Check if categorical
    if _is_categorical_column(non_null):
        return 'categorical'
    
    return 'string'


def _is_datetime_column(column_data: pd.Series) -> bool:
    """Check if column contains datetime values."""
    if len(column_data) == 0:
        return False
        
    sample_size = min(DATETIME_SAMPLE_SIZE, len(column_data))
    sample = column_data.head(sample_size).astype(str)
    
    # Check for common datetime patterns
    datetime_count = 0
    for value in sample:
        if any(re.search(pattern, str(value)) for pattern in DATETIME_PATTERNS):
            datetime_count += 1
    
    # If most values match datetime patterns, it's likely datetime
    return datetime_count / len(sample) > 0.7


def _is_boolean_column(column_data: pd.Series) -> bool:
    """Check if column contains boolean-like values."""
    unique_values = set(str(v).lower() for v in column_data.unique())
    boolean_values = {'true', 'false', '0', '1', 'yes', 'no', 'y', 'n'}
    
    return unique_values.issubset(boolean_values) and len(unique_values) <= 4


def _could_be_integer(column_data: pd.Series) -> bool:
    """Check if string column could be integer."""
    try:
        # Try to convert sample to numeric
        sample = column_data.head(100)
        converted = pd.to_numeric(sample, errors='coerce')
        
        # Check if conversion was successful and values are integers
        if converted.notna().sum() / len(sample) > 0.8:
            return (converted == converted.astype('Int64')).all()
    except:
        pass
    
    return False


def _is_categorical_column(column_data: pd.Series) -> bool:
    """Check if column should be treated as categorical."""
    unique_count = column_data.nunique()
    total_count = len(column_data)
    
    if total_count == 0:
        return False
    
    # Low unique ratio suggests categorical
    unique_ratio = unique_count / total_count
    
    return (unique_ratio <= CATEGORICAL_THRESHOLD_RATIO or 
            unique_count <= CATEGORICAL_THRESHOLD_ABSOLUTE)


def _infer_constraints(column_data: pd.Series, data_type: str, config=None) -> Dict:
    """Infer value constraints for the column with optional percentile ranges.
    
    Args:
        column_data: Pandas Series to analyze
        data_type: Data type of the column
        config: Optional AnalysisConfig for percentile configuration
        
    Returns:
        Dictionary of constraints including traditional and percentile-based ranges
    """
    constraints = {}
    
    if data_type in ['integer', 'float']:
        non_null = column_data.dropna()
        if len(non_null) > 0:
            # Traditional absolute bounds (always set for backward compatibility)
            constraints['min_value'] = float(non_null.min())
            constraints['max_value'] = float(non_null.max())
            
            # Percentile-based bounds (conditional on config and sample size)
            if config is not None and config.enable_percentile_ranges:
                if len(non_null) >= config.min_samples_for_percentiles:
                    threshold = config.default_percentile_threshold
                    lower_percentile = (100 - threshold) / 2
                    upper_percentile = 100 - lower_percentile
                    
                    try:
                        # Validate percentile calculations
                        if not (0 < lower_percentile < 100) or not (0 < upper_percentile < 100):
                            logger.warning(f"Invalid percentile range: {lower_percentile}-{upper_percentile}")
                            raise ValueError("Invalid percentile range calculated")
                        
                        p_low = non_null.quantile(lower_percentile / 100)
                        p_high = non_null.quantile(upper_percentile / 100)
                        
                        # Validate that percentiles are reasonable
                        if pd.isna(p_low) or pd.isna(p_high) or p_low > p_high:
                            logger.warning(f"Invalid percentile values: low={p_low}, high={p_high}")
                            raise ValueError("Invalid percentile values calculated")
                        
                        constraints['percentile_low'] = float(p_low)
                        constraints['percentile_high'] = float(p_high)
                        constraints['percentile_threshold'] = float(threshold)
                        
                    except Exception as e:
                        # If percentile calculation fails, leave as None and log warning
                        logger.warning(f"Percentile calculation failed for {data_type} column: {str(e)}")
                        constraints['percentile_low'] = None
                        constraints['percentile_high'] = None
                        constraints['percentile_threshold'] = None
                else:
                    # Insufficient samples for reliable percentiles
                    constraints['percentile_low'] = None
                    constraints['percentile_high'] = None
                    constraints['percentile_threshold'] = None
            else:
                # Percentiles disabled or no config provided
                constraints['percentile_low'] = None
                constraints['percentile_high'] = None
                constraints['percentile_threshold'] = None
    
    elif data_type == 'string':
        non_null = column_data.dropna().astype(str)
        if len(non_null) > 0:
            constraints['max_length'] = int(non_null.str.len().max())
            
            # Check if string column has categorical-like properties for frequency filtering
            if _is_categorical_column(column_data):
                frequency_stats = _filter_categorical_by_frequency(column_data, config)
                # Only apply frequency filtering results, not overriding string-specific constraints
                for key in ['allowed_values', 'total_categories', 'filtered_categories', 'frequency_threshold_used']:
                    if frequency_stats.get(key) is not None:
                        constraints[key] = frequency_stats[key]
    
    elif data_type == 'categorical':
        # For categorical data, apply frequency-based filtering if enabled
        frequency_stats = _filter_categorical_by_frequency(column_data, config)
        constraints.update(frequency_stats)
    
    return constraints


def _filter_categorical_by_frequency(column_data: pd.Series, config=None) -> dict:
    """
    Filter categorical values based on frequency thresholds.
    
    Args:
        column_data: Series containing categorical data
        config: Optional AnalysisConfig for frequency filtering settings
        
    Returns:
        Dictionary with frequency filtering results and statistics
    """
    # Initialize default values
    frequency_stats = {
        'allowed_values': None,
        'total_categories': None,
        'filtered_categories': None,
        'frequency_threshold_used': None,
        # NEW v1.7.0: Frequency-based categorical intelligence fields
        'unique_count': None,
        'top_value': None,
        'top_frequency': None
    }
    
    # Get non-null values
    non_null_data = column_data.dropna()
    if len(non_null_data) == 0:
        return frequency_stats
    
    # Calculate value counts
    value_counts = non_null_data.value_counts()
    total_categories = len(value_counts)
    frequency_stats['total_categories'] = total_categories
    
    # NEW v1.7.0: Populate frequency intelligence fields
    frequency_stats['unique_count'] = total_categories
    if len(value_counts) > 0:
        frequency_stats['top_value'] = str(value_counts.index[0])
        frequency_stats['top_frequency'] = int(value_counts.iloc[0])
    
    # Check if frequency filtering is enabled and we have enough samples
    if (config and 
        hasattr(config, 'enable_frequency_filtering') and 
        config.enable_frequency_filtering and
        len(non_null_data) >= getattr(config, 'min_samples_for_frequency_filtering', 20)):
        
        # Get frequency thresholds from config
        min_count = getattr(config, 'min_frequency_count', 5)
        min_percentage = getattr(config, 'min_frequency_percentage', 1.0)
        
        # Calculate actual threshold (use the more restrictive of count vs percentage)
        total_samples = len(non_null_data)
        percentage_threshold = (min_percentage / 100.0) * total_samples
        actual_threshold = max(min_count, percentage_threshold)
        
        # Filter values that meet the frequency threshold
        filtered_values = value_counts[value_counts >= actual_threshold]
        
        # Store results
        if len(filtered_values) > 0:
            # Only include categories that pass the frequency threshold
            allowed_values = list(filtered_values.index)
            frequency_stats['allowed_values'] = ','.join(str(v) for v in sorted(allowed_values))
            frequency_stats['filtered_categories'] = len(filtered_values)
            frequency_stats['frequency_threshold_used'] = actual_threshold
            
            # Log filtering results for debugging
            if len(filtered_values) < total_categories:
                excluded_count = total_categories - len(filtered_values)
                logger.info(f"Frequency filtering: {excluded_count}/{total_categories} categories excluded "
                           f"(threshold: {actual_threshold:.1f}, {min_percentage}%)")
        else:
            # No values meet threshold - fall back to traditional approach
            if total_categories <= 50:  # Reasonable limit for unfiltered categories
                frequency_stats['allowed_values'] = ','.join(str(v) for v in sorted(value_counts.index))
                frequency_stats['filtered_categories'] = total_categories
                frequency_stats['frequency_threshold_used'] = 0  # No filtering applied
    else:
        # Frequency filtering disabled or insufficient samples - use traditional approach
        if total_categories <= 50:  # Only for manageable number of values
            frequency_stats['allowed_values'] = ','.join(str(v) for v in sorted(value_counts.index))
            frequency_stats['filtered_categories'] = total_categories
            frequency_stats['frequency_threshold_used'] = 0  # No filtering applied
    
    return frequency_stats


def _infer_uniqueness(column_data: pd.Series) -> bool:
    """Check if column values should be unique."""
    non_null = column_data.dropna()
    
    if len(non_null) < 2:
        return False
    
    unique_ratio = non_null.nunique() / len(non_null)
    return unique_ratio > 0.95  # 95% unique suggests it should be unique


def _infer_role(column_name: str, column_data: pd.Series, unique_flag: bool) -> str:
    """Infer the role of the column."""
    column_lower = column_name.lower()
    
    # Check for identifier patterns
    if unique_flag and any(indicator in column_lower for indicator in ID_INDICATORS):
        return 'identifier'
    
    # Check for time index patterns
    if any(indicator in column_lower for indicator in TIME_INDICATORS):
        return 'time_index'
    
    # Check for grouping patterns
    if any(indicator in column_lower for indicator in GROUP_INDICATORS):
        return 'group_by'
    
    # Default to feature
    return 'feature'


def _infer_do_not_impute(role: str, unique_flag: bool) -> bool:
    """Determine if column should not be imputed."""
    return role == 'identifier' or unique_flag


def _infer_time_index(column_name: str, data_type: str) -> bool:
    """Check if column is a time index."""
    column_lower = column_name.lower()
    return (data_type == 'datetime' and 
            any(indicator in column_lower for indicator in TIME_INDICATORS))


def _infer_group_by(column_name: str, data_type: str, column_data: pd.Series) -> bool:
    """Check if column is suitable for grouping."""
    column_lower = column_name.lower()
    
    # Name-based detection
    if any(indicator in column_lower for indicator in GROUP_INDICATORS):
        return True
    
    # Data-based detection for categorical columns
    if data_type == 'categorical':
        unique_count = column_data.nunique()
        # Good grouping columns have reasonable number of groups
        return 2 <= unique_count <= 50
    
    return False


def _generate_description(column_name: str, data_type: str) -> str:
    """Generate a human-readable description."""
    return f"Auto-inferred {data_type} column: {column_name}"