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

import re
from teradatasqlalchemy.types import *
from teradataml import execute_sql
from teradataml.common.garbagecollector import GarbageCollector
from teradataml.common.constants import TeradataConstants
from teradataml.common.utils import UtilFuncs

def _get_or_create_internal_array_udt(val=None,  **kwargs):
    """
    DESCRIPTION:
        Internal function to create or retrieve an existing User Defined Type (UDT) for Teradata array types.

    PARAMETERS:
        val:
           Optional Argument.
           Specifies the Array object for which to create or retrieve the UDT.
           Types: Array

        kwargs:
            Optional Argument.
            Specifies keyword arguments.  

            atype:
                Optional Argument.
                Specifies the array type directly for which to create or retrieve the UDT.
                Types: Array type
           
            Note: Either 'val' or 'atype' must be provided.

    RETURNS:
        The name of the UDT that was created or already existed.

    RAISES:
        TeradataMLException, ValueError

    """
    atype = kwargs.get('atype', None)

    if val is None and atype is None:
        raise ValueError("Either 'val' or 'atype' must be provided.")
    
    # Extract array type and generate UDT operations.
    if val is not None:
        # Extract atype from Array object.
        array_type = val.atype
    else:
        # Use provided atype directly.
        array_type = atype
    
    udt_name = array_type.udt_name

    # Create UDT SQL.
    try:
        UtilFuncs._execute_ddl_statement(array_type._generate_udt_create_sql())
        # Add UDT to garbage collector.
        GarbageCollector._add_to_garbagecollector(udt_name, TeradataConstants.TERADATA_UDT)

    except Exception as err:
        # Only catch specific error for UDT already exists (Error 6832).
        error_str = str(err)
        if (f"UDT '{udt_name}' already exists." in error_str or "6832" in error_str):
            pass
        else:
            raise

    return udt_name
