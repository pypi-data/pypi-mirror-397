# ################################################################## 
# 
# Copyright 2025 Teradata. All rights reserved.
# TERADATA CONFIDENTIAL AND TRADE SECRET
#
# Primary Owner: antra.joshi@teradata.com
# Secondary Owner: PankajVinod.Purandare@teradata.com
# 
# ################################################################## 

"""
This module contains User Defined Functions (UDFs) for array operations
similar to PySpark functionality.

These UDFs are designed to work with Teradata array string representations
and provide operations like sorting, joining, slicing, and set operations.

Note:
    Before performing any UDF based array operations on Array type columns,
    One should properly format the values received from the database in the UDFs.
    The following steps are needed to standardize the array’s string representation:

    1. If the input array is an empty string, return it as is.
    2. While reading the data from CSV, the array is read as a string with extra quotes.
       For example, an array like (1,2,3) will read as '"(1,2,3)"'. So, we need to
       remove the extra quotes before processing. This can be done using: arr = arr[1:-1]
    3. Replace SQL NULL with Python None using replace() method.
    4. Float values in scientific notation need special handling to avoid spaces.
       This can be done using regular expressions to remove spaces after 'E' or 'e':
    5. Evaluate the string to convert it into a Python tuple using eval().
    6. Convert 'None' strings back to Python None.
    7. After processing, convert the Python list/tuple back to string representation
       Also make sure to convert Python None back to SQL NULL in the final output.
    8. Return the formatted string representation of the array.

    Example of formatting:
        if len(arr) == 0:
            return arr
        if arr.startswith('"') and arr.endswith('"'):
            arr = arr[1:-1]
        arr = arr.replace("NULL", "None")
        import re
        arr = re.sub(r"E\s*([+-]?\d+)", r"E\\1", arr)
        arr = eval(arr)
        arr = [None if str(item).upper() == "NONE" else item for item in arr]
        # Perform array operations...
        return str(tuple(result)).replace("None", "NULL")
"""

ARRAY_UDF_UTILITY_FUNCTIONS = '''
def _format_array_input(arr, column_type=None):
    """
    DESCRIPTION:
        Utility function to format array string representation to Python tuple.
        Handles None values, quote removal, NULL replacement, and scientific notation.
        Also handles special array types like ARRAY_DATE, ARRAY_TIMESTAMP, ARRAY_INTERVAL.
    
    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str
        
    RETURNS:
        Formatted Python tuple and flag indicating early return for None value.
    """
    if len(arr) == 0:
        return arr, True
    
    # Check if type of the array is ARRAY_DATE, ARRAY_TIMESTAMP, or ARRAY_INTERVAL
    is_special_array = column_type in ['ARRAY DATE', 'ARRAY TIMESTAMP', 'ARRAY INTERVAL']

    if arr.startswith('"') and arr.endswith('"'):
        arr = arr[1:-1]
    
    if is_special_array:
        # For date, timestamp, and interval arrays, treat as array of strings
        # Handle the special format like '(2025-10-15,2025-10-15,2025-10-15)'
        if arr.startswith("(") and arr.endswith(")"):
            arr = arr[1:-1]  # Remove '( and )'
            # Split by comma and create tuple of strings
            if arr:
                elements = [elem.strip() for elem in arr.split(',')]
                arr = tuple(None if x == "NULL" else x for x in elements)
            else:
                arr = ()
        return arr, False
    else:
        arr = arr.replace("NULL", "None")
        # Import re module within the function for UDF compatibility
        import re
        arr = re.sub(r"E\s*([+-]?\d+)", r"E\\1", arr)
        arr = eval(arr)
        arr = arr if isinstance(arr, tuple) else (arr,)
        return arr, False

def _format_array_output(result, column_type=None):
    """
    DESCRIPTION:
        Utility function to format Python tuple/list back to array string representation.
        Handles empty arrays, single elements, NULL conversion, and special array types.
    
    PARAMETERS:
        result:
            Required Argument.
            Specifies the Python tuple/list representation of the array.
            Types: tuple OR list

        column_type:
            Optional Argument.
            Specifies the column type for the array.
            Note:
                * The output array type will remain consistent with the input type.
                  Hence `column_type` for output formatting is same as that of input formatting.
            Types: str

    RETURNS:
        String representation of array
    """
    if not result:
        return "()"
    
    # Check if this is a special array type that needs custom handling
    is_special_array = column_type in ['ARRAY DATE', 'ARRAY TIMESTAMP', 'ARRAY INTERVAL']

    if is_special_array:
        # For date, timestamp, and interval arrays, return in the original format
        if len(result) == 1:
            res = f"({result[0]})"
        else:
            # Create comma-separated string of elements
            elements_str = ','.join("NULL" if elem is None else str(elem) for elem in result)
            res = f"({elements_str})"
    else:
        # Regular array formatting
        if len(result) == 1:
            element = result[0]
            res = f"('{element}')" if isinstance(element, str) else f"({element})"
        else:
            res = str(tuple(result))
    return res.replace("None", "NULL")
'''

