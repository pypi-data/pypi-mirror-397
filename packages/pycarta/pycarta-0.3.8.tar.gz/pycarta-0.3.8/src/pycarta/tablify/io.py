import os
import json
from json import JSONDecodeError
from pathlib import Path
from typing import Union, IO, Any

PathLike = Union[str, Path]
StreamLike = IO[Any]


def load_json(
    source: Union[PathLike, StreamLike, Any],
    *,
    encoder: type = json.JSONEncoder,
    decoder: type = json.JSONDecoder
) -> Any:
    """
    Load JSON from a path, string, stream, or JSON-like object.
    
    - If a path or file-like object, contents are read from disk.
    - If a string, attempts to parse it as a JSON string.
    - If a dict/list/int/etc, it's normalized by round-tripping through json.dumps/loads.
    
    Parameters
    ----------
    source : str, Path, file-like, or JSON-like Python object
        The source content to be loaded and normalized.
    encoder : JSONEncoder, optional
        Used to encode raw objects during normalization.
    decoder : JSONDecoder, optional
        Used to decode JSON content.

    Returns
    -------
    Any
        The deserialized JSON content (can be a dict, list, int, etc.)

    Raises
    ------
    TypeError
        If the input cannot be parsed or normalized into JSON.
    """
    try:
        if os.path.isfile(str(source)):
            # source is a file.
            with open(source, "rb") as f:
                content = json.load(f, cls=decoder)
        elif hasattr(source, "read"):
            # source is file-like
            content = json.load(source, cls=decoder)
        else:
            # source is str or bytes
            content = json.loads(source, cls=decoder)
    except JSONDecodeError:
        raise JSONDecodeError(f"{source} cannot be processed as JSON.")
    except TypeError:
        # source is already a JSON-formatted python object
        content = source
    try:
        # Ensure content is valid JSON content 
        return json.loads(json.dumps(content))
    except Exception as e:
        raise TypeError(f"Unsupported input type: {type(source)}") from e
