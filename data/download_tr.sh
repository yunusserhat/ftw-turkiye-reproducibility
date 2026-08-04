#!/usr/bin/env bash
set -euo pipefail

# Download only the immutable Türkiye country-partition object.  The S3 version ID,
# byte length, and SHA-256 digest identify the exact input used by the analysis.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESTINATION="${SCRIPT_DIR}/raw/ftw_turkiye.parquet"
TEMPORARY_FILE="${DESTINATION}.part"
OBJECT_URL="https://s3.us-west-2.amazonaws.com/us-west-2.opendata.source.coop/tge-labs/ftw-global-data/predictions/vectors/alpha/results-by-admin-conf/admin:country_code=TR/T%C3%BCrkiye.parquet"
VERSION_ID="xenG_6E1OYHASAduQdF4GQVAaWhx9Z.S"
URL="${OBJECT_URL}?versionId=${VERSION_ID}"
EXPECTED_SIZE_BYTES="5907043512"
EXPECTED_SHA256="423c5e780d26c2bfc0a1c84bcf9b68029452be8a0e524a4395fde9c5d745774d"

verify_file() {
    local file_path="$1"
    local observed_size
    local observed_sha256
    observed_size="$(stat --format='%s' "${file_path}")"
    observed_sha256="$(sha256sum "${file_path}" | cut -d ' ' -f 1)"
    [[ "${observed_size}" == "${EXPECTED_SIZE_BYTES}" ]] || {
        printf 'Size mismatch for %s: expected %s, observed %s\n' \
            "${file_path}" "${EXPECTED_SIZE_BYTES}" "${observed_size}" >&2
        return 1
    }
    [[ "${observed_sha256}" == "${EXPECTED_SHA256}" ]] || {
        printf 'SHA-256 mismatch for %s: expected %s, observed %s\n' \
            "${file_path}" "${EXPECTED_SHA256}" "${observed_sha256}" >&2
        return 1
    }
}

mkdir -p "$(dirname "${DESTINATION}")"
if [[ -f "${DESTINATION}" ]] && verify_file "${DESTINATION}"; then
    printf 'Verified existing immutable input %s\n' "${DESTINATION}"
    exit 0
fi

trap 'rm -f "${TEMPORARY_FILE}"' EXIT
curl --fail --location --retry 3 --retry-delay 2 --output "${TEMPORARY_FILE}" "${URL}"
verify_file "${TEMPORARY_FILE}"
mv "${TEMPORARY_FILE}" "${DESTINATION}"
trap - EXIT
printf 'Downloaded and verified %s (S3 version %s)\n' "${DESTINATION}" "${VERSION_ID}"
