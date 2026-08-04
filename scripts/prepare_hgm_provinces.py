#!/usr/bin/env python3
"""Derive an auditable 81-province reporting layer from HGM 2026 linework.

HGM distributes country/province boundary lines and settlement points rather
than ready-made province polygons.  This script polygonizes those HGM edges,
selects a pinned manifest of Turkish land components discovered from the HGM
country-line record block, labels principal faces with HGM province-capital
points, and links detached components to the nearest principal HGM face.  Four
water-separated components are explicitly adjudicated from HGM district points
and the independently published HGM province-area workbook.  Every selection,
edge, label and validation input therefore comes from the pinned HGM products.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from importlib.metadata import version
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import geopandas as gpd
import pandas as pd
from pyproj import Transformer
from shapely import make_valid, normalize
from shapely.ops import polygonize, transform, unary_union


EXPECTED_ARCHIVE_SHA256 = (
    "da8efe4dcbe47e5e8a8a34068e1e729832420634b519fab62303b86254471284"
)
EXPECTED_HGM_WORKBOOK_SHA256 = (
    "e6054762f2e03e72b56ef85cb430ea00b012ccc5eba3a8fea08e3a631d3b6447"
)
EXPECTED_PROVINCE_LOOKUP_SHA256 = (
    "6665b02547102d85d07f380147cc52f1baee6e991cc0f94ff0c844f727ec766f"
)

HGM_SOURCE_URL = "https://www.harita.gov.tr/urun/turkiye-mulki-idare-sinirlari/232"
HGM_AREA_SOURCE_URL = "https://www.harita.gov.tr/il-ve-ilce-yuzolcumleri"
SOURCE_ACCESS_DATE = "2026-07-31"

EXPECTED_PROVINCES = 81
EXPECTED_SETTLEMENTS = 1_003
EXPECTED_POLYGONIZED_COUNTRY_FACES = 130
EXPECTED_SELECTED_COUNTRY_FACES = 57
EXPECTED_POLYGONIZED_PROVINCE_FACES = 353
EXPECTED_CAPITAL_FACE_COUNT = 81
EXPECTED_MATERIAL_NEAREST_FACE_COUNT = 52
EXPECTED_ADJUDICATED_FACE_COUNT = 4
EXPECTED_MICROSCOPIC_NEAREST_FACE_COUNT = 216
EXPECTED_HGM_AREA_TOTAL_KM2 = 780_043.0
EXPECTED_NATIONAL_AREA_DIFFERENCE_KM2 = 0.00857196981087327
MAX_NATIONAL_AREA_DIFFERENCE_DEVIATION_KM2 = 0.000001
MAX_PROVINCE_MEAN_ABSOLUTE_DIFFERENCE_PCT = 0.05
MAX_PROVINCE_ABSOLUTE_DIFFERENCE_PCT = 0.20
MATERIAL_COMPONENT_M2 = 1_000.0
MAX_SOURCE_COVERAGE_DIFFERENCE_M2 = 0.000001
COUNTRY_FACE_DISCOVERY_MAX_OBJECTID = 60

PINNED_COUNTRY_FACE_SHA256 = frozenset(
    {
        "05fbf094145237c94d4ec2f101339b2777f8d8892d7ecef6cbe4b8272a66c105",
        "0707d120fcb4e28e0d9f7b9753c64bbfc85170924228b43711f61c594b47f722",
        "09a7efbe6dad68a5dc0a24e1e29d596d5ae717069879c3f420aee37fbd5f051a",
        "0f44a7593d5ae02ce715f711e70e013ddb067b3d4e1ddc7356e81662e3017001",
        "1227b33da030ff9aefb2e7f2c083a492d449d4c1f340667b0f8f52a6c22c66e1",
        "16c984f2e0bfc855d6037b5c9393793f98659e62efe77938ac04742fdba3ce05",
        "18eeb227e0fafc23de7c6a5eda7801d60e244dae8da929f4ea146cfea34a3ae3",
        "1cb6e2ee556fbdccdd2e76fb86ff8772884fa0c4a00e7e9cf5167f969683fbfe",
        "2245fcdd559821ad4f781805127240536cf76879ed0dcc827ada1d4259175994",
        "23279c6c1c0938efc6bf6ad8834fce9a93adf071e9d5c21ceeb8f51bbb7ad642",
        "266b78ee41cc01ec11214a60ec4ed2b00c67ef59e693bbfca3e29a48482b8408",
        "26d35306db2bb7efe31e84e7286bd14f1613cdeb49d118c5634fbbcc85b2e9fd",
        "2a212467b0bc1a3c15d592b7527dd4281b1b6a47402515553bd5a77ec1f9c6a3",
        "2a91ad04372c3ecf7731655cd3e4cea327688d5b2aeb595ba1dd65e213b9e204",
        "2ac14071cafb67dd3d0141e02d9b41c358a3b18aae29a1f381a6aa67451ec709",
        "2b0f60fc840433f4c5c34b0fa798e3d13d70d99bb871df151a5844a10e36f588",
        "30c14ab65ff2736a252e28de1103badd49c086e4a134dbf5ecb5390b880bf2bc",
        "322b3f39fd1c4e9aa719e2ee7a7003c8e848f212cd686ee4abd317f368fbb7e5",
        "39c19ed76c444f2c81526580ab37af62d28c7a907324d9d12ea10e55b5316ca4",
        "40515426cc12c7a054ee54921e66c7eb4cf94ad8cb26c5a002ffc4023fdb6bee",
        "40b0c78b2f9afdbe470d4a2c58635b3df188fbb8a0ca51b715b570ee5421c624",
        "43577d617b9269c2554b4e73b5cfb26c1b2a62e1315fdd045787e7a24e7b7253",
        "46b29ba16e52145d53c523d930d824cdbcccf299e2edb33c16af8c4f711774cb",
        "4beabc26ac3dc1341193e44821544a139bec6a2a82224543097763226ae16160",
        "568a59df9c327e6cb05ae3c90b2272da971297f8c17d3928e8ed99c28a3f60b5",
        "6282c8df0ee2cdc01832e055dbacecb14886cfaca97b247adbe32c2b16d10041",
        "6c3d88d63d779115858111365791176b5f04bca714cc8d866e48d974ab9aaa8b",
        "76ee2b87d5b360ac9c1070615934098f2124b21adef1663deb8c3d9bd66df237",
        "7e54f325ebbff48bae603db8c1fc6b7d68db8c3f9abac01f328c7b67e23a26b7",
        "807a1603b40fd167c9974bdd454103154a528e721fe8e7e912969bb218ff6a62",
        "83bb8240f16e883714f0256a802f3132c233810f4a9db96ecc93265232ae152b",
        "8d0fbea7e59fe9c16402fbc82dbeef230c102033c2b99c838533970a53bb0096",
        "8dc489e34876465b905db2647456e2b9ce521ce8441d8c0d3cb947a9a015a233",
        "8dfb15e82c981adc65ae9aaa06f7ff57a148e9e89a17ea08fb86c8ef94090eae",
        "92abf9593425854a0dd3c4ba5fcfb48ce50a65db14db2a66f41bbf29e06eacd1",
        "92c7ac4db0c736907558ee0d556689052f64d3107a6075d0d25a2653a81ff397",
        "976e2d0e463691210f5c5b4540885bae6f65958cb392a5f70c896d5bc5e91388",
        "9e5f1f2df0bf8f14cd1a4f9dd59ca456041344f347e558b6a6557045b15090f5",
        "ae749364aff8d5bcd3db0a275cb84b621262e96a39bcd015dc1524cf76bdd0cc",
        "b38f44d693d58b3552de12f6a5c7430b915c77122e7c0ead3e12e69f72bd4343",
        "b70f13d2b0a6715be6f8dd42c9b61d996a8c1f4638f09cf4bc9d275b2e2d4722",
        "baab54dd319ede58f2d7c2d1bcd14e6746fa845d365d6c1052bb0f2b01a4d5b0",
        "bb19636c1e5d7d7e787ce8b6ebc6a44235c8141850ada707ac97aa84d90b649c",
        "c0754b3b8e79505002c61837476c976bff7d1cf46f9aaf05a787c3602960b063",
        "ca9b1dce69cb3aa199783edd8da5b15a321453b70193645eaefc273180a59137",
        "cdd4541dfb2bd2418c9fbf88f2000db3102dfcd2c23940d81f4a6c18f3b974a9",
        "cdd6e1a3b979cb1b1217272a0424105a38822eaaee8faaebe0760b72cb2f2a01",
        "d6d2e34a1dbc2b235b03ad60763b882b26fb8083896be14bbaeedd31f7184fb5",
        "d95de650299cc081918632de1a8f9e2a09f92affcc3ea0186bc0dc1a425ee442",
        "d9c4d1203ccdc49572be8602a03d269b9087b3a772780b123f7c4f76bbcfd806",
        "e87633b4c00a97f75d7b6d7353d2fe16e7a4aec782005302d77c73648d14a788",
        "e9282072a4d3910412f2a1780227eeae0b8f9347470acae500c2bfcb49188f81",
        "eb27274a48fee53342232120d9241d383069a2d253022cc4903f2e6713ca4486",
        "ed5541dd3d73207c20f82abf8874e2dfce8ea38800bb463db5b8b89840dc2000",
        "f003a924a7a0262b8d37479ee601c5fd52c0b5af7f63de8331789895c08d6fb4",
        "fb24528c8324fe840aef8c6ad4710baba8f4c38f52c115f8505560d93fdc7b7c",
        "fbc8087c472c25f897a100ab5d5719d015c5449876168e117342b4b7b946ec19",
    }
)

ADJUDICATED_COMPONENTS = {
    "09cfdb2a596d46c931e6ee64b777e0c4dff0805c89836906ad7f73577c939be8": {
        "province_code": "17",
        "rationale": (
            "Gelibolu/Eceabat face: HGM district points and the HGM Çanakkale "
            "workbook-area deficit identify the water-separated component."
        ),
    },
    "6822d3e4e1104f7b9327947f82843a7664c5a2d89a87bc00db57f797fd469c2e": {
        "province_code": "34",
        "rationale": (
            "İstanbul Asian face: thirteen HGM district points, the nearest HGM "
            "province-capital point and the HGM İstanbul workbook-area deficit agree."
        ),
    },
    "8dfb15e82c981adc65ae9aaa06f7ff57a148e9e89a17ea08fb86c8ef94090eae": {
        "province_code": "34",
        "rationale": (
            "Büyükada face: the HGM Adalar district point and the HGM İstanbul "
            "workbook-area deficit identify the component."
        ),
    },
    "d95de650299cc081918632de1a8f9e2a09f92affcc3ea0186bc0dc1a425ee442": {
        "province_code": "34",
        "rationale": (
            "Sedef island face: its HGM island-cluster geometry and the remaining "
            "HGM İstanbul workbook-area deficit identify the component."
        ),
    },
}

XLSX_NAMESPACE = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive",
        type=Path,
        default=Path("data/external/hgm_turkiye_mulki_idare_sinirlari_2026.rar"),
    )
    parser.add_argument(
        "--seven-zip",
        default=None,
        help="7-Zip executable with RAR5 support (auto-detects 7zz or 7z)",
    )
    parser.add_argument(
        "--hgm-area-workbook",
        type=Path,
        default=Path("data/external/il_ilce_alanlari_2026_hgm.xlsx"),
    )
    parser.add_argument(
        "--province-lookup",
        type=Path,
        default=Path("tables/table_s4_province_lookup.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/external/hgm_2026_province_boundaries_wgs84.geojson"),
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=Path("data/external/hgm_2026_province_boundaries_metadata.json"),
    )
    parser.add_argument(
        "--country-face-audit-output",
        type=Path,
        default=Path("data/external/hgm_2026_country_face_selection_audit.csv"),
    )
    parser.add_argument(
        "--component-audit-output",
        type=Path,
        default=Path("data/external/hgm_2026_component_assignment_audit.csv"),
    )
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_sha256(path: Path, expected: str, label: str) -> str:
    observed = sha256(path)
    if observed != expected:
        raise RuntimeError(
            f"Unexpected {label} SHA-256: {observed}; expected {expected}"
        )
    return observed


def normalized_name(value: str) -> str:
    value = value.replace("ı", "i").replace("İ", "I")
    return "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    ).casefold()


def face_id(geometry) -> str:
    return hashlib.sha256(normalize(geometry).wkb).hexdigest()


def logical_name(path: Path) -> str:
    """Keep metadata independent of the absolute output directory."""
    return path.name


def find_seven_zip(requested: str | None) -> str:
    if requested:
        executable = shutil.which(requested) or requested
        if Path(executable).exists() or shutil.which(executable):
            return executable
        raise FileNotFoundError(f"7-Zip executable not found: {requested}")
    for candidate in ("7zz", "7z"):
        executable = shutil.which(candidate)
        if executable:
            return executable
    raise FileNotFoundError(
        "RAR5 extraction requires 7-Zip. Install 7zz/7z or pass --seven-zip PATH."
    )


def seven_zip_version(executable: str) -> str:
    result = subprocess.run(
        [executable], check=False, capture_output=True, text=True
    )
    lines = [line.strip() for line in (result.stdout + result.stderr).splitlines()]
    return next((line for line in lines if line.startswith("7-Zip")), "unknown")


def find_shapefile(root: Path, stem: str) -> Path:
    matches = list(root.rglob(f"{stem}.shp"))
    if len(matches) != 1:
        raise RuntimeError(f"Expected one {stem}.shp, found {len(matches)}")
    return matches[0]


def normalize_projection_encoding(shapefile: Path) -> None:
    """Convert Turkish Windows-1254 WKT text to UTF-8 for GDAL/PROJ."""
    prj = shapefile.with_suffix(".prj")
    payload = prj.read_bytes()
    try:
        payload.decode("utf-8")
    except UnicodeDecodeError:
        prj.write_text(payload.decode("windows-1254"), encoding="utf-8")


def read_xlsx_cell_rows(path: Path) -> list[dict[str, str]]:
    """Read the first worksheet of the simple HGM XLSX without openpyxl."""
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


def hgm_area_lookup(
    workbook: Path, name_to_code: dict[str, str]
) -> dict[str, float]:
    result: dict[str, float] = {}
    for row in read_xlsx_cell_rows(workbook):
        name = row.get("C", "")
        code = name_to_code.get(normalized_name(name))
        if code is None or not row.get("D"):
            continue
        result[code] = float(row["D"])
    if len(result) != EXPECTED_PROVINCES:
        raise RuntimeError(f"Expected 81 HGM province areas, found {len(result)}")
    if sum(result.values()) != EXPECTED_HGM_AREA_TOTAL_KM2:
        raise RuntimeError(
            f"Unexpected HGM workbook total: {sum(result.values()):,.3f} km2"
        )
    return result


def audit_coordinates(geometry, transformer: Transformer) -> dict[str, float]:
    wgs84 = transform(transformer.transform, geometry)
    point = wgs84.representative_point()
    minx, miny, maxx, maxy = wgs84.bounds
    return {
        "representative_longitude": point.x,
        "representative_latitude": point.y,
        "bbox_xmin": minx,
        "bbox_ymin": miny,
        "bbox_xmax": maxx,
        "bbox_ymax": maxy,
    }


def manifest_sha256(values: set[str] | frozenset[str]) -> str:
    """Hash a sorted, newline-delimited set so the manifest is portable."""
    payload = "".join(f"{value}\n" for value in sorted(values)).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def country_line_evidence(geometry, country_lines: gpd.GeoDataFrame) -> dict[str, object]:
    """Return HGM country-line records that form a polygonized face boundary."""
    boundary = geometry.boundary
    intersections = []
    objectids: list[int] = []
    candidates = country_lines.loc[country_lines.geometry.intersects(boundary)]
    for row in candidates.itertuples():
        intersection = row.geometry.intersection(boundary)
        if intersection.length <= 0:
            continue
        intersections.append(intersection)
        objectids.append(int(row.OBJECTID))
    if not objectids:
        raise RuntimeError(
            f"Country face {face_id(geometry)} has no contributing HGM line record"
        )
    unique_objectids = sorted(set(objectids))
    covered_length = float(unary_union(intersections).length)
    return {
        "hgm_country_line_objectids": ";".join(map(str, unique_objectids)),
        "hgm_country_line_objectid_min": min(unique_objectids),
        "hgm_country_line_objectid_max": max(unique_objectids),
        "hgm_country_line_boundary_coverage_fraction": covered_length
        / float(boundary.length),
    }


def ranked_principal_faces(
    geometry, principal_faces: gpd.GeoDataFrame
) -> list[dict[str, object]]:
    """Rank HGM principal faces by distance, breaking exact ties by province code."""
    ranked = [
        {
            "province_code": str(row.province_code),
            "province_name": str(row.province_name),
            "face_sha256": str(row.face_sha256),
            "distance_m": float(geometry.distance(row.geometry)),
        }
        for row in principal_faces.itertuples()
    ]
    return sorted(
        ranked,
        key=lambda row: (
            float(row["distance_m"]),
            str(row["province_code"]),
            str(row["face_sha256"]),
        ),
    )


def assignment_record(
    face_record: dict[str, object],
    principal_faces: gpd.GeoDataFrame,
) -> dict[str, object]:
    """Assign one province face using only pinned HGM-derived evidence."""
    geometry = face_record["geometry"]
    face_sha256 = str(face_record["face_sha256"])
    capital_code = str(face_record["capital_code"])
    ranked = ranked_principal_faces(geometry, principal_faces)

    if capital_code:
        own = next(row for row in ranked if row["province_code"] == capital_code)
        others = [row for row in ranked if row["province_code"] != capital_code]
        nearest, second = own, others[0]
        province_code = capital_code
        method = "HGM province-capital point"
        override_rationale = ""
        assigned_candidate_rank = 1
    else:
        nearest, second = ranked[:2]
        adjudication = ADJUDICATED_COMPONENTS.get(face_sha256)
        if adjudication is not None:
            province_code = str(adjudication["province_code"])
            method = "HGM-only adjudicated material component"
            override_rationale = str(adjudication["rationale"])
        else:
            province_code = str(nearest["province_code"])
            method = (
                "nearest HGM principal face (material)"
                if float(geometry.area) > MATERIAL_COMPONENT_M2
                else "nearest HGM principal face (microscopic)"
            )
            override_rationale = ""
        assigned_candidate_rank = next(
            position
            for position, candidate in enumerate(ranked, start=1)
            if candidate["province_code"] == province_code
        )

    assigned = next(
        candidate
        for candidate in ranked
        if candidate["province_code"] == province_code
    )
    return {
        "province_code": province_code,
        "assignment_method": method,
        "nearest_principal_code": nearest["province_code"],
        "nearest_principal_name": nearest["province_name"],
        "nearest_principal_face_sha256": nearest["face_sha256"],
        "nearest_principal_distance_m": nearest["distance_m"],
        "second_principal_code": second["province_code"],
        "second_principal_name": second["province_name"],
        "second_principal_face_sha256": second["face_sha256"],
        "second_principal_distance_m": second["distance_m"],
        "nearest_principal_distance_margin_m": (
            float(second["distance_m"]) - float(nearest["distance_m"])
        ),
        "assigned_principal_distance_m": assigned["distance_m"],
        "assigned_candidate_rank": assigned_candidate_rank,
        "adjudicated_override": bool(override_rationale),
        "override_rationale": override_rationale,
        "manual_review_flag": bool(override_rationale),
    }


def pairwise_overlap_summary(frame: gpd.GeoDataFrame) -> dict[str, object]:
    records: list[tuple[str, str, float]] = []
    for left_position in range(len(frame)):
        left = frame.iloc[left_position]
        for right_position in range(left_position + 1, len(frame)):
            right = frame.iloc[right_position]
            if not left.geometry.intersects(right.geometry):
                continue
            area = float(left.geometry.intersection(right.geometry).area)
            if area > 0:
                records.append((left.province_code, right.province_code, area))
    return {
        "positive_overlap_pair_count": len(records),
        "total_pairwise_overlap_m2": sum(record[2] for record in records),
        "maximum_pairwise_overlap_m2": max((record[2] for record in records), default=0.0),
        "overlap_pairs": [
            {"left": left, "right": right, "overlap_m2": area}
            for left, right, area in records
        ],
    }


def write_audit(frame: pd.DataFrame, path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.12g", lineterminator="\n")
    return sha256(path)


def main() -> None:
    args = parse_args()
    input_hashes = {
        "hgm_archive": verify_sha256(
            args.archive, EXPECTED_ARCHIVE_SHA256, "HGM boundary archive"
        ),
        "hgm_area_workbook": verify_sha256(
            args.hgm_area_workbook,
            EXPECTED_HGM_WORKBOOK_SHA256,
            "HGM area workbook",
        ),
        "province_lookup": verify_sha256(
            args.province_lookup,
            EXPECTED_PROVINCE_LOOKUP_SHA256,
            "province lookup",
        ),
    }
    input_hashes["derivation_script"] = sha256(Path(__file__).resolve())

    seven_zip = find_seven_zip(args.seven_zip)
    lookup = pd.read_csv(args.province_lookup, dtype={"province_code": str})
    lookup["province_code"] = lookup["province_code"].str.zfill(2)
    if len(lookup) != EXPECTED_PROVINCES or lookup["province_code"].nunique() != 81:
        raise RuntimeError("Province lookup must contain 81 unique two-digit codes")
    name_to_code = dict(
        zip(lookup["province_name"].map(normalized_name), lookup["province_code"])
    )
    published_area_by_code = hgm_area_lookup(args.hgm_area_workbook, name_to_code)

    with tempfile.TemporaryDirectory(prefix="ftw-hgm-") as temporary_directory:
        extraction_root = Path(temporary_directory)
        subprocess.run(
            [seven_zip, "x", "-y", f"-o{extraction_root}", str(args.archive.resolve())],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        country_path = find_shapefile(extraction_root, "Ülke_Sınırı")
        province_path = find_shapefile(extraction_root, "İl_Sınırı")
        settlement_path = find_shapefile(extraction_root, "Yerleşim_Noktası")
        for shapefile in (country_path, province_path, settlement_path):
            normalize_projection_encoding(shapefile)

        country_lines = gpd.read_file(country_path)
        province_lines = gpd.read_file(province_path)
        settlements = gpd.read_file(settlement_path).to_crs(country_lines.crs)
        if "OBJECTID" not in country_lines.columns:
            raise RuntimeError("HGM country linework lacks the required OBJECTID field")
        if not {"Adı", "KATEGORI"}.issubset(settlements.columns):
            raise RuntimeError("HGM settlements lack the required Adı/KATEGORI fields")
        if len(settlements) != EXPECTED_SETTLEMENTS:
            raise RuntimeError(
                f"Expected {EXPECTED_SETTLEMENTS} HGM settlements, "
                f"found {len(settlements)}"
            )
        if len(PINNED_COUNTRY_FACE_SHA256) != EXPECTED_SELECTED_COUNTRY_FACES:
            raise RuntimeError("Pinned HGM country-face manifest has the wrong size")
        transformer = Transformer.from_crs(
            country_lines.crs, "EPSG:4326", always_xy=True
        )

        polygonized_country_faces = sorted(
            [
                face
                for face in polygonize(unary_union(list(country_lines.geometry)))
                if face.area > 0
            ],
            key=face_id,
        )
        if len(polygonized_country_faces) != EXPECTED_POLYGONIZED_COUNTRY_FACES:
            raise RuntimeError(
                f"Expected {EXPECTED_POLYGONIZED_COUNTRY_FACES} polygonized country "
                f"faces, found {len(polygonized_country_faces)}"
            )

        country_face_rows: list[dict[str, object]] = []
        selected_country_faces: list[object] = []
        discovered_face_ids: set[str] = set()
        for face in polygonized_country_faces:
            identifier = face_id(face)
            line_evidence = country_line_evidence(face, country_lines)
            settlement_count = int(settlements.geometry.apply(face.covers).sum())
            discovery_selected = bool(
                line_evidence["hgm_country_line_objectid_max"]
                <= COUNTRY_FACE_DISCOVERY_MAX_OBJECTID
            )
            if discovery_selected:
                discovered_face_ids.add(identifier)
            selected = identifier in PINNED_COUNTRY_FACE_SHA256
            if selected:
                selected_country_faces.append(face)
            country_face_rows.append(
                {
                    "face_sha256": identifier,
                    "area_km2": float(face.area / 1_000_000),
                    **audit_coordinates(face, transformer),
                    **line_evidence,
                    "hgm_settlement_point_count": settlement_count,
                    "discovery_selected": discovery_selected,
                    "selected": selected,
                    "discovery_rule": (
                        "all contributing HGM country-line OBJECTID values <= 60"
                    ),
                    "selection_rule": (
                        "exact face SHA-256 membership in pinned HGM-only manifest"
                    ),
                }
            )
        country_face_audit = pd.DataFrame(country_face_rows).sort_values(
            "face_sha256"
        )
        if discovered_face_ids != PINNED_COUNTRY_FACE_SHA256:
            missing = sorted(PINNED_COUNTRY_FACE_SHA256 - discovered_face_ids)
            extra = sorted(discovered_face_ids - PINNED_COUNTRY_FACE_SHA256)
            raise RuntimeError(
                "HGM OBJECTID discovery no longer reproduces the pinned country-face "
                f"manifest; missing={missing}, extra={extra}"
            )
        if len(selected_country_faces) != EXPECTED_SELECTED_COUNTRY_FACES:
            raise RuntimeError(
                f"Expected {EXPECTED_SELECTED_COUNTRY_FACES} selected country faces, "
                f"found {len(selected_country_faces)}"
            )
        excluded_with_settlement = country_face_audit.loc[
            ~country_face_audit["selected"]
            & country_face_audit["hgm_settlement_point_count"].gt(0)
        ]
        if not excluded_with_settlement.empty:
            raise RuntimeError("A country face containing an HGM settlement was excluded")

        country = unary_union(selected_country_faces)
        settlement_covered = settlements.geometry.apply(country.covers)
        if int(settlement_covered.sum()) != EXPECTED_SETTLEMENTS:
            missing_names = sorted(
                settlements.loc[~settlement_covered, "Adı"].astype(str).tolist()
            )
            raise RuntimeError(
                "Pinned HGM country-face manifest does not cover every HGM settlement: "
                f"{missing_names}"
            )
        country_area_km2 = float(country.area / 1_000_000)
        national_area_difference_km2 = country_area_km2 - EXPECTED_HGM_AREA_TOTAL_KM2
        if (
            abs(
                national_area_difference_km2
                - EXPECTED_NATIONAL_AREA_DIFFERENCE_KM2
            )
            > MAX_NATIONAL_AREA_DIFFERENCE_DEVIATION_KM2
        ):
            raise RuntimeError(
                "Polygonized HGM country area no longer matches the pinned HGM "
                "baseline: "
                f"{national_area_difference_km2:+.12f} km2"
            )

        clipped_province_lines = unary_union(
            [geometry.intersection(country) for geometry in province_lines.geometry]
        )
        province_network = unary_union([country.boundary, clipped_province_lines])
        province_faces = sorted(
            [
                face
                for face in polygonize(province_network)
                if country.covers(face.representative_point())
            ],
            key=face_id,
        )
        if len(province_faces) != EXPECTED_POLYGONIZED_PROVINCE_FACES:
            raise RuntimeError(
                f"Expected {EXPECTED_POLYGONIZED_PROVINCE_FACES} polygonized province "
                f"faces, found {len(province_faces)}"
            )
        capitals = settlements[
            settlements["KATEGORI"].isin(["İL", "BAŞKENT"])
        ].copy()
        if len(capitals) != EXPECTED_PROVINCES:
            raise RuntimeError(
                f"Expected {EXPECTED_PROVINCES} HGM capital points, found {len(capitals)}"
            )

        code_to_name = dict(zip(lookup["province_code"], lookup["province_name"]))
        face_records: list[dict[str, object]] = []
        principal_rows: list[dict[str, object]] = []
        for face in province_faces:
            identifier = face_id(face)
            capital_hits = capitals.loc[capitals.geometry.apply(face.covers)]
            if len(capital_hits) > 1:
                names = ", ".join(sorted(capital_hits["Adı"].astype(str)))
                raise RuntimeError(
                    f"Province face {identifier} contains multiple capitals: {names}"
                )
            settlement_hits = settlements.loc[settlements.geometry.apply(face.covers)]
            capital_name = ""
            capital_code = ""
            if len(capital_hits) == 1:
                capital_name = str(capital_hits.iloc[0]["Adı"])
                capital_code = name_to_code.get(normalized_name(capital_name), "")
                if not capital_code:
                    raise RuntimeError(
                        f"Capital name is absent from province lookup: {capital_name}"
                    )
                principal_rows.append(
                    {
                        "province_code": capital_code,
                        "province_name": code_to_name[capital_code],
                        "face_sha256": identifier,
                        "geometry": face,
                    }
                )
            face_records.append(
                {
                    "face_sha256": identifier,
                    "geometry": face,
                    "area_m2": float(face.area),
                    "material_component": bool(face.area > MATERIAL_COMPONENT_M2),
                    "hgm_capital_name": capital_name,
                    "capital_code": capital_code,
                    "hgm_settlement_point_count": len(settlement_hits),
                    "hgm_district_point_count": int(
                        settlement_hits["KATEGORI"].eq("İLÇE").sum()
                    ),
                    "hgm_settlement_names": " | ".join(
                        sorted(settlement_hits["Adı"].astype(str).unique())
                    ),
                    "hgm_settlement_categories": " | ".join(
                        sorted(settlement_hits["KATEGORI"].astype(str).unique())
                    ),
                    **audit_coordinates(face, transformer),
                }
            )

        principal_faces = gpd.GeoDataFrame(
            principal_rows, geometry="geometry", crs=country_lines.crs
        ).sort_values(["province_code", "face_sha256"])
        if len(principal_faces) != EXPECTED_CAPITAL_FACE_COUNT:
            raise RuntimeError(
                f"Expected {EXPECTED_CAPITAL_FACE_COUNT} HGM principal faces, "
                f"found {len(principal_faces)}"
            )
        expected_codes = set(lookup["province_code"])
        principal_codes = set(principal_faces["province_code"])
        if principal_codes != expected_codes or not principal_faces[
            "province_code"
        ].is_unique:
            raise RuntimeError(
                "Capital-labelled principal faces differ from the 81-code lookup"
            )
        province_face_ids = {str(record["face_sha256"]) for record in face_records}
        if not set(ADJUDICATED_COMPONENTS).issubset(province_face_ids):
            missing = sorted(set(ADJUDICATED_COMPONENTS) - province_face_ids)
            raise RuntimeError(f"Pinned adjudicated HGM faces are missing: {missing}")

        component_rows: list[dict[str, object]] = []
        component_audit_rows: list[dict[str, object]] = []
        for record in face_records:
            assignment = assignment_record(record, principal_faces)
            component_rows.append(
                {
                    "province_code": assignment["province_code"],
                    "geometry": record["geometry"],
                }
            )
            component_audit_rows.append(
                {
                    key: value
                    for key, value in {**record, **assignment}.items()
                    if key not in {"geometry", "capital_code"}
                }
            )
        components = gpd.GeoDataFrame(component_rows, crs=country_lines.crs)
        component_audit = pd.DataFrame(component_audit_rows).sort_values("face_sha256")

        assignment_counts = component_audit["assignment_method"].value_counts().to_dict()
        expected_assignment_counts = {
            "HGM province-capital point": EXPECTED_CAPITAL_FACE_COUNT,
            "nearest HGM principal face (material)": (
                EXPECTED_MATERIAL_NEAREST_FACE_COUNT
            ),
            "HGM-only adjudicated material component": EXPECTED_ADJUDICATED_FACE_COUNT,
            "nearest HGM principal face (microscopic)": (
                EXPECTED_MICROSCOPIC_NEAREST_FACE_COUNT
            ),
        }
        if assignment_counts != expected_assignment_counts:
            raise RuntimeError(
                "Unexpected HGM face-assignment counts: "
                f"{assignment_counts}; expected {expected_assignment_counts}"
            )
        adjudicated_audit = component_audit.loc[
            component_audit["adjudicated_override"]
        ]
        if set(adjudicated_audit["face_sha256"]) != set(ADJUDICATED_COMPONENTS):
            raise RuntimeError("Applied HGM adjudications differ from the pinned set")
        if not adjudicated_audit["material_component"].all():
            raise RuntimeError("A pinned adjudication is no longer a material component")

        provinces = components.dissolve(by="province_code").reset_index()
        provinces = provinces.merge(
            lookup[["province_code", "province_name", "geographical_region"]],
            on="province_code",
            how="left",
            validate="one_to_one",
        )
        provinces = gpd.GeoDataFrame(
            provinces, geometry="geometry", crs=country_lines.crs
        ).sort_values("province_code").reset_index(drop=True)
        if len(provinces) != EXPECTED_PROVINCES:
            raise RuntimeError(f"Expected 81 output provinces, found {len(provinces)}")
        if not provinces.geometry.is_valid.all():
            raise RuntimeError("Source-CRS province polygons must be valid before reprojection")

        source_union = unary_union(list(provinces.geometry))
        source_coverage_symmetric_difference_m2 = float(
            source_union.symmetric_difference(country).area
        )
        if (
            source_coverage_symmetric_difference_m2
            > MAX_SOURCE_COVERAGE_DIFFERENCE_M2
        ):
            raise RuntimeError(
                "Dissolved provinces do not exactly cover the selected HGM country "
                f"faces: {source_coverage_symmetric_difference_m2:.12g} m2"
            )
        source_area_by_code = {
            row.province_code: float(row.geometry.area / 1_000_000)
            for row in provinces.itertuples()
        }
        area_comparison = pd.DataFrame(
            {
                "province_code": sorted(expected_codes),
                "derived_km2": [
                    source_area_by_code[code] for code in sorted(expected_codes)
                ],
                "published_km2": [
                    published_area_by_code[code] for code in sorted(expected_codes)
                ],
            }
        )
        area_comparison["difference_pct"] = 100 * (
            area_comparison["derived_km2"] - area_comparison["published_km2"]
        ) / area_comparison["published_km2"]
        mean_absolute_area_difference_pct = float(
            area_comparison["difference_pct"].abs().mean()
        )
        maximum_absolute_area_difference_pct = float(
            area_comparison["difference_pct"].abs().max()
        )
        if (
            mean_absolute_area_difference_pct
            > MAX_PROVINCE_MEAN_ABSOLUTE_DIFFERENCE_PCT
            or maximum_absolute_area_difference_pct
            > MAX_PROVINCE_ABSOLUTE_DIFFERENCE_PCT
        ):
            raise RuntimeError("Province areas do not reconcile to the HGM workbook")
        maximum_area_difference_row = area_comparison.loc[
            area_comparison["difference_pct"].abs().idxmax()
        ]

        provinces["boundary_source"] = "HGM 2026 linework"
        provinces["component_selection_reference"] = (
            "Pinned HGM-only country-face manifest and HGM internal evidence"
        )
        provinces["source_access_date"] = SOURCE_ACCESS_DATE
        provinces["legal_status"] = "Indicative; not legally official"

        pre_repair_wgs84 = provinces.to_crs("EPSG:4326")
        invalid_before_repair = ~pre_repair_wgs84.geometry.is_valid
        repaired_codes = pre_repair_wgs84.loc[
            invalid_before_repair, "province_code"
        ].tolist()
        output_provinces = pre_repair_wgs84.copy()
        output_provinces.loc[invalid_before_repair, "geometry"] = (
            output_provinces.loc[invalid_before_repair, "geometry"].apply(
                lambda geometry: make_valid(
                    geometry, method="structure", keep_collapsed=False
                )
            )
        )
        if not output_provinces.geometry.is_valid.all():
            raise RuntimeError("WGS84 geometries remain invalid after targeted repair")
        if not output_provinces.geom_type.isin(["Polygon", "MultiPolygon"]).all():
            raise RuntimeError("Validity repair produced a non-polygon geometry")

        pre_repair_back = pre_repair_wgs84.to_crs(country_lines.crs)
        post_repair_back = output_provinces.to_crs(country_lines.crs)
        repair_area_change_m2 = float(
            post_repair_back.geometry.area.sum()
            - pre_repair_back.geometry.area.sum()
        )
        post_repair_union = unary_union(list(post_repair_back.geometry))
        post_repair_gap_m2 = float(country.difference(post_repair_union).area)
        post_repair_excess_m2 = float(post_repair_union.difference(country).area)
        overlap_summary = pairwise_overlap_summary(post_repair_back)
        if abs(repair_area_change_m2) > 100:
            raise RuntimeError(
                "WGS84 validity repair changed more than 100 m2: "
                f"{repair_area_change_m2:+.6f} m2"
            )
        if overlap_summary["total_pairwise_overlap_m2"] > 20:
            raise RuntimeError("Repaired provinces overlap by more than 20 m2")
        if post_repair_gap_m2 + post_repair_excess_m2 > 100:
            raise RuntimeError(
                "Repaired province coverage differs from HGM by more than 100 m2: "
                f"gap={post_repair_gap_m2:.6f}, excess={post_repair_excess_m2:.6f}"
            )

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            output_provinces.to_json(
                drop_id=True, ensure_ascii=False, separators=(",", ":")
            ),
            encoding="utf-8",
        )
        output_hash = sha256(args.output)
        country_audit_hash = write_audit(
            country_face_audit, args.country_face_audit_output
        )
        component_audit_hash = write_audit(
            component_audit, args.component_audit_output
        )

        assignment_counts = {
            str(method): int(count)
            for method, count in component_audit[
                "assignment_method"
            ].value_counts().sort_index().items()
        }
        adjudicated_components = [
            {
                "face_sha256": str(row.face_sha256),
                "province_code": str(row.province_code),
                "area_m2": float(row.area_m2),
                "hgm_district_point_count": int(row.hgm_district_point_count),
                "hgm_settlement_names": str(row.hgm_settlement_names),
                "nearest_principal_code": str(row.nearest_principal_code),
                "nearest_principal_distance_m": float(
                    row.nearest_principal_distance_m
                ),
                "second_principal_code": str(row.second_principal_code),
                "second_principal_distance_m": float(
                    row.second_principal_distance_m
                ),
                "nearest_principal_distance_margin_m": float(
                    row.nearest_principal_distance_margin_m
                ),
                "assigned_candidate_rank": int(row.assigned_candidate_rank),
                "override_rationale": str(row.override_rationale),
            }
            for row in adjudicated_audit.sort_values("face_sha256").itertuples()
        ]

        metadata = {
            "source_url": HGM_SOURCE_URL,
            "source_access_date": SOURCE_ACCESS_DATE,
            "source_archive": logical_name(args.archive),
            "hgm_area_source_url": HGM_AREA_SOURCE_URL,
            "hgm_inputs": {
                "boundary_archive": logical_name(args.archive),
                "province_area_workbook": logical_name(args.hgm_area_workbook),
                "country_line_feature_count": len(country_lines),
                "province_line_feature_count": len(province_lines),
                "settlement_point_count": len(settlements),
                "settlement_category_counts": {
                    str(category): int(count)
                    for category, count in settlements[
                        "KATEGORI"
                    ].value_counts().sort_index().items()
                },
            },
            "input_sha256": input_hashes,
            "output": logical_name(args.output),
            "output_sha256": output_hash,
            "country_face_audit": logical_name(args.country_face_audit_output),
            "country_face_audit_sha256": country_audit_hash,
            "component_assignment_audit": logical_name(args.component_audit_output),
            "component_assignment_audit_sha256": component_audit_hash,
            "crs": "EPSG:4326",
            "province_count": len(output_provinces),
            "polygonized_country_face_count": len(country_face_audit),
            "selected_country_face_count": len(selected_country_faces),
            "country_face_manifest": sorted(PINNED_COUNTRY_FACE_SHA256),
            "country_face_manifest_sha256": manifest_sha256(
                PINNED_COUNTRY_FACE_SHA256
            ),
            "country_face_selection_rule": (
                "exact normalized-WKB SHA-256 membership in the pinned HGM-only "
                "face manifest"
            ),
            "country_face_discovery": {
                "role": "one-time manifest discovery and pinned-snapshot assertion only",
                "rule": (
                    "all positive-length boundary-contributing HGM country-line "
                    "OBJECTID values are <= 60"
                ),
                "maximum_objectid": COUNTRY_FACE_DISCOVERY_MAX_OBJECTID,
                "discovered_face_count": len(discovered_face_ids),
                "exactly_matches_manifest": True,
            },
            "covered_hgm_settlement_point_count": int(settlement_covered.sum()),
            "polygonized_province_face_count": len(province_faces),
            "assignment_method_counts": assignment_counts,
            "detached_component_rule": (
                "minimum distance to an HGM capital-labelled principal face; exact "
                "distance ties are resolved by ascending two-digit province code"
            ),
            "face_level_distance_audit_fields": [
                "nearest_principal_distance_m",
                "second_principal_distance_m",
                "nearest_principal_distance_margin_m",
                "assigned_principal_distance_m",
                "assigned_candidate_rank",
            ],
            "adjudicated_material_components": adjudicated_components,
            "output_area_km2_in_hgm_equal_area_crs": country_area_km2,
            "hgm_workbook_area_km2": EXPECTED_HGM_AREA_TOTAL_KM2,
            "national_area_difference_km2": national_area_difference_km2,
            "national_area_difference_pct": (
                100 * national_area_difference_km2 / EXPECTED_HGM_AREA_TOTAL_KM2
            ),
            "mean_absolute_province_area_difference_pct": mean_absolute_area_difference_pct,
            "maximum_absolute_province_area_difference_pct": maximum_absolute_area_difference_pct,
            "maximum_absolute_province_area_difference": {
                "province_code": str(maximum_area_difference_row["province_code"]),
                "province_name": code_to_name[
                    str(maximum_area_difference_row["province_code"])
                ],
                "difference_pct": float(maximum_area_difference_row["difference_pct"]),
            },
            "province_area_km2_in_hgm_equal_area_crs": source_area_by_code,
            "source_crs_country_province_symmetric_difference_m2": (
                source_coverage_symmetric_difference_m2
            ),
            "wgs84_invalid_before_targeted_repair_count": len(repaired_codes),
            "wgs84_targeted_repair_province_codes": repaired_codes,
            "wgs84_repair_method": (
                "Shapely make_valid(method='structure', keep_collapsed=False), "
                "applied only to invalid geometries after reprojection"
            ),
            "wgs84_roundtrip_repair_area_change_m2": repair_area_change_m2,
            "wgs84_roundtrip_gap_m2": post_repair_gap_m2,
            "wgs84_roundtrip_excess_m2": post_repair_excess_m2,
            "wgs84_roundtrip_pairwise_overlap": overlap_summary,
            "software": {
                "python": platform.python_version(),
                "geopandas": version("geopandas"),
                "shapely": version("shapely"),
                "pyproj": version("pyproj"),
                "pandas": version("pandas"),
                "seven_zip": seven_zip_version(seven_zip),
            },
            "derivation_note": (
                "Every output edge and assignment derives from the pinned HGM 2026 "
                "boundary archive, settlement points and province-area workbook. "
                "Country faces are selected by an exact normalized-WKB hash manifest; "
                "the HGM country-line OBJECTID block is used only to reproduce and "
                "assert that manifest for this pinned snapshot. Principal faces are "
                "labelled by HGM province-capital points. Detached faces use nearest "
                "principal-face distance except for four documented HGM-only "
                "adjudications preserved in the component audit and this metadata."
            ),
            "legal_status": (
                "HGM describes its boundaries as indicative and not legally official; "
                "HGM non-commercial redistribution and attribution terms are retained."
            ),
        }
        args.metadata_output.parent.mkdir(parents=True, exist_ok=True)
        args.metadata_output.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(f"Wrote {args.output} ({output_hash})")
    print(f"Wrote {args.metadata_output}")
    print(f"Wrote {args.country_face_audit_output} ({country_audit_hash})")
    print(f"Wrote {args.component_audit_output} ({component_audit_hash})")
    print(
        f"Validated {len(output_provinces)} provinces; HGM area {country_area_km2:,.6f} "
        f"km2 ({national_area_difference_km2:+.6f} km2 versus workbook)."
    )


if __name__ == "__main__":
    main()
