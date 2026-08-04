"""Execution helpers used by ``ftw_turkiye_eda.ipynb``.

The notebook owns the analytical choices and exports.  This module contains only
low-level routines that would otherwise obscure those choices: exhaustive
batch-wise geometry checks, a dependency-free reader for the HGM XLSX workbook,
Lin's concordance coefficient, and a grid-neighbour diagnostic.
"""

from __future__ import annotations

import json
import re
import ssl
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import certifi
import numpy as np
import pandas as pd


XLSX_NAMESPACE = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
HTTPS_CONTEXT = ssl.create_default_context(cafile=certifi.where())

def _sql_path(path: Path) -> str:
    return str(path.resolve()).replace("'", "''")


def read_xlsx_cell_rows(path: Path) -> list[dict[str, str]]:
    """Read the first worksheet of a simple XLSX file without openpyxl."""

    with ZipFile(path) as archive:
        shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
        shared_strings = [
            "".join(node.text or "" for node in item.findall(".//m:t", XLSX_NAMESPACE))
            for item in shared_root.findall("m:si", XLSX_NAMESPACE)
        ]
        sheet_root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))

    rows: list[dict[str, str]] = []
    for row in sheet_root.findall(".//m:sheetData/m:row", XLSX_NAMESPACE):
        values: dict[str, str] = {}
        for cell in row.findall("m:c", XLSX_NAMESPACE):
            column = re.match(r"[A-Z]+", cell.attrib["r"])
            value_node = cell.find("m:v", XLSX_NAMESPACE)
            value = "" if value_node is None else (value_node.text or "")
            if cell.attrib.get("t") == "s" and value:
                value = shared_strings[int(value)]
            if column:
                values[column.group()] = value
        rows.append(values)
    return rows


def batched_geometry_quality(
    connection,
    parquet_path: Path,
    *,
    layer_expression: str,
    stage: str,
    scope_expression: str,
    batch_size: int = 1_000_000,
) -> pd.DataFrame:
    """Exhaustively audit geometry status without materialising a large frame.

    Rows are split into the declared analysis scope and excluded scope in the
    same scan.  This keeps peak memory bounded and permits before/after checks on
    multi-gigabyte GeoParquet files.
    """

    path_sql = _sql_path(parquet_path)
    row_count = int(
        connection.execute(
            f"SELECT count(*) FROM read_parquet('{path_sql}', file_row_number=true)"
        ).fetchone()[0]
    )
    parts: list[pd.DataFrame] = []
    for start in range(0, row_count, batch_size):
        stop = min(start + batch_size, row_count)
        part = connection.execute(
            f"""SELECT
                {layer_expression} AS layer,
                CASE WHEN {scope_expression}
                     THEN 'analysis_scope' ELSE 'excluded_scope' END AS scope_group,
                count(*) AS row_count,
                sum(CASE WHEN geometry IS NULL THEN 1 ELSE 0 END) AS null_geometry_count,
                sum(CASE WHEN geometry IS NOT NULL AND ST_IsEmpty(geometry) THEN 1 ELSE 0 END)
                    AS empty_geometry_count,
                sum(CASE WHEN geometry IS NOT NULL AND NOT ST_IsEmpty(geometry)
                              AND NOT ST_IsValid(geometry) THEN 1 ELSE 0 END)
                    AS invalid_geometry_count,
                sum(CASE WHEN geometry IS NOT NULL AND NOT ST_IsEmpty(geometry)
                              AND ST_IsValid(geometry) THEN 1 ELSE 0 END)
                    AS valid_geometry_count
            FROM read_parquet('{path_sql}', file_row_number=true)
            WHERE file_row_number >= {start} AND file_row_number < {stop}
            GROUP BY 1, 2"""
        ).fetchdf()
        parts.append(part)
    result = (
        pd.concat(parts, ignore_index=True)
        .groupby(["layer", "scope_group"], as_index=False)[
            [
                "row_count",
                "null_geometry_count",
                "empty_geometry_count",
                "invalid_geometry_count",
                "valid_geometry_count",
            ]
        ]
        .sum()
    )
    result.insert(0, "stage", stage)
    result["batch_size"] = batch_size
    result["repair_applied"] = False
    return result


def lin_concordance(x: pd.Series, y: pd.Series) -> float:
    """Return Lin's concordance correlation coefficient using population moments."""

    paired = pd.concat([x, y], axis=1).dropna().astype(float)
    x_values = paired.iloc[:, 0].to_numpy()
    y_values = paired.iloc[:, 1].to_numpy()
    covariance = np.mean((x_values - x_values.mean()) * (y_values - y_values.mean()))
    denominator = (
        x_values.var(ddof=0)
        + y_values.var(ddof=0)
        + (x_values.mean() - y_values.mean()) ** 2
    )
    return float(2.0 * covariance / denominator) if denominator else float("nan")


