# Copyright (C) 2024 Floating Rock Studio Ltd
from ...exceptions import DataValidationException
from ... import constants


def validate(data, schema, special_types=None, name="unknown"):
    special_types = special_types or schema.get(constants.KEYS.TYPE_REFS, {})
    for k, v in data.items():
        if k in constants.RESERVED_KEYS:
            continue
        if k not in schema:
            raise DataValidationException(f"'{k}' not in schema keys for {name}")

        info = schema[k]
        _validate_type(k, v, info, special_types)

        if info.get(constants.KEYS.EACH_ITEM):
            if isinstance(v, dict):
                validate(v, info[constants.KEYS.EACH_ITEM], special_types, f"{name}/{k}")
            else:
                for each in v:
                    _validate_type(k, each, info[constants.KEYS.EACH_ITEM], special_types)
        # ignore cascade, unique here


def _validate_type(key, data, schema, special_types):
    data_type = type(data).__name__  # json formats in int, float, str, dict, list, bool
    data_type = constants.TYPE_MAP.get(data_type, data_type)
    info_type = schema[constants.KEYS.TYPE]
    if info_type in special_types:
        meta_info = special_types[info_type]
        info_type = meta_info[constants.KEYS.VALUE][constants.KEYS.TYPE]
        if data_type == constants.TYPES.OBJECT:
            # Check each component
            for k, v in data.items():
                if k not in meta_info:
                    raise DataValidationException(f"'{key}' has unexpected subkey '{k}'")

                expected_type = meta_info[k][constants.KEYS.TYPE]
                v_type = type(v).__name__
                v_type = constants.TYPE_MAP.get(v_type, v_type)
                if v_type != meta_info[k][constants.KEYS.TYPE]:
                    raise DataValidationException(f"'{key}'.{k} expected type '{expected_type}', got '{v_type}'")

                # TODO: this should be recursive
                return
        else:
            # Check against constants.KEYS.VALUE
            pass

    # TODO: nested/complex types
    if info_type != data_type:
        raise DataValidationException(f"'{key}' expected type '{info_type}', got '{data_type}'")
