import pandas as pd
from pathlib import Path
from typing import Any, Union
from .core import Json
from .utils import SchemaParser, get_sorted_columns

PathLike = Union[str, Path]

def tablify(
        forms: list[Any], 
        schemas: list[Any | None] | None=None,
        *,
        melt: bool = True
    ) -> pd.DataFrame:
    """
    Combine an aligned list of already-loaded forms (JSON-like dicts) and optional aligned 
    schema(s) into a single dataframe.

    Parameters
    ----------
    forms : list[dict-like]
        Already-loaded JSON documents (one per form).
    schemas : list[Any | None] | None
        - None: no schema-based sorting.
        - list: one-to-one mapping with `forms` (same length), each item a dict or None.
    melt : bool, default=True
        If True, perform a partial melt to expand nested list structures into rows.

    Returns
    -------
    pd.DataFrame
        Combined, optionally partially-melted table with columns sorted
        according to schema-derived ordering (if provided).
    """
    from .melt import partial_melt

    # Check inputs
    if not isinstance(forms, list) or len(forms) == 0:
        raise ValueError("`forms` must be a non-empty list of JSON-like objects.")

    if schemas is not None:
        if not isinstance(schemas, list):
            raise TypeError(
                "`schemas` must be a list aligned to `forms` (or None). "
                "Passing a single schema object is not supported here."
            )
        if len(schemas) != len(forms):
            raise ValueError("`schemas` length must match `forms` length.")
        
    # Normalize schemas to an aligned list of Nones when not provided
    schemas: list[Any | None] = schemas if schemas is not None else [None] * len(forms)

    tables: list[pd.DataFrame] = []
    schema_parsers: list[SchemaParser] = []

    # Flatten each form and parse its matching schema
    for i, (form, schema) in enumerate(zip(forms, schemas)):
        df = Json(form).to_dataframe(index=i)
        tables.append(df)

        if schema:
            schema_parsers.append(SchemaParser().parse(schema))
    
    # Concatenate forms
    combined_df = pd.concat(tables, ignore_index=True, sort=False)

    # Optionally partial melt
    if melt:
        combined_df = partial_melt(combined_df)

    # Drop entirely-empty rows
    combined_df = combined_df[combined_df.notna().any(axis=1)]

    # Optional schema-driven column ordering
    if schema_parsers:
            final_order = get_sorted_columns(combined_df.columns, schema_parsers)
            combined_df = combined_df.reindex(columns=final_order)

    return combined_df
