#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
export TZ=UTC
umask 022

# Build a deterministic, rights-minimised review snapshot.  In addition to the
# 5.9 GB FTW input and analysis caches, this archive deliberately excludes HGM
# source/derived geometry and any obsolete auxiliary boundary-audit geometry.
# HGM identifiers and lawful local-derivation instructions remain in the included
# documentation; the source/derived files require separate rights clearance.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
SNAPSHOT_VERSION="${FTW_SNAPSHOT_VERSION:-2026-08-01-r1}"
if [[ ! "${SNAPSHOT_VERSION}" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ || \
      "${SNAPSHOT_VERSION}" == *'..'* ]]; then
    printf 'Unsafe snapshot version: %s\n' "${SNAPSHOT_VERSION}" >&2
    exit 1
fi
RELEASE_DIR="${PROJECT_ROOT}/release"
ARCHIVE_NAME="ftw-turkiye-review-snapshot-${SNAPSHOT_VERSION}.tar.gz"
ARCHIVE_PATH="${RELEASE_DIR}/${ARCHIVE_NAME}"
STAGING_DIR="$(mktemp -d)"
STAGING_ROOT="${STAGING_DIR}/ftw-turkiye-review-snapshot-${SNAPSHOT_VERSION}"

if (( BASH_VERSINFO[0] < 4 )); then
    printf 'Bash 4 or newer is required.\n' >&2
    exit 1
fi
if ! tar --version 2>/dev/null | head -n 1 | grep -q 'GNU tar'; then
    printf 'GNU tar is required for deterministic archive metadata.\n' >&2
    exit 1
fi
command -v python >/dev/null

cleanup() {
    rm -rf -- "${STAGING_DIR}"
}
trap cleanup EXIT

mkdir -p "${STAGING_ROOT}" "${RELEASE_DIR}"

require_path() {
    local relative_path="$1"
    if [[ ! -e "${PROJECT_ROOT}/${relative_path}" ]]; then
        printf 'Refusing to build an incomplete snapshot; missing: %s\n' \
            "${relative_path}" >&2
        exit 1
    fi
}

for required_path in \
    requirements-lock.txt ftw_turkiye_eda.ipynb \
    protocol/protocol_decision_record.schema.json \
    protocol/ftw_turkiye_decision_record.json \
    tables/artifact_manifest.csv tables/table_0_protocol_decision_record.csv \
    tables/table_1_dataset_extract_processing.csv \
    tables/table_2_national_summary_2024_2025.csv \
    tables/table_3_province_metrics_2024.csv \
    tables/table_4_confidence_coverage_sensitivity_2024_2025.csv \
    tables/table_5_cross_layer_consistency_2024_2025.csv \
    figures/fig_1_national_area_distribution.pdf \
    figures/fig_2_spatial_patterns_2024.pdf \
    figures/fig_3_confidence_2024_2025.pdf \
    figures/fig_4_cross_layer_consistency_2024_2025.pdf \
    manuscript/ftw_turkiye.pdf \
    manuscript/ftw_turkiye.tex manuscript/sn-bibliography.bib \
    manuscript/sn-jnl.cls manuscript/bst/sn-basic.bst \
    manuscript/TEMPLATE_PROVENANCE.md manuscript/supplementary_material.md; do
    require_path "${required_path}"
done

if pgrep -f '[n]bconvert.*ftw_turkiye_eda\.ipynb' >/dev/null; then
    printf 'Refusing to snapshot while the analysis notebook is executing.\n' >&2
    exit 1
fi

