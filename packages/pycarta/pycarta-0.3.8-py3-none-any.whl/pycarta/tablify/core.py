import numpy as np
import pandas as pd
from collections.abc import Mapping
from typing import Any, Iterator, Union

class Json(Mapping):
    """
    Json handles conversion between a (possibly nested) JSON object
    and a wide-format pandas DataFrame.

    Methods
    -------
    Json(data).to_dataframe() : Creates a wide-format DataFrame from JSON.
    Json(data).to_json() : Returns a JSON-formatted object.
    Json.from_dataframe(df) : Returns a new Json from a DataFrame.
    """

    class JsonView(Mapping):
        """
        Provides a view into a partially-unwound JSON content,
        allowing traversal by key or key prefix.
        """
        def __init__(self, content: dict[tuple[Union[str, int]], Any]):
            self._content = content

        def __getitem__(self, key: Union[str, int, tuple]) -> Any:
            # Direct match
            try:
                return self._content[key]
            except KeyError:
                # Look for keys with this as prefix
                match = {
                    k[1:]: v for k, v in self._content.items() if k and k[0] == key
                }
                if not match:
                    raise KeyError(f"Key not found: {key}")
                if len(match) == 1:
                    return next(iter(match.values()))
                return Json.JsonView(match)

        def __iter__(self) -> Iterator:
            return iter(self._content)

        def __len__(self) -> int:
            return len(self._content)

    def __init__(self, obj: Any):
        """
        Create a Json object from any JSON-like Python structure.
        """
        def unwind(obj) -> list[tuple[tuple[Union[str, int]], Any]]:
            """
            Recursively unwind a nested dict/list into flat key tuples.
            """
            if isinstance(obj, dict):
                items = []
                for k, v in obj.items():
                    for subkeys, subvalue in unwind(v):
                        items.append(((k,) + subkeys, subvalue))
                return items
            elif isinstance(obj, list):
                items = []
                for idx, v in enumerate(obj):
                    for subkeys, subvalue in unwind(v):
                        items.append(((idx,) + subkeys, subvalue))
                return items
            else:
                return [((), obj)]

        self._content: dict[tuple[Union[str, int]], Any] = dict(unwind(obj))

    def __getitem__(self, key: Union[str, int, tuple]) -> Any:
        return Json.JsonView(self._content)[key]

    def __iter__(self) -> Iterator:
        return iter(self._content)

    def __len__(self) -> int:
        return len(self._content)

    def to_dataframe(self, *, index: int = 0) -> pd.DataFrame:
        """
        Converts the JSON to a wide-format DataFrame.

        Parameters
        ----------
        index : int
            Index label for the row.

        Returns
        -------
        pd.DataFrame
        """
        flat_df = pd.DataFrame({
            "Index": [index] * len(self),
            "Level": list(self._content.keys()),
            "Value": list(self._content.values())
        }, dtype=object)

        wide_df = (
            flat_df
            .pivot(index="Index", columns="Level", values="Value")
        )
        # Reset column index to plain tuple keys
        wide_df.columns = wide_df.columns
        return wide_df

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> "Json":
        """
        Rebuild a Json object from a wide-format DataFrame.

        Parameters
        ----------
        df : pd.DataFrame

        Returns
        -------
        Json
        """
        # Melt to long format
        melted = df.reset_index().melt(
            id_vars=["Index"],
            var_name="Level",
            value_name="Value")
        melted = melted.dropna(subset=["Value"])

        flat_content = {
            tuple(col if isinstance(col, tuple) else (col,) for col in [var]): val
            for var, val in zip(melted["Level"], melted["Value"])
        }

        obj = cls({})
        obj._content = {k if isinstance(k, tuple) else (k,): v for k, v in flat_content.items()}
        return obj

    def to_json(self) -> Any:
        """
        Reconstruct a nested JSON object.

        Returns
        -------
        Any
            The nested JSON structure.
        """
        def insert(container, keys, value):
            """Insert value at nested keys."""
            for key in keys[:-1]:
                if isinstance(key, int):
                    while len(container) <= key:
                        container.append(None)
                    if container[key] is None:
                        container[key] = []
                    container = container[key]
                else:
                    if key not in container:
                        container[key] = {}
                    container = container[key]
            last = keys[-1]
            if isinstance(last, int):
                while len(container) <= last:
                    container.append(None)
                container[last] = value
            else:
                container[last] = value

        root: Union[dict, list, None] = None

        for keys, value in self._content.items():
            if root is None:
                root = [] if isinstance(keys[0], int) else {}
            insert(root, keys, value)

        return root
