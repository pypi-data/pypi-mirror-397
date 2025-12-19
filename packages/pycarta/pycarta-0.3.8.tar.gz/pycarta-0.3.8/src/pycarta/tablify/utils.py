"""
utils.py

Helper utilities for schema parsing, column ordering, and schema resolution.
This module provides:
  - `SchemaParser` for extracting PKs, FKs, and property order from JSON Schemas.
  - Column reordering logic to produce consistent, schema-driven DataFrames.
  - Schema resolution to match forms with their best-fit schema files.

These utilities are used internally by the combine/melt modules to unify
flattened JSON form data into structured tables.
"""
import pandas as pd
import pathlib
from typing import List, Dict, Any, Union, Optional, Generator

MAX_ORDER = 2**31 - 1

# region sorting
def reorder_columns(df, preferred_order: List[str]) -> pd.DataFrame:
    """
    Reorder DataFrame columns to place `preferred_order` columns first.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame to reorder.
    preferred_order : list of str
        List of column names to prioritize.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns reordered such that all preferred columns
        (if present) appear first, followed by the remaining columns.
    """
    preferred = [col for col in preferred_order if col in df.columns]
    others = [col for col in df.columns if col not in preferred]
    return df[preferred + others]

class SchemaParser:
    """
    Parse a JSON Schema to extract primary key, foreign keys, and field order.

    Supports both lazy and eager initialization:
        - Eager: SchemaParser(schema_dict)
        - Lazy: SchemaParser().parse(schema_dict)

    Attributes
    ----------
    schema : dict | None
        The JSON Schema being parsed.
    pk : tuple[str, ...] | None
        The primary key path (tuple of property names) if found.
    fks : list[tuple[str, ...]]
        List of foreign key paths.
    property_order : list[tuple[str, ...]]
        Ordered list of property keys according to `propertyOrder` values.
    """

    def __init__(self, schema: Optional[Dict[str, Any]] = None):
        self.schema: Optional[Dict[str, Any]] = None
        self.pk: Optional[tuple[str, ...]] = None
        self.fks: list[tuple[str, ...]] = []
        self.property_order: list[tuple[str, ...]] = []

        if schema is not None:
            self.parse(schema)

    def parse(self, schema: Dict[str, Any]) -> "SchemaParser":
        """
        Parse the schema recursively to populate pk, fks, and property_order.

        Parameters
        ----------
        schema : dict
            A JSON Schema dictionary.

        Returns
        -------
        SchemaParser
            Returns self for chaining.
        """
        self.schema = schema
        self.pk = None
        self.fks = []
        self.property_order = []

        properties = schema.get("properties", {})

        def _parse_properties(props: Dict[str, Any], base_order=0, path_prefix=()):
            for field_name, field_attrs in props.items():
                full_key = path_prefix + (field_name,)

                if field_attrs.get("&pk"):
                    if self.pk:
                        raise ValueError(f"Multiple PKs found: {self.pk} and {full_key}")
                    self.pk = full_key

                if field_attrs.get("&fk"):
                    self.fks.append(full_key)

                po = field_attrs.get("propertyOrder", MAX_ORDER)
                total_order = base_order + po * 0.01

                if field_attrs.get("type") == "object" and "properties" in field_attrs:
                    self.property_order.append(((base_order, total_order), full_key))
                    _parse_properties(field_attrs["properties"], total_order, full_key)
                else:
                    self.property_order.append(((base_order, total_order), full_key))

        for section_name, section in properties.items():
            section_po = section.get("propertyOrder", MAX_ORDER)
            if section.get("type") == "object" and "properties" in section:
                _parse_properties(section["properties"], base_order=section_po, path_prefix=(section_name,))
            else:
                _parse_properties({section_name: section}, base_order=section_po)

        self.property_order.sort(key=lambda x: (x[0][0], x[0][1]))
        self.property_order = [key for _, key in self.property_order]
        return self
    
       
def match_suffix(col: Union[str, tuple], target: Union[str, tuple]) -> bool:
    """ Check if `col` ends with `target`: works for varying tuple lengths. """
    if not isinstance(col, tuple):
        col = (col,)
    if not isinstance(target, tuple):
        target = (target,)
    if len(target) > len(col):
        return False
    return col[-len(target):] == target

