"""
Copyright (c) 2024 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements constants required for Teradata Enterprise Feature Store.
"""

from teradatasqlalchemy.types import *
from enum import Enum

# Template for creating the triggers on
# corresponding tables.

# Tables for storing the data domains.
EFS_DATA_DOMAINS="""
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        created_time TIMESTAMP(6)
        )
    UNIQUE PRIMARY INDEX (name);
"""


# Tables for storing the features.
EFS_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        id INTEGER,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        column_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        tags VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_type VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_type VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        status VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES _efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain)
    UNIQUE INDEX (id);
"""

EFS_FEATURES_STAGING="""
    CREATE MULTISET TABLE {0}.{1}
        (
        id INTEGER,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        column_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        tags VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_type VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_type VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        status VARCHAR(100) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;
"""

EFS_FEATURES_TRG="""
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.id, DeletedRow.name, DeletedRow.data_domain, DeletedRow.column_name, DeletedRow.description, DeletedRow.tags, DeletedRow.data_type, DeletedRow.feature_type, DeletedRow.status, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

EFS_GROUP_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        feature_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),	
    CONSTRAINT feature_name_fk FOREIGN KEY (feature_name, feature_data_domain) REFERENCES {0}._efs_features (name, data_domain),
    CONSTRAINT group_name_fk FOREIGN KEY (group_name, group_data_domain) REFERENCES {0}._efs_feature_group (name, data_domain),
    CONSTRAINT data_domain_fk1 FOREIGN KEY (feature_data_domain) REFERENCES {0}._efs_data_domains (name),
    CONSTRAINT data_domain_fk2 FOREIGN KEY (group_data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (feature_name, feature_data_domain, group_name, group_data_domain);
"""

EFS_GROUP_FEATURES_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        feature_name VARCHAR(255),
        feature_data_domain VARCHAR(255),
        group_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        group_data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;  
"""

EFS_GROUP_FEATURES_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.feature_name, DeletedRow.feature_data_domain, DeletedRow.group_name, DeletedRow.group_data_domain, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );   
"""  

# Tables for Entities.

EFS_ENTITY = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_ENTITY_STAGING= """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX ;
"""

EFS_ENTITY_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

EFS_ENTITY_XREF= """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC, 
        entity_column VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC, 
    CONSTRAINT entity_xref_fk FOREIGN KEY (entity_name, data_domain) REFERENCES {0}._efs_entity (name, data_domain),
    CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (entity_name, data_domain, entity_column);
"""

EFS_ENTITY_XREF_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_column VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,      
        archived_time TIMESTAMP(6)
        )
    NO PRIMARY INDEX ;
"""

EFS_ENTITY_XREF_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.entity_name, DeletedRow.data_domain, DeletedRow.entity_column, 
                current_timestamp(6)
                );       
"""

# Table for Data sources.

EFS_DATA_SOURCE = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        timestamp_column VARCHAR(50) CHARACTER SET LATIN NOT CASESPECIFIC,
        source VARCHAR(5000) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_DATA_SOURCE_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(1024) CHARACTER SET LATIN NOT CASESPECIFIC,
        timestamp_column VARCHAR(50) CHARACTER SET LATIN NOT CASESPECIFIC,
        source VARCHAR(5000) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX;
"""

EFS_DATA_SOURCE_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.timestamp_column, DeletedRow.source, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

# Table for Feature groups.

EFS_FEATURE_GROUP = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6), 
    CONSTRAINT data_source_name_fk FOREIGN KEY (data_source_name, data_domain) REFERENCES {0}._efs_data_source (name, data_domain),
    CONSTRAINT entity_fk FOREIGN KEY (entity_name, data_domain) REFERENCES {0}._efs_entity (name, data_domain),
    CONSTRAINT data_domain_fk FOREIGN KEY (data_domain) REFERENCES {0}._efs_data_domains (name)
        )
    UNIQUE PRIMARY INDEX (name, data_domain);
"""

EFS_FEATURE_GROUP_STAGING = """
    CREATE MULTISET TABLE {0}.{1}
        (
        name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,      
        description VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_name VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6),
        modified_time TIMESTAMP(6),
        archived_time TIMESTAMP(6))
    NO PRIMARY INDEX ;