validate_artifact_manifest() {
    local validation_root="$1"
    local manifest="${validation_root}/tables/artifact_manifest.csv"
    local header relative_path artifact_type expected_size expected_sha remainder
    local artifact_path actual_size actual_sha candidate candidate_relative
    declare -A listed=()

    IFS= read -r header < "${manifest}"
    if [[ "${header}" != path,artifact_type,size_bytes,sha256,* ]]; then
        printf 'Unexpected artifact-manifest schema: %s\n' "${header}" >&2
        exit 1
    fi

    while IFS=, read -r relative_path artifact_type expected_size expected_sha remainder; do
        expected_sha="${expected_sha%$'\r'}"
        case "${relative_path}" in
            tables/*.csv|figures/*.png|figures/*.pdf|protocol/ftw_turkiye_decision_record.json) ;;
            *)
                printf 'Unsafe or unexpected artifact-manifest path: %s\n' \
                    "${relative_path}" >&2
                exit 1
                ;;
        esac
        if [[ "${relative_path}" == *'..'* || "${relative_path}" == /* ]]; then
            printf 'Unsafe artifact-manifest path: %s\n' "${relative_path}" >&2
            exit 1
        fi
        artifact_path="${validation_root}/${relative_path}"
        if [[ ! -f "${artifact_path}" ]]; then
            printf 'Artifact manifest references a missing file: %s\n' \
                "${relative_path}" >&2
            exit 1
        fi
        actual_size="$(stat -c '%s' "${artifact_path}")"
        actual_sha="$(sha256sum "${artifact_path}" | cut -d' ' -f1)"
        if [[ "${actual_size}" != "${expected_size}" || \
              "${actual_sha}" != "${expected_sha}" ]]; then
            printf 'Artifact differs from its manifest entry: %s\n' \
                "${relative_path}" >&2
            exit 1
        fi
        listed["${relative_path}"]=1
    done < <(tail -n +2 "${manifest}")

    while IFS= read -r -d '' candidate; do
        candidate_relative="${candidate#${validation_root}/}"
        if [[ -z "${listed[${candidate_relative}]+x}" ]]; then
            printf 'Generated artifact is absent from the manifest: %s\n' \
                "${candidate_relative}" >&2
            exit 1
        fi
    done < <(
        find "${validation_root}/tables" -maxdepth 1 -type f -name '*.csv' \
            ! -name 'artifact_manifest.csv' -print0
        find "${validation_root}/figures" -maxdepth 1 -type f \
            \( -name '*.png' -o -name '*.pdf' \) -print0
        printf '%s\0' "${validation_root}/protocol/ftw_turkiye_decision_record.json"
    )
}

validate_manifest_provenance() {
    local validation_root="$1"
    python - "${validation_root}" <<'PY'
import csv
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()
manifest = root / "tables" / "artifact_manifest.csv"
with manifest.open(newline="", encoding="utf-8") as stream:
    rows = list(csv.DictReader(stream))
if not rows:
    raise SystemExit("Artifact manifest has no data rows")

provenance_columns = {
    "source_input_sha256": "423c5e780d26c2bfc0a1c84bcf9b68029452be8a0e524a4395fde9c5d745774d",
    "helpers_sha256": hashlib.sha256((root / "helpers.py").read_bytes()).hexdigest(),
    "requirements_lock_sha256": hashlib.sha256(
        (root / "requirements-lock.txt").read_bytes()
    ).hexdigest(),
    "protocol_schema_sha256": hashlib.sha256(
        (root / "protocol" / "protocol_decision_record.schema.json").read_bytes()
    ).hexdigest(),
    "fixed_source_access_date": "2026-07-18",
    "fixed_hgm_area_access_date": "2026-07-18",
    "fixed_hgm_boundary_access_date": "2026-07-31",
}

notebook = json.loads((root / "ftw_turkiye_eda.ipynb").read_text(encoding="utf-8"))
source_only = [
    {
        "cell_type": cell.get("cell_type"),
        "source": (
            "".join(cell.get("source", []))
            if isinstance(cell.get("source", []), list)
            else cell.get("source", "")
        ),
    }
    for cell in notebook.get("cells", [])
]
payload = json.dumps(
    source_only, ensure_ascii=False, sort_keys=True, separators=(",", ":")
).encode("utf-8")
provenance_columns["analysis_notebook_source_sha256"] = hashlib.sha256(payload).hexdigest()

for column, expected in provenance_columns.items():
    observed = {row.get(column) for row in rows}
    if observed != {expected}:
        raise SystemExit(
            f"Artifact-manifest provenance mismatch for {column}: {sorted(observed)}"
        )

with (root / "tables" / "table_s0_code_source_provenance.csv").open(
    newline="", encoding="utf-8"
) as stream:
    code_rows = list(csv.DictReader(stream))
observed_code_hashes = {row["path"]: row["sha256"] for row in code_rows}
expected_code_hashes = {
    "ftw_turkiye_eda.ipynb": provenance_columns["analysis_notebook_source_sha256"],
    "helpers.py": provenance_columns["helpers_sha256"],
    "requirements-lock.txt": provenance_columns["requirements_lock_sha256"],
    "scripts/prepare_hgm_provinces.py": hashlib.sha256(
        (root / "scripts" / "prepare_hgm_provinces.py").read_bytes()
    ).hexdigest(),
    "protocol/protocol_decision_record.schema.json": provenance_columns[
        "protocol_schema_sha256"
    ],
}
if observed_code_hashes != expected_code_hashes:
    raise SystemExit(
        "Code-source provenance differs from packaged sources: "
        f"observed={observed_code_hashes!r} expected={expected_code_hashes!r}"
    )

from jsonschema import Draft202012Validator, FormatChecker

schema = json.loads(
    (root / "protocol" / "protocol_decision_record.schema.json").read_text(
        encoding="utf-8"
    )
)
record = json.loads(
    (root / "protocol" / "ftw_turkiye_decision_record.json").read_text(
        encoding="utf-8"
    )
)
Draft202012Validator(schema, format_checker=FormatChecker()).validate(record)
stages = record["stages"]
if [stage["stage_id"] for stage in stages] != list(range(9)):
    raise SystemExit("Protocol stages are not the ordered 0-8 sequence")
for stage in stages:
    if stage["outcome"] in {"fail", "indeterminate"} and stage["allowed_action"] == "continue":
        raise SystemExit(f"Non-pass stage continues without restriction: {stage['stage_id']}")
    if stage["allowed_action"] == "stop" and stage["outcome"] != "fail":
        raise SystemExit(f"Stop action without failed outcome: {stage['stage_id']}")
if any(stage["allowed_action"] == "stop" for stage in stages):
    if record["final_action"] != "reject_for_declared_use":
        raise SystemExit("A stop stage requires reject_for_declared_use")
if any(stage["allowed_action"] == "external_validation_required" for stage in stages):
    if record["final_action"] not in {"external_validation_required", "reject_for_declared_use"}:
        raise SystemExit("Stage-level external validation is inconsistent with final action")
if record["final_action"] == "adopt_with_restrictions" and not record["restrictions"]:
    raise SystemExit("Restricted adoption has no machine-readable restrictions")
PY
}

validate_artifact_manifest "${PROJECT_ROOT}"
validate_manifest_provenance "${PROJECT_ROOT}"

if find "${PROJECT_ROOT}/tables" "${PROJECT_ROOT}/figures" \
    "${PROJECT_ROOT}/protocol/ftw_turkiye_decision_record.json" \
    -type f -newer "${PROJECT_ROOT}/tables/artifact_manifest.csv" \
    ! -path "${PROJECT_ROOT}/tables/artifact_manifest.csv" -print -quit \
    | grep -q .; then
    printf 'Generated outputs are newer than artifact_manifest.csv; rerun the notebook.\n' >&2
    exit 1
fi

for manuscript_dependency in \
    manuscript/ftw_turkiye.tex manuscript/sn-bibliography.bib \
    manuscript/sn-jnl.cls manuscript/bst/sn-basic.bst \
    figures/fig_1_national_area_distribution.pdf \
    figures/fig_2_spatial_patterns_2024.pdf \
    figures/fig_3_confidence_2024_2025.pdf \
    figures/fig_4_cross_layer_consistency_2024_2025.pdf; do
    if [[ "${PROJECT_ROOT}/${manuscript_dependency}" \
          -nt "${PROJECT_ROOT}/manuscript/ftw_turkiye.pdf" ]]; then
        printf 'Compiled manuscript PDF is stale relative to: %s\n' \
            "${manuscript_dependency}" >&2
        exit 1
    fi
done

copy_path() {
    local relative_path="$1"
    if [[ -e "${PROJECT_ROOT}/${relative_path}" ]]; then
        mkdir -p "${STAGING_ROOT}/$(dirname "${relative_path}")"
        cp -a "${PROJECT_ROOT}/${relative_path}" "${STAGING_ROOT}/${relative_path}"
    fi
}

for relative_path in \
    README.md LICENSE LICENSE-CODE requirements.txt requirements-lock.txt environment.yml \
    ftw_turkiye_eda.ipynb helpers.py data/download_tr.sh \
    data/raw/ftw_catalog_summary.json data/external/README.md \
    data/external/ne10m_turkiye_boundary_wgs84.geojson \
    data/external/ne_10m_admin_1_turkiye.geojson \
    protocol/README.md protocol/protocol_decision_record.schema.json \
    scripts/build_review_snapshot.sh scripts/prepare_hgm_provinces.py \
    tables/artifact_manifest.csv \
    manuscript/ftw_turkiye.tex manuscript/ftw_turkiye.pdf \
    manuscript/sn-bibliography.bib manuscript/TEMPLATE_PROVENANCE.md \
    manuscript/supplementary_material.md \
    manuscript/revision_change_log.md; do
    copy_path "${relative_path}"
done

while IFS=, read -r relative_path _; do
    copy_path "${relative_path}"
done < <(tail -n +2 "${PROJECT_ROOT}/tables/artifact_manifest.csv")

# Fail closed if a future edit accidentally adds a restricted boundary payload.
for restricted_basename in \
    hgm_turkiye_mulki_idare_sinirlari_2026.rar \
    il_ilce_alanlari_2026_hgm.xlsx \
    hgm_2026_province_boundaries_wgs84.geojson \
    hgm_2026_province_boundaries_metadata.json \
    hgm_2026_country_face_selection_audit.csv \
    hgm_2026_component_assignment_audit.csv \
    geoboundaries_tur_adm0_2021.geojson \
    geoboundaries_tur_adm1_2021.geojson; do
    if find "${STAGING_ROOT}" -type f -name "${restricted_basename}" -print -quit \
        | grep -q .; then
        printf 'Refusing to package restricted boundary file: %s\n' \
            "${restricted_basename}" >&2
        exit 1
    fi
done

validate_artifact_manifest "${STAGING_ROOT}"
validate_manifest_provenance "${STAGING_ROOT}"

find "${STAGING_ROOT}" -type f \
    ! -name 'SNAPSHOT_MANIFEST.sha256' -print0 \
    | sort -z \
    | xargs -0 sha256sum \
    | sed "s#${STAGING_ROOT}/##" \
    > "${STAGING_ROOT}/SNAPSHOT_MANIFEST.sha256"

(
    cd "${STAGING_ROOT}"
    sha256sum --check --strict SNAPSHOT_MANIFEST.sha256
)

tar --sort=name \
    --mtime='UTC 2026-08-01 00:00:00' \
    --owner=0 --group=0 --numeric-owner \
    --mode='u+rwX,go+rX,go-w' \
    -C "${STAGING_DIR}" \
    -cf - "$(basename "${STAGING_ROOT}")" \
    | gzip -n > "${ARCHIVE_PATH}"

sha256sum "${ARCHIVE_PATH}" > "${ARCHIVE_PATH}.sha256"
printf 'Created %s\n' "${ARCHIVE_PATH}"
cat "${ARCHIVE_PATH}.sha256"