def get_sorted_columns(columns, schema_parsers):
    """
    Determine a unified column order across multiple schemas.
    Order:
      1. All primary keys (PKs)
      2. All foreign keys (FKs)
      3. Columns in propertyOrder per schema
      4. Remaining columns
    """
    pk_list, fk_list, property_order = [], [], []

    for parser in schema_parsers:
        if parser.pk and parser.pk not in pk_list:
            pk_list.append(parser.pk)

        for fk in parser.fks:
            if fk not in fk_list:
                fk_list.append(fk)

        for key in parser.property_order:
            if key not in property_order and key not in pk_list and key not in fk_list:
                property_order.append(key)

    final_order = []

    def match(col, key):
        # Remove NaNs. Interestingly, there would be 4 rows of nans between forms of different schema.
        # Columns are stored as tuples of strings that represent a hierarchical path
        # (e.g., ('stepParameters', 'power') for nested JSON). However, when we
        # concatenate data from forms with different schemas, some columns exist
        # in one schema but not the other. Pandas aligns columns by name during concat,
        # so if a column doesn't exist in a form, its value becomes NaN.
        #
        # When pandas builds the final MultiIndex column set, it still includes these
        # columns where their tuple label may contain np.nan values (e.g., (nan, nan)). 
        # These appear as completely blank rows between blocks of forms with different schemas.
        #
        # Here, we remove NaNs from the column tuples to make suffix matching more robust
        # and avoid misalignments caused by these unexpected blank columns.
        col = tuple(c for c in col if pd.notna(c))
        return col[-len(key):] == key if len(col) >= len(key) else False

    # Add PKs
    for pk in pk_list:
        matches = [c for c in columns if match(c, pk)]
        final_order.extend(matches)

    # Add FKs
    for fk in fk_list:
        matches = [c for c in columns if match(c, fk) and c not in final_order]
        final_order.extend(matches)

    # Add propertyOrder
    for key in property_order:
        matches = [c for c in columns if match(c, key) and c not in final_order]
        final_order.extend(matches)

    # Add remaining
    remaining = [c for c in columns if c not in final_order]
    final_order.extend(remaining)
    return final_order