get_array_utility_functions = lambda: ARRAY_UDF_UTILITY_FUNCTIONS

def is_array_udf_function(func_name):
    """
    DESCRIPTION:
        Checks if a function name corresponds to an array UDF function.
        
    PARAMETERS:
        func_name:
            Required Argument.
            Specifies the name of the function to check.
            Types: str
        
    RETURNS:
        Boolean indicating if it's an array UDF function
    """
    array_udf_functions = [
        'td_array_sort', 'td_array_join', 'td_array_slice', 'td_array_overlap',
        'td_array_insert', 'td_array_remove', 'td_array_distinct', 'td_array_intersect',
        'td_array_union', 'td_array_except', 'td_array_compact', 'td_array_position',
        'td_shuffle', 'td_array_reverse', 'td_sequence', 'td_array_repeat'
    ]
    return func_name in array_udf_functions

def td_array_sort(arr, elements_order, nulls_order, column_type=None):
    """
    DESCRIPTION:
        UDF to sort array elements in ascending or descending order.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to be sorted.
            Types: str

        elements_order:
            Required Argument.
            Specifies the order in which the elements to be sorted.
            Permitted Values: ASC, DESC
            Types: str

        nulls_order:
            Required Argument.
            Specifies whether NULL values should appear first or last in the sorted array.
            Permitted Values: 'FIRST', 'LAST'
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Sorted array as string representation.

    EXAMPLES:
        >>> td_array_sort("(3,1,2)", 'ASC', 'LAST')
    """
    # Use unified formatting function
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    
    arr_gen = (None if str(item).upper() == "NONE" else item for item in arr)
    # Sort the array while handling None values
    nones = (x for x in arr_gen if x is None)
    sorted_values = sorted((x for x in arr if x is not None), reverse=(elements_order != 'ASC'))
    sorted_arr = (list(nones) + sorted_values if nulls_order == 'FIRST' else sorted_values + list(nones))

    return _format_array_output(sorted_arr, column_type)

def td_array_join(arr, delimiter, null_replacement, column_type=None):
    """
    DESCRIPTION:
        UDF to join array elements into a single string with a specified delimiter.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to be joined.
            Types: str

        delimiter:
            Required Argument.
            Specifies the delimiter to use between elements in the resulting string.
            Types: str

        null_replacement:
            Required Argument.
            Specifies the string to replace None values in the array.
            Types: None OR str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Joined string of array elements.

    EXAMPLES:
        >>> td_array_join("(1,2,NULL,4)", ",", "AB")
    """
    # Format the input array string representation to a Python tuple to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    
    # Generate the joined string with delimiter and null replacement.
    res_string = []
    for item in arr:
        val = None if str(item).upper() == "NONE" else item
        if val is None:
            if null_replacement is not None:
                res_string.append(str(null_replacement))
        else:
            res_string.append(str(val))
    return delimiter.join(res_string)