def size_band_decomposition(
    threshold_shares: pd.DataFrame,
    layer_totals: dict[int, tuple[int, float]],
    *,
    thresholds: tuple[float, ...] = (0.1, 0.5, 1.0, 2.0, 5.0),
) -> pd.DataFrame:
    """Decompose the between-layer count and area change by mapped-unit size band.

    Differences between annual layers are reported per size band so that a
    distribution-wide shift can be distinguished from a shift concentrated at
    one end. This is a distributional diagnostic only: it does not match or
    track individual polygons and cannot attribute a band-level difference to
    the splitting or merging of any particular mapped unit.
    """

    cumulative = {
        (int(row["layer"]), float(row["area_threshold_ha"])): (
            float(row["share_of_field_count_below_pct"]),
            float(row["share_of_mapped_area_below_pct"]),
        )
        for _, row in threshold_shares.iterrows()
    }
    layers = sorted(layer_totals)
    edges = list(zip((0.0,) + thresholds, thresholds + (None,)))

    records = []
    for lower, upper in edges:
        record: dict[str, float | str] = {
            "lower_bound_ha": lower,
            "upper_bound_ha": upper if upper is not None else float("inf"),
            "band_label": f"{lower}-{upper}" if upper is not None else f">={lower}",
        }
        for layer in layers:
            count_total, area_total = layer_totals[layer]
            upper_shares = (100.0, 100.0) if upper is None else cumulative[(layer, upper)]
            lower_shares = (0.0, 0.0) if lower == 0.0 else cumulative[(layer, lower)]
            record[f"field_count_{layer}"] = (
                (upper_shares[0] - lower_shares[0]) / 100.0 * count_total
            )
            record[f"mapped_area_ha_{layer}"] = (
                (upper_shares[1] - lower_shares[1]) / 100.0 * area_total
            )
        if len(layers) == 2:
            early, late = layers
            record["field_count_difference"] = (
                record[f"field_count_{late}"] - record[f"field_count_{early}"]
            )
            record["mapped_area_ha_difference"] = (
                record[f"mapped_area_ha_{late}"] - record[f"mapped_area_ha_{early}"]
            )
            base = record[f"field_count_{early}"]
            record["field_count_difference_pct"] = (
                100.0 * record["field_count_difference"] / base if base else float("nan")
            )
        records.append(record)
    return pd.DataFrame(records)


def grid_neighbour_diagnostic(
    grid: pd.DataFrame,
    *,
    x_column: str,
    y_column: str,
    value_column: str,
) -> pd.DataFrame:
    """Summarise rook-neighbour similarity and Moran's I for a regular grid.

    Weights are binary rook contiguity on the regular grid: each cell is a
    neighbour of the cell one step away in x or in y. Each adjacency is counted
    once, which is equivalent to the standard symmetric-weight formulation.
    The result is a finite-grid descriptive diagnostic; it has no permutation
    test or significance interpretation.
    """

    frame = grid[[x_column, y_column, value_column]].dropna().copy()
    frame[x_column] = frame[x_column].astype(int)
    frame[y_column] = frame[y_column].astype(int)
    frame = frame.reset_index(drop=True)
    frame["_pos"] = np.arange(len(frame), dtype=int)

    keys = frame[[x_column, y_column, "_pos"]]
    own_pos: list[np.ndarray] = []
    neighbour_pos: list[np.ndarray] = []
    for delta_x, delta_y in [(1, 0), (0, 1)]:
        shifted = keys.rename(columns={"_pos": "_neighbour_pos"}).copy()
        shifted[x_column] -= delta_x
        shifted[y_column] -= delta_y
        pair = keys.merge(shifted, on=[x_column, y_column], how="inner")
        own_pos.append(pair["_pos"].to_numpy())
        neighbour_pos.append(pair["_neighbour_pos"].to_numpy())
    left = np.concatenate(own_pos) if own_pos else np.empty(0, dtype=int)
    right = np.concatenate(neighbour_pos) if neighbour_pos else np.empty(0, dtype=int)

    values = frame[value_column].to_numpy(dtype=float)
    cell_count = len(frame)
    pair_count = len(left)

    def morans_i(sample: np.ndarray) -> float:
        centred = sample - sample.mean()
        denominator = float(np.square(centred).sum())
        if not pair_count or denominator <= 0:
            return float("nan")
        numerator = float((centred[left] * centred[right]).sum())
        return cell_count / pair_count * numerator / denominator

    moran_i = morans_i(values)
    differences = np.abs(values[left] - values[right])
    record = {
        "grid_cell_count": cell_count,
        "rook_neighbour_pair_count": pair_count,
        "median_absolute_neighbour_difference_pct": float(np.median(differences)),
        "share_neighbour_pairs_within_10pp_pct": float(
            100.0 * (differences <= 10).mean()
        ),
        "morans_i_null_share": float(moran_i),
    }

    return pd.DataFrame([record])


def fetch_json(url: str, *, timeout: int = 90) -> dict:
    request = Request(url, headers={"User-Agent": "ftw-turkiye-eda/round1"})
    try:
        with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
            return json.load(response)
    except (URLError, ssl.SSLError):
        payload = subprocess.check_output(
            ["curl", "-L", "--fail", "--silent", "--show-error", url],
            timeout=timeout,
        )
        return json.loads(payload)
