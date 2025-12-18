from __future__ import annotations

import importlib
from typing import Any, Optional

CHALK_IMPORT_MESSAGE = (
    'chalkpy is required for this functionality. Install the optional dependency with `pip install "chalkdf[chalkpy]"`.'
)


def require_chalk_module(module: str):
    """
    Import a chalk module, raising a helpful error if the dependency is missing.
    """

    try:
        return importlib.import_module(module)
    except ImportError as exc:  # pragma: no cover - dependent on optional dependency
        raise ImportError(CHALK_IMPORT_MESSAGE) from exc


def require_chalk_attrs(module: str, *names: str) -> Any:
    """
    Import specific attributes from a chalk module with a friendly error message.
    """

    mod = require_chalk_module(module)
    try:
        attrs = tuple(getattr(mod, name) for name in names)
    except AttributeError as exc:  # pragma: no cover - dependent on optional dependency
        requested = ", ".join(names)
        raise ImportError(f"Failed to import {requested} from {module}. {CHALK_IMPORT_MESSAGE}") from exc
    return attrs[0] if len(attrs) == 1 else attrs


_EXPR_PB: Optional[Any] = None
_UNDERSCORE_CLS: Optional[Any] = None
_UNDERSCORE_ATTR: Optional[Any] = None
_UNDERSCORE_ROOT: Optional[Any] = None
_BASE_SQL_SOURCE_CLS: Optional[Any] = None
_PRIMITIVE_FEATURE_CONVERTER: Optional[Any] = None
_GRPC_CLIENT_CLS: Optional[type] = None


def _get_expr_pb():
    global _EXPR_PB
    if _EXPR_PB is None:
        _EXPR_PB = require_chalk_module("chalk._gen.chalk.expression.v1.expression_pb2")
    return _EXPR_PB


def _get_underscore_cls():
    global _UNDERSCORE_CLS
    if _UNDERSCORE_CLS is None:
        _UNDERSCORE_CLS = require_chalk_attrs("chalk.features", "Underscore")
    return _UNDERSCORE_CLS


def _get_underscore_attr_and_root():
    global _UNDERSCORE_ATTR
    global _UNDERSCORE_ROOT
    if _UNDERSCORE_ATTR is None:
        _UNDERSCORE_ATTR = require_chalk_attrs("chalk.features.underscore", "UnderscoreAttr")
    if _UNDERSCORE_ROOT is None:
        _UNDERSCORE_ROOT = require_chalk_attrs("chalk.features.underscore", "UnderscoreRoot")
    return _UNDERSCORE_ATTR, _UNDERSCORE_ROOT


def _get_base_sql_source_cls():
    global _BASE_SQL_SOURCE_CLS
    if _BASE_SQL_SOURCE_CLS is None:
        _BASE_SQL_SOURCE_CLS = require_chalk_attrs("chalk.sql._internal.sql_source", "BaseSQLSource")
    return _BASE_SQL_SOURCE_CLS


def _get_primitive_feature_converter():
    global _PRIMITIVE_FEATURE_CONVERTER
    if _PRIMITIVE_FEATURE_CONVERTER is None:
        _PRIMITIVE_FEATURE_CONVERTER = require_chalk_attrs(
            "chalk.features._encoding.converter", "PrimitiveFeatureConverter"
        )
    return _PRIMITIVE_FEATURE_CONVERTER
