import pandas as pd
from collections import defaultdict
from typing import Any
from .types import EMPTY
from .utils import flatten_json, object_of_lists, reshape


def partial_melt(data: pd.DataFrame | Any, *,
                 sort: bool=True,
                 drop_na: bool=True,
                 drop_duplicates: bool=True,
                 raise_on_empty: bool=True):
    """
    What is a partial melt?
    
    Before answering that, what is "melt"? In pandas, melting a table is the
    opposite operation to pivoting. Melting reshapes a wide-format table into
    a long-form table. These are used above because arbitrary JSON can be
    readily converted into a long-format table, then pivoted into a wide-format
    table.
    
    This wide table has column levels that correspond to list indices. While this
    ensures that one row maps to one JSON document, this is generally not
    desired. In general, we want the lists to be extended along the rows --
    that each list element is indexed to a row with all values that correspond
    to that list element.
    
    This mix, where one JSON document extends to multiple rows based on
    potentially nested lists, is what we're calling a *partial melt*.

    Parameters
    ----------
    df : pandas.DataFrame | JSON-structured data
        The data to be partially melted. If a DataFrame, it should be
        wide-format.

    sort : bool
        Sort the resulting dataframe columns and row indices. Default: True.

    drop_na : bool
        If True (default), drop rows that are all NaN/None.
    
    drop_duplicates : bool
        If True (default), drop duplicate rows.

    raise_on_empty : bool
        If present, and EMPTY sentinel indicates an unprocessed field. If True
        (default), raises an IndexError.

    Returns
    -------
    pandas.DataFrame
        The partially melted dataframe.
    """
    def try_int(k):
        try:
            return int(k)
        except ValueError:
            return k
        
    def as_container(k: Any):
        if hasattr(k, "__iter__") and not isinstance(k, str):
            return k
        else:
            return (k,)
        
    if isinstance(data, pd.DataFrame):
        # Encode source row-id into the key so forms don't collide.
        flattened = {}
        for ridx, (_, row) in enumerate(data.iterrows()):
            for key, value in row.items():
                if pd.isna(key):  # type: ignore
                    continue
                key_tuple = (ridx,) + tuple(try_int(k) for k in as_container(key))
                flattened[key_tuple] = value
        flattened = reshape(flattened)
    else:
        flattened = flatten_json(data, reshape=True)

    columns = {col for col, _ in map(object_of_lists, flattened)}
    indexes = {idx for _, idx in map(object_of_lists, flattened)}

    def _fetch_with_broadcast(col, row):
        """Exact match first; otherwise broadcast from nearest ancestor prefix."""
        cur = row
        while True:
            key = (col, cur)
            if key in flattened:
                return flattened[key]
            if not cur:  # ()
                return EMPTY()
            cur = cur[:-1]  # drop the deepest index and try again

    # pandas dict representation of the data.
    result = {col: {row: _fetch_with_broadcast(col, row) for row in indexes}
              for col in columns}
    output = pd.DataFrame(result)

    if raise_on_empty and (output == EMPTY()).values.any():
        raise IndexError("Failed to generate a DataFrame representation of the data.")

    # Apply convenience functions
    if sort:
        output = output\
            .sort_index(axis=0)\
            .sort_index(axis=1)
    if drop_na:
        output.dropna(how='all', ignore_index=True, inplace=True)
    if drop_duplicates:
        output.drop_duplicates(ignore_index=True, inplace=True)
    return output