def sort_dataframe(df: pd.DataFrame, schema: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Sort the columns of a DataFrame based on schema information.
    """
    if schema:
        parser = SchemaParser().parse(schema)
        sorted_cols = get_sorted_columns(df.columns, [parser])
        return df.reindex(columns=sorted_cols)
    return df
# end region

# region schema resolution
def find_best_schema(form: pathlib.Path, schema_paths: List[pathlib.Path]) -> Optional[pathlib.Path]:
    """
    Identify the most likely schema file for a given form based on token overlap. This is(?) useful in
    cases where (like the BIRDSHOT data) forms are saved as names in (for example) Google Drive as their 
    form-type (e.g. a tensile.json) maps to a schema of the same name (tensile.json). which could occur
    if users are using the cli directly, outside of forms in FormsDB. 

    Matching is performed by:
      1. Splitting the form's stem (filename without extension) into lowercase tokens,
         replacing underscores with hyphens.
      2. Splitting each schema filename the same way.
      3. Counting the number of shared tokens between the form and schema filenames.
    """
    form_tokens = set(form.stem.replace("_", "-").lower().split("-"))
    best_match = None
    best_score = 0

    for schema in schema_paths:
        schema_tokens = set(schema.stem.replace("_", "-").split("-"))
        score = len(form_tokens & schema_tokens)

        if score > best_score:
            best_match = schema
            best_score = score

    return best_match if best_score > 0 else None

def resolve_schemas(
    form_paths: List[Union[str, pathlib.Path]],
    schema_input: Optional[Any] = None,
) -> Dict[pathlib.Path, Optional[dict]]:
    """
    Resolve a schema for each form path.

    Accepted `schema_input` patterns:
      1) None
         → all forms map to None.

      2) Single schema (any of):
         - Path-like to a JSON file,
         - JSON string/bytes,
         - file-like stream with .read(),
         - already-loaded dict
         → the same parsed schema dict is applied to every form.

      3) Single directory (path-like to directory)
         → for each form, pick the best matching *.json file in that directory
           by filename token overlap (see `find_best_schema`), load it, or None.

      4) List aligned 1:1 with `form_paths`
         Each item may be:
           - None,
           - path-like to a JSON file,
           - JSON string/bytes,
           - file-like stream,
           - dict,
           - (optionally) a directory path (best-match within that directory for that single form)
         → each item is normalized with `load_json` to a dict (or None).

    Returns
    -------
    Dict[pathlib.Path, Optional[dict]]
        A mapping from each form path to its resolved schema object (dict) or None.

    Notes
    -----
    - Loaded schemas must be JSON objects (dict). Non-dict JSON (e.g., list/str) will raise TypeError.
    - This function performs I/O only for reading schemas; it does not read forms themselves.
    """
    from .io import load_json

    def _to_path(p: Union[str, pathlib.Path]) -> pathlib.Path:
        return p if isinstance(p, pathlib.Path) else pathlib.Path(p)

    def _load_schema_like(obj: Any) -> dict:
        """Normalize any supported schema representation into a dict."""
        loaded = load_json(obj)
        if not isinstance(loaded, dict):
            raise TypeError(
                "Schema must deserialize to a JSON object (dict); "
                f"got {type(loaded).__name__}."
            )
        return loaded

    forms: List[pathlib.Path] = [_to_path(f) for f in form_paths]
    resolved: Dict[pathlib.Path, Optional[dict]] = {}

    # Case 1: No schema provided
    if schema_input is None:
        return {f: None for f in forms}

    # Case 2/3: Single input that might be a file, JSON text/bytes/dict, or a directory
    if not hasattr(schema_input, "__iter__") or isinstance(schema_input, (str, bytes, bytearray, pathlib.Path)):
        # Treat as single item (not an aligned list)
        if isinstance(schema_input, (str, pathlib.Path)):
            p = _to_path(schema_input)
            if p.exists() and p.is_dir():
                # Directory of schemas → best match per form
                candidates = list(p.glob("*.json"))
                for f in forms:
                    best = find_best_schema(f, candidates)
                    resolved[f] = _load_schema_like(best) if best else None
                return resolved
        # Single shared schema (file path, JSON string/bytes, file-like, or dict)
        shared = _load_schema_like(schema_input)
        return {f: shared for f in forms}

    # Case 4: List aligned 1:1 with forms
    items = list(schema_input)
    if len(items) != len(forms):
        raise ValueError("When `schema_input` is a list, it must be the same length as `form_paths`.")

    for form, item in zip(forms, items):
        if item is None:
            resolved[form] = None
            continue

        # Allow a directory per-item (optional quality-of-life)
        if isinstance(item, (str, pathlib.Path)):
            p = _to_path(item)
            if p.exists() and p.is_dir():
                candidates = list(p.glob("*.json"))
                best = find_best_schema(form, candidates)
                resolved[form] = _load_schema_like(best) if best else None
                continue

        # Otherwise, treat as schema-like and normalize
        resolved[form] = _load_schema_like(item)

    return resolved

# TODO: Refactor this logic to reduce duplication across schema resolution modes. Such as the below:
# def resolve_schemas(*form_paths: Union[str, Path], schema_input: None | str | Path | list[None | str | Path]) -> ...:
#     ...
#     def map_forms_to_schema() -> dict[str, Any]:
#         // Missing and remote schemas
#         if schema_input is None:
#             // No schema
#             // TODO: Check for schema information in form metadata
#             return {f: None for f in form_paths}

#         // Local schemas
#         if isinstance(schema_input, (str, Path)):
#             path = Path(schema_input)
#             if path.is_file():
#                 //  Single shared schema
#                 schema_input_ = cycle([path])
#             elif path.is_dir():
#                 // Directory of schemas
#                 candidates = list(schema_dir.glob("*.json"))
#                 schema_input_ = [find_best_schema(form, candidates) for form in form_paths]
#         elif hasattr(schema_input, "__iter__") and len(schema_input) == len(form_paths)):
#             // List (iterable) of schemas
#             schema_input_ = schema_input
#         else:
#             // Cannot map schema_input to forms
#             raise ValueError("Cannot map schema to form paths.")

#         resolved = {form: json.load(open(schema, "rb")) for form, schema in zip(form_paths, schema_input_)}
    
#     return map_forms_to_schema()

# TODO: how to resolve schema when fetching forms from FormsDB (there is metadata with each form that contains a form-type and version field)
# end region

# region JSON Manip
def walk(obj) -> Generator:
    """Converts a possibly nested dict into a list of tuples."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter((k,) + p for p in walk(v))
    elif isinstance(obj, (list, tuple)):
        for i, x in enumerate(obj):
            yield from iter((i,) + p for p in walk(x))
    else:
        yield (obj,)