"""

EFS_FEATURE_GROUP_TRG = """
    CREATE TRIGGER {0}.{1}
    AFTER DELETE ON {0}.{2}
    REFERENCING OLD AS DeletedRow
    FOR EACH ROW
        INSERT INTO {3}
        VALUES (DeletedRow.name, DeletedRow.data_domain, DeletedRow.description, DeletedRow.data_source_name, DeletedRow.entity_name, DeletedRow.creation_time, DeletedRow.modified_time, 
                current_timestamp(6)
                );
"""

# Table for feature process.
EFS_FEATURE_PROCESS = """
    CREATE MULTISET TABLE {0}.{1}
        (
        process_id VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        description VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        process_type VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_source VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        entity_id VARCHAR(255) CHARACTER SET LATIN CASESPECIFIC,
        feature_names VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        feature_ids VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (process_id);
"""


EFS_FEATURE_RUNS = """
CREATE MULTISET TABLE {0}.{1}
        (
        run_id BIGINT GENERATED ALWAYS AS IDENTITY (START WITH 1 INCREMENT BY 1 MINVALUE 1 NO MAXVALUE NO CYCLE) NOT NULL,
        process_id VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        data_domain VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        start_time TIMESTAMP(6),
        end_time TIMESTAMP(6),
        status VARCHAR(20) CHARACTER SET LATIN NOT CASESPECIFIC,
        filter VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        as_of_start TIMESTAMP(6) WITH TIME ZONE,
        as_of_end TIMESTAMP(6) WITH TIME ZONE,
        failure_reason VARCHAR(2000) CHARACTER SET LATIN CASESPECIFIC)
    UNIQUE PRIMARY INDEX (run_id);
"""

# Table for storing the features metadata.
EFS_FEATURES_METADATA = """
    CREATE MULTISET TABLE {0}.{1}
        (
        entity_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_id BIGINT NOT NULL,
        table_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (entity_name);
"""

EFS_DATASET_CATALOG = """
    CREATE MULTISET TABLE {0}.{1}
        (
        id VARCHAR(36) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        entity_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        database_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        description VARCHAR(2000) CHARACTER SET LATIN NOT CASESPECIFIC,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (id);
"""

EFS_DATASET_FEATURES = """
    CREATE MULTISET TABLE {0}.{1}
        (
        dataset_id VARCHAR(36) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        data_domain VARCHAR(200) CHARACTER SET LATIN NOT CASESPECIFIC,
        feature_id BIGINT,
        feature_name VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_version VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_repo VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        feature_view VARCHAR(255) CHARACTER SET LATIN NOT CASESPECIFIC NOT NULL,
        valid_start TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        valid_end TIMESTAMP(6) WITH TIME ZONE NOT NULL,
        PERIOD FOR ValidPeriod  (valid_start, valid_end) AS VALIDTIME)
    PRIMARY INDEX (dataset_id);
"""

EFS_FEATURE_VERSION = """
CREATE VIEW {}.{} AS 
LOCK ROW FOR ACCESS
SELECT
    data_domain,
    entity_id,        
    trim(NGRAM) AS feature_name,
    PROCESS_ID as feature_version
FROM NGramSplitter (
    ON (
        SELECT * FROM {}.{}
        ) as paragraphs_input
        USING
            TextColumn ('FEATURE_NAMES')
            ConvertToLowerCase ('false')
            Grams ('1')
            Delimiter(',')
    ) AS dt; 
"""

# Select the archived records.
EFS_ARCHIVED_RECORDS = """
SELECT {}, 
CASE WHEN valid_end < current_timestamp then 1 else 0 end as is_archived 
FROM {} 
WHERE {}"""

# Table to store the version of feature store. This is very important.
# When teradataml incrementally adds functionality for feature store, this
# version will be deciding factor whether teradataml should automatically
# update metadata or not.

EFS_VERSION = """
    CREATE MULTISET TABLE {0}.{1} (
        version VARCHAR(20) CHARACTER SET LATIN NOT CASESPECIFIC,
        creation_time TIMESTAMP(6)
    );
"""

EFS_VERSION_ = "2.0.0"

EFS_DB_COMPONENTS = {
    "data_domain": "_efs_data_domains",
    "feature": "_efs_features",
    "feature_staging": "_efs_features_staging",
    "feature_trg": "_efs_features_trg",
    "group_features": "_efs_group_features",
    "group_features_staging": "_efs_group_features_staging",
    "group_features_trg": "_efs_group_features_trg",
    "entity": "_efs_entity",
    "entity_staging": "_efs_entity_staging",
    "entity_trg": "_efs_entity_trg",
    "entity_xref": "_efs_entity_xref",
    "entity_staging_xref": "_efs_entity_xref_staging",
    "entity_xref_trg": "_efs_entity_xref_trg",
    "data_source": "_efs_data_source",
    "data_source_staging": "_efs_data_source_staging",
    "data_source_trg": "_efs_data_source_trg",
    "feature_group": "_efs_feature_group",
    "feature_group_staging": "_efs_feature_group_staging",
    "feature_group_trg": "_efs_feature_group_trg",
    "feature_process": "_efs_feature_process",
    "feature_runs": "_efs_feature_runs",
    "feature_metadata": "_efs_features_metadata",
    "dataset_catalog": "_efs_dataset_catalog",
    "dataset_features": "_efs_dataset_features",
    "feature_version": "_efs_feature_version",
    "version": "_efs_version"
}


EFS_TABLES = {
    EFS_DATA_DOMAINS: "_efs_data_domains",
    EFS_FEATURES: "_efs_features",
    EFS_FEATURES_STAGING: "_efs_features_staging",
    EFS_GROUP_FEATURES: "_efs_group_features",
    EFS_GROUP_FEATURES_STAGING: "_efs_group_features_staging",
    EFS_ENTITY: "_efs_entity",
    EFS_ENTITY_STAGING: "_efs_entity_staging",
    EFS_ENTITY_XREF: "_efs_entity_xref",
    EFS_ENTITY_XREF_STAGING: "_efs_entity_xref_staging",
    EFS_DATA_SOURCE: "_efs_data_source",
    EFS_DATA_SOURCE_STAGING: "_efs_data_source_staging",
    EFS_FEATURE_GROUP: "_efs_feature_group",
    EFS_FEATURE_RUNS: "_efs_feature_runs",
    EFS_FEATURE_GROUP_STAGING: "_efs_feature_group_staging",
    EFS_FEATURE_PROCESS: "_efs_feature_process",
    EFS_FEATURES_METADATA: "_efs_features_metadata",
    EFS_DATASET_CATALOG: "_efs_dataset_catalog",
    EFS_DATASET_FEATURES: "_efs_dataset_features",
    EFS_VERSION: "_efs_version"
}

EFS_TRIGGERS = {
    EFS_FEATURES_TRG: "_efs_features_trg",
    EFS_GROUP_FEATURES_TRG: "_efs_group_features_trg",
    EFS_ENTITY_TRG: "_efs_entity_trg",
    EFS_ENTITY_XREF_TRG: "_efs_entity_xref_trg",
    EFS_DATA_SOURCE_TRG: "_efs_data_source_trg",
    EFS_FEATURE_GROUP_TRG: "_efs_feature_group_trg"
}

# SQL Query constants for get_df method
EFS_QUERY_FEATURE_TEMPLATE = """
    SELECT 
        f.id,
        f.name,
        f.data_domain,
        f.column_name,
        f.description,
        f.tags,
        f.data_type,
        f.feature_type,
        f.status,
        f.creation_time,
        f.modified_time,{4}
        g.group_name
    FROM 
        "{0}"."{1}" f
    LEFT JOIN 
        "{0}"."{2}" g
    ON 
        f.name = g.feature_name 
        AND f.data_domain = g.feature_data_domain
    WHERE 
        f.data_domain = '{3}'
"""

EFS_QUERY_ENTITY_TEMPLATE = """
    SELECT 
        e.name,
        e.data_domain,
        e.description,
        e.creation_time,
        e.modified_time,{4}
        x.entity_column
    FROM 
        "{0}"."{1}" e
    INNER JOIN 
        "{0}"."{2}" x
    ON 
        e.name = x.entity_name 
        AND e.data_domain = x.data_domain
    WHERE 
        e.data_domain = '{3}'
"""

# Column fragments for conditional inclusion
EFS_ARCHIVED_TIME_COLUMN = """
        e.archived_time,"""

EFS_FEATURE_ARCHIVED_TIME_COLUMN = """
        f.archived_time,"""

EFS_QUERY_FEATURE_INFO = """
    SELECT 
        fm.*,
        f.name,
        f.column_name,
        f.description,
        f.tags,
        f.data_type,
        f.feature_type,
        f.status,
        f.creation_time,
        f.modified_time
    FROM 
        "{0}"."{1}" fm
    INNER JOIN 
        "{0}"."{2}" f
    ON 
        fm.feature_id = f.id 
        AND fm.data_domain = f.data_domain
    WHERE 
        fm.data_domain = '{3}'
"""

EFS_QUERY_FEATURE_CATALOG = """
    SELECT DISTINCT
        fv.entity_id,
        fm.data_domain,
        f.id,
        f.name,
        fm.table_name,
        fv.feature_version,
        fm.valid_end
    FROM 
        "{0}"."{1}" fm
    INNER JOIN 
        "{0}"."{2}" f
    ON 
        fm.feature_id = f.id 
        AND fm.data_domain = f.data_domain
    INNER JOIN 
        "{0}"."{3}" fv
    ON 
        fm.data_domain = fv.data_domain
        AND fm.entity_name = fv.entity_id
        AND fv.feature_name = f.name
    WHERE 
        fm.data_domain = '{4}'
"""

EFS_QUERY_ENTITY_INFO = """
    SELECT 
        e.name as entity_name,
        e.data_domain,
        x.entity_column,
        e.description
    FROM 
        "{0}"."{1}" e
    INNER JOIN 
        "{0}"."{2}" x
    ON 
        e.name = x.entity_name 
        AND e.data_domain = x.data_domain
    WHERE 
        e.data_domain = '{3}'
"""

class FeatureStatus(Enum):
    ACTIVE = 1
    INACTIVE = 2


class FeatureType(Enum):
    CONTINUOUS = 1
    CATEGORICAL = 2
    NUMERICAL = 3

class ProcessType(Enum):
    DENORMALIZED_VIEW = 'denormalized view'
    FEATURE_GROUP = 'feature group'
    NEW = 'new'
    EXISTING = 'existing'


class ProcessStatus(Enum):
    NOT_STARTED = 'not started'
    RUNNING = 'running'
    COMPLETED = 'completed'
    FAILED = 'failed'

from teradataml.dataframe.dataframe import DataFrame, in_schema

class _FeatureStoreDFContainer:
    """
    Utility class for FeatureStore DataFrame operations.
    
    This class provides static methods for creating and managing DataFrames
    used across different FeatureStore components, eliminating code duplication
    and providing a centralized, efficient approach to DataFrame handling.
    """
    __df_container = {}

    @staticmethod
    def _get_base_df(table_name, repo):
        """
        Internal helper method to create and cache base DataFrames.

        PARAMETERS:
            table_name:
                Required Argument.
                Specifies the logical table name from EFS_DB_COMPONENTS.
                Types: str

            repo:
                Required Argument.
                Specifies the repository name.
                Types: str

        RETURNS:
            teradataml DataFrame

        """
        key = f"{repo}.{table_name}"

        if key not in _FeatureStoreDFContainer.__df_container:
            _FeatureStoreDFContainer.__df_container[key] = DataFrame(
                in_schema(repo, EFS_DB_COMPONENTS[table_name])
            )
        return _FeatureStoreDFContainer.__df_container[key]

    @staticmethod
    def get_df(obj_type, repo, data_domain):
        """
        DESCRIPTION:
            Generic static method to create and manage DataFrames for different object types
            in FeatureStore. Handles joins and special object type processing.

        PARAMETERS:
            obj_type:
                Required Argument.
                Specifies the type of DataFrame to return.
                Supported types: 'feature', 'feature_staging', 'entity', 'entity_staging',
                'feature_wog', 'feature_info', 'feature_catalog', 'entity_info', and all
                other types defined in EFS_DB_COMPONENTS.
                Types: str

            repo:
                Required Argument.
                Specifies the repository name.
                Types: str

            data_domain:
                Required Argument.
                Specifies the data domain for filtering operations.
                Types: str

        RETURNS:
            teradataml DataFrame.

        RAISES:
            TeradataMlException

        EXAMPLES:
            >>> # Basic DataFrame retrieval
            >>> df = _FeatureStoreDFContainer.get_df(
            ...     obj_type='feature',
            ...     repo='my_repo',
            ...     data_domain='analytics'
            ... )
            
            >>> # Complex join for feature info
            >>> df = _FeatureStoreDFContainer.get_df(
            ...     obj_type='feature_info',
            ...     repo='my_repo',
            ...     data_domain='analytics'
            ... )
        """
        repo_obj = f"{repo}.{data_domain}.{obj_type}"

        if repo_obj not in _FeatureStoreDFContainer.__df_container:
            try:
                if obj_type in ["feature", "feature_staging"]:
                    # Based on object type, determine group table and archived_time column
                    if obj_type == "feature":
                        group_table = "group_features"
                        archived_time_col = ""
                    else:
                        group_table = "group_features_staging"
                        archived_time_col = EFS_FEATURE_ARCHIVED_TIME_COLUMN

                    # Join features with group features based on data domain
                    sql_query = EFS_QUERY_FEATURE_TEMPLATE.format(
                        repo, 
                        EFS_DB_COMPONENTS[obj_type], 
                        EFS_DB_COMPONENTS[group_table], 
                        data_domain,
                        archived_time_col
                    )
                    _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame.from_query(sql_query)

                elif obj_type in ["entity", "entity_staging"]:
                    # Based on object type, determine if archived_time column should be included
                    archived_time_col = EFS_ARCHIVED_TIME_COLUMN if obj_type == "entity_staging" else ""
                    
                    # Join entity with entity_xref based on data domain
                    sql_query = EFS_QUERY_ENTITY_TEMPLATE.format(
                        repo,
                        EFS_DB_COMPONENTS[obj_type],
                        EFS_DB_COMPONENTS[f'{obj_type}_xref'],
                        data_domain,
                        archived_time_col
                    )
                    _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame.from_query(sql_query)

                elif obj_type == "feature_wog":
                    # Feature without group
                    _FeatureStoreDFContainer.__df_container[repo_obj] = _FeatureStoreDFContainer._get_base_df("feature", repo)

                elif obj_type == "feature_info":
                    # Join feature metadata with feature based on data domain
                    sql_query = EFS_QUERY_FEATURE_INFO.format(
                        repo,
                        EFS_DB_COMPONENTS['feature_metadata'],
                        EFS_DB_COMPONENTS['feature'],
                        data_domain
                    )
                    _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame.from_query(sql_query)

                elif obj_type == "feature_catalog":
                    # Join feature metadata, feature, and feature version based on data domain
                    sql_query = EFS_QUERY_FEATURE_CATALOG.format(
                        repo,
                        EFS_DB_COMPONENTS['feature_metadata'],
                        EFS_DB_COMPONENTS['feature'],
                        EFS_DB_COMPONENTS['feature_version'],
                        data_domain
                    )
                    _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame.from_query(sql_query)

                elif obj_type == "entity_info":
                    # Single SQL query instead of DataFrame joins
                    sql_query = EFS_QUERY_ENTITY_INFO.format(
                        repo,
                        EFS_DB_COMPONENTS['entity'],
                        EFS_DB_COMPONENTS['entity_xref'],
                        data_domain
                    )
                    _FeatureStoreDFContainer.__df_container[repo_obj] = DataFrame.from_query(sql_query)

                elif obj_type == "data_domain":
                    _FeatureStoreDFContainer.__df_container[repo_obj] = _FeatureStoreDFContainer._get_base_df("data_domain", repo)

                else:
                    # Default: simple table load + domain filter
                    df = _FeatureStoreDFContainer._get_base_df(obj_type, repo)
                    if "data_domain" in df.columns:
                        df = df[df.data_domain == data_domain]
                    _FeatureStoreDFContainer.__df_container[repo_obj] = df
            except Exception as e:
                if "encountered problem with the query." in str(e).lower():
                    # If it's a "Encountered problem with the query." error, try to get better error message using in_schema
                    try:
                        # Test if database exists with a simple query
                        test_df = DataFrame(in_schema(repo, EFS_DB_COMPONENTS[obj_type]))
                    except Exception as schema_e:
                        # Re-raise the schema error which gives better error message
                        raise schema_e
                # If not a database or table issue, raise original error
                raise e

        return _FeatureStoreDFContainer.__df_container[repo_obj]