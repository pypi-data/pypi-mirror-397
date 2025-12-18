# Copyright (C) 2024 Floating Rock Studio Ltd
import re as _re
from pathlib import Path
from types import SimpleNamespace as _SimpleNamespace

# Reserved keys in fr_config files that have special meaning and cannot be used as regular config keys
RESERVED_KEYS = (
    "$defs",  # Schema definitions
    "$ref",  # Reference a $defs
    "$parent",  # Change the parent directory used (redirect)
    "__info__",  # Metadata about the schema
    "__types__",  # Custom reusable types
)

# Default variant name used when no specific variant is requested in fr_config
DEFAULT_VARIANT: str = "default"

# File extension for fr_config configuration files
FR_CONFIG_EXT: str = ".fr_config"

# Directory name that contains fr_config files within project structures
FR_CONFIG_DIR: str = ".fr_config"

# File extension for fr_config schema definition files
FR_SCHEMA_EXT: str = ".fr_schema"

# Path to the json-schema that validates fr_config schema files
CORE_SCHEMA_PATH = Path(__file__).parent / "../schema/fr_config.json"

# Environment variable name that defines paths to search for schema files
SCHEMA_PATH_VAR: str = "FR_CONFIG_SCHEMA_PATH"

# Environment variable name that defines root paths for config resolution
ROOT_PATH_VAR: str = "FR_CONFIG_ROOT_PATHS"

# Token used in fr_config values that gets replaced with the platform-specific path separator
PATHSEP_TOKEN: str = "%pathsep%"

# Tags used for versioning and state management of fr_config files
TAGS = _SimpleNamespace()
TAGS.LATEST = "latest"  # Marks the most recent version of a config
TAGS.PUBLISHED = "published"  # Marks a stable, approved version for production use
TAGS.DEPRECATED = "deprecated"  # Marks an outdated version that should not be used
TAGS.LOCKED = "locked"  # Marks a version that cannot be modified (used during operations)
TAGS.BROKEN = "broken"  # Marks a version with known issues or validation failures
TAGS.WIP = "wip"  # Marks a work-in-progress version not ready for use

# Default tags to search for when loading configs (in order of preference)
TAGS.DEFAULT = (TAGS.PUBLISHED, TAGS.LATEST)

# Tags that indicate configs should be hidden from normal operations
TAGS.HIDE = (TAGS.DEPRECATED, TAGS.LOCKED, TAGS.BROKEN)

# Tags that should be unique - only one config can have these tags at a time
TAGS.UNIQUE = (TAGS.LATEST, TAGS.PUBLISHED)

# Schema and config file structure keys used in fr_config
KEYS = _SimpleNamespace()
KEYS.METADATA = "__info__"  # Key for storing metadata about the config file
KEYS.TYPE_REFS = "__types__"  # Key for storing custom type definitions in schemas
KEYS.DEFAULT = "default"  # Key for specifying default values in schemas
KEYS.TYPE = "type"  # Key for specifying the data type of a schema field
KEYS.ARRAY_LENGTH = "length"  # Key for specifying fixed length of arrays in schemas
KEYS.CASCADE_MODE = "cascade"  # Key for specifying how values are merged when cascading configs
KEYS.ITEMS = "items"  # Key for specifying the schema of array/object items
KEYS.EACH_ITEM = "each"  # Key for validation of individual items in collections
KEYS.UNIQUE = "unique"  # Key for enforcing uniqueness constraints in arrays
KEYS.SEPARATOR = "separator"  # Key for specifying string separators in concatenated values
KEYS.COMPARE = "compare"  # Key for specifying comparison patterns for uniqueness checks
KEYS.VALUE = "value"  # Key for the actual data value in structured config entries

# Keys that are protected and have special meaning in fr_config processing
KEYS.PROTECTED = (
    KEYS.METADATA,
    KEYS.TYPE_REFS,
    KEYS.TYPE,
    KEYS.ARRAY_LENGTH,
    KEYS.CASCADE_MODE,
    KEYS.DEFAULT,
    KEYS.ITEMS,
    KEYS.UNIQUE,
    KEYS.SEPARATOR,
    KEYS.COMPARE,
)

# Data types supported in fr_config schemas and validation
TYPES = _SimpleNamespace()
TYPES.ARRAY = "array"  # List/array type for collections of values
TYPES.OBJECT = "object"  # Dictionary type for structured data
TYPES.INT = "int"
TYPES.FLOAT = "float"
TYPES.STRING = "string"
TYPES.BOOL = "bool"

# Mapping from Python built-in types to fr_config schema types
TYPE_MAP = {
    "dict": TYPES.OBJECT,
    "int": TYPES.INT,
    "float": TYPES.FLOAT,
    "str": TYPES.STRING,
    "bytes": TYPES.STRING,
    "bool": TYPES.BOOL,
    "list": TYPES.ARRAY,
    "set": TYPES.ARRAY,
    "tuple": TYPES.ARRAY,
}

# Cascade modes for controlling how configuration values are merged across hierarchy
CASCADE = _SimpleNamespace()
CASCADE.REPLACE = "replace"  # Replace the entire value with the new one
CASCADE.UPDATE = "update"  # Merge objects by updating keys, or replace primitives
CASCADE.APPEND = "append"  # Add new values to the end of arrays/strings
CASCADE.PREPEND = "prepend"  # Add new values to the beginning of arrays/strings

_VERSION = r"(?P<prefix>[vV])?(?P<number>[0-9]+)"  # Matches version patterns like "v1", "V2", "1", etc.

# Regex for parsing version tag files like ".v1.published"
TAG_REGEX = _re.compile(rf"^\.(?P<version>{_VERSION})\.(?P<tag>[-_\.a-zA-Z0-9]+)$")

# Regex for parsing version directories/files like "v1", "v1.ext"
VERSION_REGEX = _re.compile(rf"^{_VERSION}(?P<ext>\..+)?$")

# Regex for parsing full file names with version info like "config_v1.fr_config"
FILE_VERSION_REGEX = _re.compile(rf"^(?:(?P<name>.*)(?P<separator>[-_\.]))?(?P<version>{_VERSION})(?P<ext>\..+)?$")
