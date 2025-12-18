# ################################################################## 
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: Kulkarni SriVaishnavi (kulkarni.srivaishnavi@teradata.com)
# Secondary Owner: Pradeep Garre (pradeep.garre@teradata.com)
# 
# Version: 1.0
# Function Version: 1.0
# 
# ################################################################## 

import inspect
from datetime import datetime
from teradataml.utils.validators import _Validators
from teradataml.utils.dtypes import _Dtypes
from teradataml.dataframe.sql_interfaces import ColumnExpression
from teradataml.common.exceptions import TeradataMlException
from teradataml.common.messagecodes import MessageCodes
from teradataml.common.messages import Messages
import teradatasqlalchemy.types as td_types
from teradataml.utils.internal_buffer import _InternalBuffer
from teradataml.common.constants import ArrayDefaults, TeradataTypes
import sqlalchemy as sqlalc
import numpy as np

class Array:
    """
    A class to represent an array in Teradata.
    """

    def __init__(self, elements, atype=None, default_null=False):
        """
        DESCRIPTION:
            Creates the object of Array.

        PARAMETERS:
            elements:
                Required Argument.
                Specifies the elements of similar Teradata types or literal values or numpy arrays
                to store in array.
                Note:
                    * If an empty tuple is provided, the atype defaults to ARRAY_VARCHAR with scope 100.
                Types: tuple

            atype:
                Optional Argument.
                Specifies the Teradata type of the array elements.
                If the argument is not specified, then teradataml infers the type
                based on the first element of the array. 
                Types: teradatasqlalchemy.types

            default_null:
                Optional Argument.
                Specifies whether the array type prepopulates the missing values 
                with NULL or not. When set to True, missing values are populated
                with NULL values, otherwise are undefined. 
                Default Value: False
                Types: bool

        RAISES:
            TeradataMlException, TypeError, ValueError

        EXAMPLES:
            >>> from teradataml import Array, DataFrame
            >>> from teradatasqlalchemy.types import ARRAY_INTEGER, ARRAY_FLOAT, ARRAY_NUMBER
            >>> import datetime
            
            # Set up DataFrame for examples.
            >>> load_example_data("DataFrame", "sales")
            >>> df = DataFrame("sales")

            # Example 1: Creating an Array with literal values.
            >>> Array((1, 2, 3))
            Array [elements=(1, 2, 3), atype=ARRAY_INTEGER, default_null=False]

            # Example 2: Creating an Array with DataFrame columns.
            >>> array_cols = Array((df.Jan, df.Feb), atype=ARRAY_NUMBER('[1:2]'))
            >>> print(array_cols.elements[0].name)
            'Jan'
            >>> array_cols.atype
            ARRAY_NUMBER('[1:2]')

            # Example 3: Creating an Array with both columns and literal values.
            >>> array_mixed = Array((df.Jan, 100, df.Feb, 200), atype=ARRAY_NUMBER('[1:4]'))
            >>> array_mixed.elements[1]
            100
            >>> print(len(array_mixed.elements))
            4

            # Example 4: Creating an Array to store DATE type values.
            >>> arr_dates = Array((datetime.date(2024, 6, 20), datetime.date(2025, 6, 2)))
            >>> print(arr_dates)
            Array [elements=(datetime.date(2024, 6, 20), datetime.date(2025, 6, 2)), atype=ARRAY_DATE, 
            default_null=False]

            # Example 5: Creating an Array with Timestamp type elements.
            >>> from teradatasqlalchemy.types import ARRAY_TIMESTAMP
            >>> arr_timestamp = Array(datetime.datetime(2024, 6, 20, 12, 0, 0), datetime.datetime(2025, 6, 2, 15, 30, 0)),
            ...                    atype=ARRAY_TIMESTAMP('[2]', timezone=True))
            >>> print(arr_timestamp)
            Array [elements=(datetime.datetime(2024, 6, 20, 12, 0), datetime.datetime(2025, 6, 2, 15, 30)), 
            atype=ARRAY_TIMESTAMP, default_null=False]

            # Example 6: Creating an Array with numpy arrays as elements.
            >>> import numpy as np
            >>> arr_numpy = Array((np.array([1, 2, 3]), np.array([4, 5, 6])))
            >>> print(arr_numpy)
            Array [elements=(array([1, 2, 3]), array([4, 5, 6])), atype=ARRAY_INTEGER, default_null=False]

        """
        self.elements = elements
        self.atype = atype
        self.default_null = default_null

        arg_matrix = []
        arg_matrix.append(["atype", self.atype, True, TeradataTypes.TD_ARRAY_TYPES.value])
        arg_matrix.append(["elements", self.elements, False, (tuple,)])
        arg_matrix.append(["default_null", self.default_null, True, (bool,)])

        _Validators._validate_function_arguments(arg_matrix)

        # Infer atype if not provided and elements are present.
        if (self.atype is None or isinstance(self.atype, sqlalc.sql.sqltypes.NullType)) \
            and self.elements and len(self.elements) > 0:
            
            first_scalar = self._get_first_element(self.elements)
            # If elements contain numpy arrays, extract their first scalar element
            if isinstance(first_scalar, np.ndarray):
                # empty numpy arrays should be treated as no element
                first_scalar = first_scalar.flat[0] if first_scalar.size > 0 else None
           
            # Convert numpy scalar types to native python scalars so _Dtypes can map them
            if isinstance(first_scalar, np.generic):
                first_scalar = first_scalar.item()

            # Get the type of the first element and convert it to primitive Teradata type
            td_type = _Dtypes._python_type_to_teradata_type(type(first_scalar)) \
                      if not isinstance(first_scalar, ColumnExpression) else first_scalar.type

            has_timezone = False
            # If we have a datetime type, we need to check if any elements have timezone info
            if isinstance(first_scalar, datetime):
                # Check if any element in the array has timezone info
                if first_scalar.tzinfo is not None:
                    has_timezone = True
                    td_type = td_types.TIMESTAMP(timezone=True)
                
                
            td_type = td_type or td_types.VARCHAR(1024)  # Default to VARCHAR if type is not found.
            # Get the corresponding Teradata Array type class.
            array_type_map, supported_array_types = self._get_array_types_info()
            array_type_cls = array_type_map.get(td_type.__visit_name__.upper())
            
            if array_type_cls is not None:
                scope = self._infer_scope(self.elements)
                # Get configuration values for the array type.
                config_kwargs = self._get_config_for_type(array_type_cls.__name__)
                config_kwargs['default_null'] = self.default_null

                # Use inspect to filter only supported arguments for the array type constructor.
                # Example:
                # Suppose the array type constructor signature is:
                #   (self, scope, default_null=False, length=100, charset=None, **kwargs)
                # Then supported_params will be:
                #   {'scope', 'default_null', 'length', 'charset', 'kwargs'}
                #
                # If config_kwargs is:
                #   {'length': 30, 'default_null': False, 'extra_param': 'ignored'}
                #
                # After filtering, filtered_kwargs will be:
                #   {'length': 30, 'default_null': False}
                #
                # Only keys in supported_params are included in filtered_kwargs.
                # This ensures that only valid arguments are passed to the constructor.
                sig = inspect.signature(array_type_cls.__init__)
                supported_params = set(sig.parameters.keys()) - {'self'}
                filtered_kwargs = {k: v for k, v in config_kwargs.items() if k in supported_params}

                self.atype = array_type_cls(scope, **filtered_kwargs)
                # If any element has timezone, set timezone=True for ARRAY_TIMESTAMP
                if array_type_cls.__name__ == 'ARRAY_TIMESTAMP' and has_timezone:
                    self.atype.timezone = True
            else:
                self.atype = None
        else:
            if self.atype is None:
                #  assign atype as array_varchar if not provided
                self.atype = td_types.ARRAY_VARCHAR(self._infer_scope(self.elements))
            # Still need to get supported_array_types for validation
            _, supported_array_types = self._get_array_types_info()
            
            # Apply configurations to explicitly provided atype
            if self.atype is not None:
                self._apply_config_to_existing_type()

    def _apply_config_to_existing_type(self):
        """
        DESCRIPTION:
            Apply configuration values to an existing array type.

        PARAMETERS:
            None

        RETURNS:
            None
        """
        type_name = self.atype.__class__.__name__
        config = self._get_config_for_type(type_name)
        
        # Apply each configuration value if it exists
        for attr, value in config.items():
            if value is not None:
                setattr(self.atype, attr, value)
        
        # Ensure default_null is set
        self.atype.default_null = self.default_null or self.atype.default_null

    def _get_config_for_type(self, type_name):
        """
        DESCRIPTION:
            Get the configuration values for a specific array type.

        PARAMETERS:
            type_name: 
                Required Argument.
                The name of the array type class.
                Types: str

        RETURNS:
            dict
        """
        # Mapping of array type names to required config keys
        type_config_map = {
            'ARRAY_DECIMAL': ['decimal_precision', 'decimal_scale'],
            'ARRAY_NUMBER': ['number_precision', 'number_scale'],
            'ARRAY_CHAR': ['char_length'],
            'ARRAY_VARCHAR': ['char_length'],
            'ARRAY_BYTE': ['byte_length'],
            'ARRAY_VARBYTE': ['byte_length'],
            'ARRAY_TIME': ['time_precision'],
            'ARRAY_TIMESTAMP': ['timestamp_precision'],
            'ARRAY_INTERVAL_DAY_TO_SECOND': ['interval_precision', 'interval_frac_precision'],
            'ARRAY_INTERVAL_HOUR_TO_SECOND': ['interval_precision', 'interval_frac_precision'],
            'ARRAY_INTERVAL_MINUTE_TO_SECOND': ['interval_precision', 'interval_frac_precision'],
            'ARRAY_INTERVAL_SECOND': ['interval_precision', 'interval_frac_precision'],
            'ARRAY_INTERVAL_YEAR': ['interval_precision'],
            'ARRAY_INTERVAL_YEAR_TO_MONTH': ['interval_precision'],
            'ARRAY_INTERVAL_MONTH': ['interval_precision'],
            'ARRAY_INTERVAL_DAY': ['interval_precision'],
            'ARRAY_INTERVAL_DAY_TO_HOUR': ['interval_precision'],
            'ARRAY_INTERVAL_DAY_TO_MINUTE': ['interval_precision'],
            'ARRAY_INTERVAL_HOUR': ['interval_precision'],
            'ARRAY_INTERVAL_HOUR_TO_MINUTE': ['interval_precision'],
            'ARRAY_INTERVAL_MINUTE': ['interval_precision']
        }

        config = {}
        config_keys = type_config_map.get(type_name, [])
        for key in config_keys:
            config_name = 'length' if key == 'char_length' and type_name in ('ARRAY_CHAR', 'ARRAY_VARCHAR') else key
            value = _InternalBuffer.get(key)
            if value is not None:
                config[config_name] = value
        return config

    def _get_array_types_info(self):
        """
        DESCRIPTION:
            Dynamically get all ARRAY types from teradatasqlalchemy.types and build
            both the type mapping and supported types tuple.

        PARAMETERS:
            None

        RETURNS:
            tuple
        """
        array_type_map = {}
        supported_array_types_list = []

        for attr_name in dir(td_types):
            if attr_name.startswith('ARRAY_'):
                array_type_class = getattr(td_types, attr_name)
                # Add to supported types list
                supported_array_types_list.append(array_type_class)
                # Extract base type name and add to mapping
                base_type_name = attr_name[6:]  # Remove 'ARRAY_' prefix
                array_type_map[base_type_name] = array_type_class

        # Convert list to tuple for supported array types
        supported_array_types = tuple(supported_array_types_list)
        
        return array_type_map, supported_array_types

    def _infer_scope(self, elements):
        """
        DESCRIPTION:
            Infers scope of the array based on the provided elements structure.
            Traverses the nested structure until finding the first tuple element.

        PARAMETERS:
            elements: 
                Required Argument.
                Specifies the elements of the array to infer dimension.
                Types: tuple

        RETURNS:
            The scope of the array.
        """
        # Get array size from internal buffer (defaults are pre-populated)
        default_array_size = _InternalBuffer.get("default_array_size") or \
                             ArrayDefaults.DEFAULT_ARRAY_SIZE.value

        dimension = 1
        if len(elements) == 0 or elements is None:
            return f'[{default_array_size}]'
        
        curr = elements[0]
        while isinstance(curr, tuple) and curr:
            dimension += 1
            curr = curr[0]

        scope = ''.join([f'[{default_array_size}]'] * dimension)
        return scope

    def _get_first_element(self, elements):
        """
        DESCRIPTION:
            Recursively get the first non-tuple, non-None element.
            If all elements are None, return the first element (None).

        PARAMETERS:
            elements: 
                Required Argument.
                Specifies the elements of the array to infer dimension.
                Types: tuple

        RETURNS:
            The first non-tuple, non-None element.
        """
        # Support numpy arrays as iterable containers similar to tuple/list
        if isinstance(elements, np.ndarray):
            if elements.size == 0:
                return None
            for item in elements.flat:
                result = self._get_first_element(item)
                if result is not None and not isinstance(result, tuple):
                    return result
            # If all elements are None or tuples, return first flattened element
            return None

        if isinstance(elements, tuple) and elements:
            for item in elements:
                result = self._get_first_element(item)
                if result is not None and not isinstance(result, tuple):
                    return result
            return self._get_first_element(elements[0])

        return elements
            
    def __repr__(self):
        """
        DESCRIPTION:
            String representation of Array object.

        RETURNS:
            str

        EXAMPLES:
            >>> arr = Array(1.2, 4.3)
            >>> print(arr)
            Array [elements=(1.2, 4.3), atype=ARRAY_FLOAT, default_null=False]
        """
        return "{} [elements={}, atype={}, default_null={}]".format(self.__class__.__name__,
                                                                     self.elements,
                                                                     self.atype.__class__.__name__,
                                                                     self.default_null)