def object_of_lists(key: tuple) -> tuple:
    """
    Reshape the path of a nested JSON object into objects of lists.

    The path through a nested JSON object can be represented as a tuple of
    keys/indexes, e.g. ("foo", 0, "bar", 1) in:

        {
            "foo": [
                {
                    "bar": ['a', 'b', 'c']
                }
            ]
        }
    
    would return 'b'.

    As an object of lists, this key is reordered to ("foo", "bar", 0, 1),
    corresponding to JSON object,:

        {
            "foo": {
                "bar": [['a', 'b', 'c']]
            }
        }
    
    This restructuring maintains data alignment, but partitions that alignment
    into a category (str) part and an index (array-like) part.
    """
    # foo: [bar: 1, bar:2, bar: 3] --> (foo, 0, bar, 1), (foo, 1, bar, 2), (foo, 2, bar, 3)
    # foo: bar: [1, 2, 3] --> (foo, bar, 0, 1), (foo, bar, 1, 2), (foo, bar, 2, 3)
    # 
    # foo: [bar: [baz: 1, baz: 2], bar: [baz: 3, baz: 4]] --> (foo, 0, bar, 0, baz | 1), ...
    # (foo, 0, bar, 0, baz) --> (foo, bar, baz, 0, 0) --> foo: bar: baz: [[1]]

    # Accept keys already shaped as ((obj...), (num...))
    if (
        isinstance(key, tuple)
        and len(key) == 2
        and all(isinstance(k, tuple) for k in key)
    ):
        obj, num = key
        if not all(isinstance(k, str) for k in obj) or not all(isinstance(k, int) for k in num):
            raise ValueError(f"{key} is not a valid (obj, num) index.")
        return (obj, num)

    obj = tuple(k for k in key if isinstance(k, str))
    num = tuple(k for k in key if isinstance(k, int))
    if set(key) != set(obj + num):
        raise ValueError(f"{set(key) - set(obj + num)} is not a valid index.")
    return (obj, num)

    # obj = tuple(k for k in key if isinstance(k, str))
    # num = tuple(k for k in key if isinstance(k, int))
    # if set(key) != set(obj + num):
    #     raise ValueError(f"{set(key) - set(obj + num)} is not a valid index.")
    # return (obj, num)


def reshape(data: dict[tuple, Any]) -> dict[tuple, Any]:
    """
    Reshape flattened JSON data, dict[tuple, Any], so dict keys (str keys) 
    are ordered before list indexes (int indexes).

    Parameters
    ----------
    data : dict[tuple, Any]
        Flattened dictionary with mixed (dict/list) container structure.

    Returns
    -------
    dict[tuple, Any]
        Flattened diction with ordered (dict then list) container structure.
    """
    return {object_of_lists(k): v for k, v in data.items()}


_reshape = reshape  # alias the reshape function so bool parameter does not mask function.

def flatten_json(data, *, reshape: bool=True):
    """
    Flatten an JSON document into a flattened map

    Converts a potentially nested JSON object into a tuple-keyed dict, e.g.:

        {
            "foo": [
                {
                    "bar": ['a', 'b', 'c']
                }
            ]
        }
    
    becomes:

        {
            ("foo", 0, "bar", 0): 'a',
            ("foo", 0, "bar", 1): 'a',
            ("foo", 0, "bar", 2): 'a'
        }
    
    Parameters
    ----------
    data : JSON-formatted content
        Data that is to be flattened
    
    reshape : bool
        Whether to reshape the content into maps (str keys) followed by
        lists (int indexes). Default: True.
    """
    result = {tuple(key): value for *key, value in walk(data)}
    if reshape:
        return _reshape(result)
    else:
        return result
# end region
