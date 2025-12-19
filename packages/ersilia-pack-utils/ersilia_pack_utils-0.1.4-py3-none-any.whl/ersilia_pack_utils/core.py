import csv
import json
import struct
import numpy as np
from typing import List, Tuple, Optional, Any

Smiles = List[str]
Header = List[str]

_ALLOWED_BIN_DTYPES = {
    np.dtype(np.int8),
    np.dtype(np.int16),
    np.dtype(np.int32),
    np.dtype(np.int64),
    np.dtype(np.float32),
    np.dtype(np.float64),
}

_DTYPE_ALIASES = {
    "float": np.dtype(np.float64),
    "float32": np.dtype(np.float32),
    "float64": np.dtype(np.float64),
    "int8": np.dtype(np.int8),
    "int16": np.dtype(np.int16),
    "int32": np.dtype(np.int32),
    "int64": np.dtype(np.int64),
}

def _normalize_dtype(dtype: Any) -> np.dtype:
    if dtype is None:
        raise ValueError("dtype must be specified.")

    if isinstance(dtype, str):
        key = dtype.strip().lower()
        if key in _DTYPE_ALIASES:
            return _DTYPE_ALIASES[key]
        return np.dtype(key)

    if isinstance(dtype, (int, float)) and not isinstance(dtype, bool):
        return np.dtype(type(dtype))

    return np.dtype(dtype)


def read_smiles_csv(in_file: str) -> Tuple[Header, Smiles]:
    with open(in_file, "r", newline="") as f:
        reader = csv.reader(f)
        cols = next(reader)
        data = [r[0] for r in reader]
    return cols, data


def read_smiles_bin(in_file: str) -> Tuple[Header, Smiles]:
    with open(in_file, "rb") as f:
        data = f.read()

    mv = memoryview(data)
    nl = mv.tobytes().find(b"\n")
    meta = json.loads(mv[:nl].tobytes().decode("utf-8"))
    cols = meta.get("columns", [])
    count = meta.get("count", 0)

    smiles_list = [None] * count
    offset = nl + 1
    for i in range(count):
        (length,) = struct.unpack_from(">I", mv, offset)
        offset += 4
        smiles_list[i] = mv[offset: offset + length].tobytes().decode("utf-8")
        offset += length

    return cols, smiles_list


def read_smiles(in_file: str) -> Tuple[Header, Smiles]:
    if in_file.endswith(".bin"):
        return read_smiles_bin(in_file)
    return read_smiles_csv(in_file)


def write_out_csv(results, header, file: str) -> None:
    with open(file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)


def write_out_bin(results, header, file: str, dtype: Optional[Any] = None) -> None:
    dt = _normalize_dtype(dtype)

    if dt not in _ALLOWED_BIN_DTYPES:
        allowed = ", ".join(sorted(d.name for d in _ALLOWED_BIN_DTYPES))
        raise ValueError(f"Unsupported dtype {dt!r}. Allowed: {allowed}")

    arr = np.asarray(results, dtype=dt)
    if arr.ndim == 1:
        arr = arr.reshape(-1, 1)

    if len(header) != arr.shape[1]:
        raise ValueError(f"Header length ({len(header)}) != number of columns ({arr.shape[1]}).")

    meta = {"columns": list(header), "shape": list(arr.shape), "dtype": dt.name}
    meta_bytes = (json.dumps(meta) + "\n").encode("utf-8")

    with open(file, "wb") as f:
        f.write(meta_bytes)
        f.truncate(len(meta_bytes) + arr.nbytes)

    m = np.memmap(file, dtype=dt, mode="r+", offset=len(meta_bytes), shape=arr.shape)
    m[:] = arr
    m.flush()


def write_out(results, header, file: str, dtype: Optional[Any] = np.float32) -> None:
    if file.endswith(".bin"):
        write_out_bin(results, header, file, dtype)
    elif file.endswith(".csv"):
        write_out_csv(results, header, file)
    else:
        raise ValueError(f"Unsupported extension for {file!r}")