def td_array_slice(arr, start, length, column_type=None):
    """
    DESCRIPTION:
        UDF to slice an array from a specified start index for a given length.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to be sliced.
            Types: str

        start:
            Required Argument.
            Specifies the starting index for the slice (1-based).
            Types: int

        length:
            Required Argument.
            Specifies the number of elements to include in the slice.
            Types: int

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Sliced array as string representation.

    EXAMPLES:
        >>> td_array_slice("(1,2,3)", 2, 2)
    """
    # Format the input array string representation to a Python list to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    arr = list(arr) if isinstance(arr, tuple) else [arr]
        
    # Convert 1-based index to 0-based, handle negatives.
    start_idx = len(arr) + start if start < 0 else start - 1
    end_idx = start_idx + length

    # Handle out of bounds start index. 
    if start_idx < 0 or start_idx >= len(arr):
        return "()"
    sliced = arr[start_idx:end_idx]
    
    # Format the resultant array back to string representation
    return _format_array_output(sliced, column_type)

def td_array_overlap(arr1, arr2, column_type=None):
    """
    DESCRIPTION:
        UDF to check if two arrays have any elements in common.

    PARAMETERS:
        arr1:
            Required Argument.
            Specifies the string representation of the first array to compare.
            Types: str

        arr2:
            Required Argument.
            Specifies the string representation of the second array to compare.
            Types: str  

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Boolean indicating if there is any overlap between the two arrays.

    EXAMPLES:
        >>> td_array_overlap("(1,2,3)", "(3,4,5)")
    """

    # Format the first input array string representation to a Python list/tuple to process.
    arr1, is_none = _format_array_input(arr1, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr1
    arr1 = arr1 if isinstance(arr1, tuple) else [arr1]

    # Format the second input array string representation to a Python list/tuple to process.
    arr2, is_none = _format_array_input(arr2, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr2
    arr2 = arr2 if isinstance(arr2, tuple) else [arr2]

    # Check for overlap
    intersection = set(arr1).intersection(set(arr2))
    # If there's overlap and at least one non-NULL element, return True
    if len(intersection) > 0 and any(item is not None for item in intersection):
        return True
    # If no overlap but either array contains None (NULL), return None(i.e. '')
    if None in arr1 or None in arr2:
        return ''
    # No overlap and no NULLs, return False
    return False

def td_array_insert(arr, index, element, column_type=None):
    """
    DESCRIPTION:
        UDF to insert an element at a specified index in the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to process.
            Types: str

        index:
            Required Argument.
            Specifies the index at which to insert the element (1-based).
            Types: int

        element:
            Required Argument.
            Specifies the element to insert into the array.
            Types: Python literal

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array with element inserted as string representation.

    EXAMPLES:
        >>> td_array_insert("(1,2,3)", 2, 99)
    """
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr

    arr = list(arr) if isinstance(arr, tuple) else [arr]
    if index < 0:
        # Convert negative index to positive: -1 adds at end, -2 adds second-to-last, etc.
        index = max(1, len(arr) + index + 2)
    
    # Convert 1-based index to 0-based for Python list
    insert_idx = index - 1
    # If position is beyond array size, fill with NULLs 
    if insert_idx > len(arr):
        arr.extend([None] * (insert_idx - len(arr)))
    
    insert_idx = max(0, min(len(arr), insert_idx))
    arr.insert(insert_idx, element)
    
    # Format the resultant array back to string representation
    return _format_array_output(arr, column_type)

def td_array_remove(arr, element, column_type=None):
    """
    DESCRIPTION:
        UDF to remove all occurrences of an element from the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to process.
            Types: str

        element:
            Required Argument.
            Specifies the element to remove from the array.
            Types: Python literal 

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array with element removed as string representation.

    EXAMPLES:
        >>> td_array_remove("(1,2,2,3,NULL,3)", 2)
    """
    # Format the input array string representation to a Python list to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    arr = list(arr) if isinstance(arr, tuple) else [arr]
    
    # Remove all occurrences of the element
    result = [item for item in arr if item != element]
    
    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_distinct(arr, column_type=None):
    """
    DESCRIPTION:
        UDF to remove duplicate elements from the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to process.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array with duplicates removed as string representation. 

    EXAMPLES:
        >>> td_array_distinct("(1,2,2,3,NULL,3)")
    """
    # Format the input array string representation to a Python list to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    arr = list(arr) if isinstance(arr, tuple) else [arr]

    # Remove duplicates while preserving order
    distinct_arr = list(dict.fromkeys(arr))  
    
    # Format the resultant array back to string representation
    return _format_array_output(distinct_arr, column_type)

def td_array_intersect(arr1, arr2, column_type=None):
    """
    DESCRIPTION:
        UDF to find the intersection of two arrays.

    PARAMETERS:
       PARAMETERS:
        arr1:
            Required Argument.
            Specifies the string representation of the first array for intersection.
            Types: str

        arr2:
            Required Argument.
            Specifies the string representation of the second array for intersection.
            Types: str  

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array representing the intersection as string representation.

    EXAMPLES:
        >>> td_array_intersect("(1,2,3)", "(2,3,4)")
    """
    # Format the first array string representation to a Python list to process.
    arr1, is_none = _format_array_input(arr1, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr1
    arr1 = arr1 if isinstance(arr1, tuple) else [arr1]

    # Process second array string representation to a Python list to process.
    arr2, is_none = _format_array_input(arr2, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr2
    arr2 = arr2 if isinstance(arr2, tuple) else [arr2]
    
    # Find intersection while preserving order from first array
    set2 = set(arr2)
    result = []
    seen = set()
    for item in arr1:
        if item in set2 and item not in seen:
            result.append(item)
            seen.add(item)

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_union(arr1, arr2, column_type=None):
    """
    DESCRIPTION:
        UDF to return a union of two arrays.

    PARAMETERS:
        arr1:
            Required Argument.
            Specifies the string representation of the first array.
            Types: str

        arr2:
            Required Argument.
            Specifies the string representation of the second array.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array representing the union as string representation.

    EXAMPLES:
        >>> td_array_union("(1,2,3)", "(3,4,5)")
    """
    # Format first array string representation to a Python list to process.
    arr1, is_none = _format_array_input(arr1, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr1
    arr1 = arr1 if isinstance(arr1, tuple) else [arr1]

    # Process second array string representation to a Python list to process.
    arr2, is_none = _format_array_input(arr2, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr2
    arr2 = arr2 if isinstance(arr2, tuple) else [arr2]
    
    # Combine arrays and remove duplicates while preserving order
    result = list(dict.fromkeys(arr1 + arr2))

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_except(arr1, arr2, column_type=None):
    """
    DESCRIPTION:
        UDF to return elements from arr1 that are not in arr2.

    PARAMETERS:
        arr1:
            Required Argument.
            Specifies the string representation of the first array.
            Types: str

        arr2:
            Required Argument.
            Specifies the string representation of the second array.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array with elements from arr1 not in arr2 as string representation.

    EXAMPLES:
        >>> td_array_except("(1,2,3,4)", "(2,4)")
    """
    # Format first array string representation to a Python list to process.
    arr1, is_none = _format_array_input(arr1, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr1
    arr1 = arr1 if isinstance(arr1, tuple) else [arr1]

    # Process second array string representation to a Python list to process.
    arr2, is_none = _format_array_input(arr2, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr2
    arr2 = arr2 if isinstance(arr2, tuple) else [arr2]
    
    # Create set of elements to exclude
    exclude_set = set(arr2)
    # Keep only elements from arr1 that are not in arr2
    result = [item for item in arr1 if item not in exclude_set]

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_compact(arr, column_type=None):
    """
    DESCRIPTION:
        UDF to remove NULL values from the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to compact.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array with NULL values removed as string representation.

    EXAMPLES:
        >>> td_array_compact("(1,NULL,2,NULL,3)")
    """
    # Format the input array string representation to a Python list/tuple to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    arr = arr if isinstance(arr, tuple) else [arr]
    
    # Remove None values
    result = [item for item in arr if item is not None]

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_position(arr, element, column_type=None):
    """
    DESCRIPTION:
        UDF to find the position (1-based index) of an element in the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to search.
            Types: str

        element:
            Required Argument.
            Specifies the element to find in the array.
            Types: Python literal

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Integer position (1-based) of the element, or 0 if not found.

    EXAMPLES:
        >>> td_array_position("(1,2,3,2)", 2)
    """
    # Format the input array string representation to a Python list/tuple to process.
    arr, _ = _format_array_input(arr, column_type)
    arr = arr if isinstance(arr, tuple) else [arr]
    
    # Find the first occurrence of the element
    try:
        return arr.index(element) + 1  # Convert to 1-based index
    except ValueError:
        return 0  # Element not found

def td_shuffle(arr, column_type=None):
    """
    DESCRIPTION:
        UDF to randomly shuffle the elements of the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to shuffle.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Shuffled array as string representation.

    EXAMPLES:
        >>> td_shuffle("(1,2,3,4,5)")
    """
    # Import random module within the function for UDF compatibility
    import random
    
    # Format the input array string representation to a Python list/tuple to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    arr = list(arr) if isinstance(arr, tuple) else [arr]
    
    random.shuffle(arr)

    # Format the resultant array back to string representation
    return _format_array_output(arr, column_type)

def td_array_reverse(arr, column_type=None):
    """
    DESCRIPTION:
        UDF to reverse the order of elements in the array.

    PARAMETERS:
        arr:
            Required Argument.
            Specifies the string representation of the array to reverse.
            Types: str

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Reversed array as string representation.

    EXAMPLES:
        >>> td_reverse("(1,2,3,4,5)")
    """
    # Format the input array string representation to a Python list/tuple to process.
    arr, is_none = _format_array_input(arr, column_type)
    if is_none: # If input array is empty string, return as is.
        return arr
    
    arr = arr if isinstance(arr, tuple) else [arr]
    result = list(reversed(arr))

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_sequence(start, stop, step, column_type=None):
    """
    DESCRIPTION:
        UDF to generate a sequence of numbers from start to stop with given step.

    PARAMETERS:
        start:
            Required Argument.
            Specifies the starting value of the sequence (inclusive).
            Types: int

        stop:
            Required Argument.
            Specifies the ending value of the sequence (inclusive).
            Types: int

        step:
            Required Argument.
            Specifies the step size for the sequence.
            Default Value: 1
            Types: int

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array of sequence values as string representation.

    EXAMPLES:
        >>> td_sequence(1, 5, 1)
    """
    if step == 0:
        raise ValueError("Step cannot be zero")
    stop = stop+1 if step > 0 else stop-1
    result = list(range(start, stop, step))

    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)

def td_array_repeat(element, count, column_type=None):
    """
    DESCRIPTION:
        UDF to create an array containing the given element repeated count times.

    PARAMETERS:
        element:
            Required Argument.
            Specifies the element to repeat in the array.
            Types: Any

        count:
            Required Argument.
            Specifies the number of times to repeat the element.
            Types: int

        column_type:
            Optional Argument.
            Specifies the column type for the input array.
            Types: str

    RETURNS:
        Array containing the element repeated count times as string representation.

    EXAMPLES:
        >>> td_array_repeat('hello', 3)
    """
    # If count is less than or equal to zero, return an empty array
    if count <= 0:
        return "()"

    # Create an array with the element repeated 'count' times
    result = [element] * count
    
    # Format the resultant array back to string representation
    return _format_array_output(result, column_type)