# A due diligence protocol for open geospatial products derived by artificial intelligence applied to Fields of The World in Türkiye

Reproducibility materials for:

> Bıçakçı, Y. S. A due diligence protocol for open geospatial products derived by artificial
> intelligence applied to Fields of The World in Türkiye. Submitted to *Discover Geoscience* in
> August 2026 and revised in October 2026.

The article was submitted under the title "A use-conditioned due-diligence protocol for open
AI-derived geospatial products: Application to Fields of The World in Türkiye".

Department of Artificial Intelligence and Machine Learning, Faculty of Applied Sciences,
Marmara University, Istanbul, Türkiye.
ORCID [0000-0002-7288-9959](https://orcid.org/0000-0002-7288-9959).

**What this repository does and does not contain.** It contains the executable workflow, the
pinned environment, the protocol schema and decision record, and every generated table and
figure, each indexed by SHA-256 in `tables/artifact_manifest.csv`. It deliberately does not
redistribute third-party source material. The Turkish General Directorate of Mapping (HGM)
boundary archive, area workbook, derived province geometry and face-level ledgers are excluded
because HGM permits attributed, non-commercial reuse of material it describes as indicative
rather than legally official. The 5.9 GB Fields of The World country partition and the derived
analysis caches are excluded because of their size. In each case the retrieval location,
immutable identifier and local derivation instructions are documented in
`data/external/README.md`, so that the analysis can be rebuilt by anyone who obtains those
inputs under their own terms. The article itself is held by the journal and is not part of this
repository.

`ftw_turkiye_eda.ipynb` is the top-level executable workflow. Its calculations also use
`helpers.py`, the pinned inputs and the documented HGM preparation script; generated CSVs are
the authoritative source for numbers reported in the article.

## Licences

The analysis code is licensed under the GNU General Public License v3.0; see
[`LICENSE-CODE`](LICENSE-CODE). Project documentation and authored tables and figures are
CC BY 4.0; see [`LICENSE`](LICENSE).
The upstream FTW data remain CC BY 4.0, and every third-party input described under
`data/external/` retains its own terms. HGM publishes its boundary product and province-area
workbook free of charge and permits their use and distribution outside commercial activities
with attribution. It describes both as indicative and without legal official status. Neither is
redistributed here. Natural Earth is public domain; it is used as an independent
generalized-boundary sensitivity and for figure display only. Published figures contain no
HGM-derived boundary geometry, although some plotted values use HGM assignment or HGM area
denominators and credit HGM accordingly. The tables that contain HGM-derived values are listed
in Section S8.5 of `supplementary_material.md`. Those values remain subject to HGM's
terms, which the repository licences do not replace.

## Scope

FTW targets seasonal/annual crop fields. Permanent grassland, pasture, orchards,
vineyards, fallow, forestry, and perennial/tree crops are outside the declared target
ontology. Its polygons are AI-detected remote-sensing mapped units; they are **not**
cadastral or legal parcels, holdings, farms, ownership units, or ÇKS records. Comparing
the prediction layers is a cross-layer consistency analysis, **not**
agricultural-change inference. No independent ground-truth validation is undertaken here.

One property of the product bears on every result. The FTW benchmark spans 24 countries and
Türkiye is not among them, and the global map was validated against reference boundaries in
24 countries — with full-country evaluation in only Austria, Latvia and Finland — none of
them Türkiye. No country-specific independent evaluation is therefore reported for the
Türkiye partition, and its geographic-transfer performance remains uncharacterised.

The vector confidence value is a provider-derived cell-level reliability value, sampled at a
polygon point on surface and rescaled from the underlying scale. A **null means no value
outside modelled-confidence coverage, not a low score**. Both 2024 and 2025 coverage are
reported; neither layer supports a national confidence filter. The schema carries no
raw-probability field.

Robinson et al. (2026) describes a three-class argmax followed by connected components for
field extraction; the Source Cooperative README instead describes thresholding softmax output
before polygonisation. The notebook pins both, records the unresolved ambiguity, and
characterises the polygons as distributed. The input compositing is also described
inconsistently. The paper sets the planting and harvest windows from WorldCereal crop calendars, whereas
the pinned feature catalogue describes latitude-based day-of-year windows (Section S11.4 of
`supplementary_material.md`).

## Reproduce

The recommended tested path is a Python 3.13 virtual environment with the hash-locked
transitive dependency set. Rebuilding the restricted HGM derivative additionally requires a system installation of
`7zz` or `7z` with RAR5 support (or an explicit path passed to the preparation script):

    python3.13 -m venv .venv && . .venv/bin/activate
    python -c 'import sys; assert sys.version_info[:2] == (3, 13)'
    python -m pip install --require-hashes -r requirements-lock.txt

As a convenience alternative, Conda users may run:

    conda env create -f environment.yml && conda activate ftw-tr-eda

`requirements.txt` is the concise direct-dependency specification;
`requirements-lock.txt` is the generated, hash-locked transitive resolution used for a clean
pip installation. `environment.yml` pins the direct Conda dependencies but is not a transitive
`conda-lock` file, so the two installation paths are not claimed to have identical solver
resolutions.

Lawfully obtain the external administrative inputs described in
`data/external/README.md`, including the HGM boundary archive and area workbook, and run
`scripts/prepare_hgm_provinces.py` to rebuild the compact HGM derivative. That script verifies
the documented source digests before use. Then download the Türkiye partition (~5.9 GB) when
absent and run the notebook. The
download script requests the pinned S3 version and verifies both its 5,907,043,512-byte
length and SHA-256 digest before installing it:

    bash data/download_tr.sh
    jupyter lab ftw_turkiye_eda.ipynb

Or non-interactively:

    jupyter nbconvert --to notebook --execute --inplace \
      --ExecutePreprocessor.kernel_name=python3 \
      --ExecutePreprocessor.timeout=-1 ftw_turkiye_eda.ipynb

The standard `python3` kernelspec is installed inside either environment by the
pinned `ipykernel` dependency, so the non-interactive command does not depend on a
user-global Jupyter kernelspec.

The first run writes content-fingerprinted GeoParquet caches under `data/interim/`: one
after exact-WKB deduplication and one after exhaustive point-on-surface assignment to the
pinned, island-complete HGM-derived 81-province geometry. Original provider subdivision
codes are preserved for the full crosswalk but are not used for aggregation. Natural Earth
is evaluated as a boundary-framework sensitivity and supplies generalized display outlines.
MD5 accelerates duplicate grouping, but every repeated digest must pass an exact WKB byte-
equality collision guard before removal. The primary characterization has no
analyst-imposed area floor; 0, 50, 100, 200, 400, and 800 m² scenarios are exported
separately. The raw extract and caches are excluded from version control and regenerated by
the steps above. The final complete non-interactive execution on 1 August 2026 used Python
3.13.14 and content-fingerprint-validated cleaned and spatial-assignment caches. It exited 0
after 5,350.42 s (01:29:10.42; user 20,023.35 s, sys 255.14 s). The monitored notebook kernel
reached a peak RSS of 56,859,568 KiB (54.23 GiB) and peak VSZ of 89,341,724 KiB (85.20 GiB);
these are kernel-process measurements, not whole-job peaks. DuckDB spilled while computing the
exhaustive tiled national unions.

## Outputs

Four main figures and one supplementary diagnostic, each as PNG and PDF:

1. National mapped-unit area distribution and cumulative concentration.
2. Province median area, province density, and national density grid.
3. Both-layer non-null confidence distributions and the explicitly labelled 2024
   grid-cell coverage snapshot.
4. Province-level cross-layer correspondence.
5. Supplementary outline audit of the four largest mapped units in each layer.

File numbers predate the revised article, so figures 1–4 above are article Figs. 4, 6, 7 and 8.
Article Figs. 1, 2, 3 and 5 are the revision figures described below.

Five main tables: dataset and processing characteristics; national summary and
area-threshold shares; complete province metrics; both-layer confidence coverage and
sensitivity; cross-layer consistency.

Supplementary CSVs record schema, exact-WKB collision/attribute-conflict audits, and exhaustive geometry checks; the full provider-to-HGM
province crosswalk, exclusions, and HGM-versus-Natural-Earth sensitivity; ring-aware
area/perimeter verification; 0/50/100/200/400/800 m² sensitivity; outlier bands and cap
sensitivity; exact national unique mapped surface from non-overlapping 0.1° tile unions;
selected-cell overlap and near-duplicate diagnostics; confidence provenance and spatial
coverage for both layers; denominator provenance; and descriptive province- and 0.1°
grid-level cross-layer correspondence. Cross-layer quantities are finite-population
descriptive statistics; no bootstrap interval or significance claim is attached to them.
`tables/table_0_protocol_decision_record.csv` records the actual pass/fail/indeterminate
decision at stages 0–8. `protocol/ftw_turkiye_decision_record.json` is the corresponding
machine-readable record, validated during execution against the Draft 2020-12 schema.
Cross-stage outcome/action and final-decision consistency is then checked by explicit
semantic decision rules.
`tables/artifact_manifest.csv` inventories all 80 current generated artefacts (69 tables,
10 figure files and one protocol JSON record) by SHA-256 and deliberately excludes its own
self-referential hash. The 38,833-byte manifest has SHA-256
`bb43f0c9e7e1a196e89eed0839d29b615dff0988263aa2fd0ea78dab7cbbf957`; an independent check
matched all 80 paths, sizes and hashes.

### Figures added in the first revision

`scripts/make_revision_figures.py` builds the study-area map, the multiscale figure of model
inputs and outputs, and the visual examples. It reads the pinned GeoParquet (and verifies its
SHA-256), the tables above, Natural Earth, and windows of two Zarr V3 stores that Fields of The
World publishes under CC BY 4.0. One store holds the Sentinel-2 planting and harvest composites
(`features/zarr/alpha/global.zarr`) and the other the PRUE class probabilities
(`predictions/zarr/alpha/global.zarr`). The example sites are chosen by deterministic rules,
which are recorded together with the SHA-256 of every data window in
`tables/table_r1_example_sites.csv`. The protocol workflow diagram is drawn in TikZ
(`figures/src/fig_r1_protocol_workflow.tex`). All revision outputs are indexed in
`tables/artifact_manifest_revision1.csv`, and the original manifest above is unchanged.

    python -m pip install -r scripts/requirements-revision-figures.txt
    bash data/download_tr.sh
    (cd figures/src && pdflatex fig_r1_protocol_workflow.tex && cp fig_r1_protocol_workflow.pdf ..)
    python scripts/make_revision_figures.py

The diagram is compiled first because the script also lists it in the revision manifest. The
remote stores are versioned only by data release (alpha), so the cached window digests are the
record of exactly which values were plotted. The figures are visual illustrations and do
not constitute an accuracy assessment. Section S11 of `supplementary_material.md` gives the sources,
the site-selection rules and the documentation discrepancy found while preparing them.

### Review snapshot (Online Resource 1)

`scripts/build_review_snapshot.sh` writes a deterministic, rights-minimised archive of this
repository to `release/`. It is tested on Linux with Bash 4 or newer, GNU tar and GNU
coreutils. It normalises locale, time zone, permissions, ownership, path order and timestamps.
It also validates both artifact manifests and the code and input provenance, stops if the
notebook is still running, and verifies the internal snapshot manifest before writing the
archive. Staleness of generated outputs is decided by their SHA-256 digests. Modification times
are not used because a fresh clone resets them.

    bash scripts/build_review_snapshot.sh

The snapshot submitted with the original manuscript,
`ftw-turkiye-review-snapshot-2026-08-01-r1.tar.gz`, passed two consecutive byte-identity
builds. The revised snapshot, `ftw-turkiye-review-snapshot-2026-10-28-r2.tar.gz`, adds the
revision figures, their script and the two revision tables. Unlike the first snapshot, it does
not contain the manuscript. It also passed two consecutive byte-identity builds. Each archive's external `.sha256` sidecar records its release digest
without creating a self-reference inside the archive.

## Data sources

- FTW Global Data alpha, Source Cooperative, CC BY 4.0 — https://source.coop/ftw/global-data
- FTW Sentinel-2 planting and harvest composites and PRUE class probabilities (Zarr, CC BY 4.0,
  used only for the revision figures) at
  https://data.source.coop/ftw/global-data/features/zarr/alpha/global.zarr and
  https://data.source.coop/ftw/global-data/predictions/zarr/alpha/global.zarr. Contains modified
  Copernicus Sentinel data.
- Provider catalog metadata (vector-confidence semantics) — https://data.source.coop/ftw/global-data/catalog.json
- Provider README — https://data.source.coop/ftw/global-data/README.md
- Natural Earth Admin 1, public domain — https://www.naturalearthdata.com
- HGM Türkiye Mülki İdare Sınırları, attribution/non-commercial, indicative — https://www.harita.gov.tr/urun/turkiye-mulki-idare-sinirlari/232
- Turkish General Directorate of Mapping province areas — https://www.harita.gov.tr/il-ve-ilce-yuzolcumleri
- Turkish Statistical Institute Agricultural Holdings Structure Survey, 2016 — https://veriportali.tuik.gov.tr/en/press/24869

For scholarly use, cite Robinson et al. (2026) for the global map, Kerner et al. (2025) for
the benchmark, Muhawenayo et al. (2026) for PRUE, and Corley et al. (2026) for the Field
Guide, together with the Source Cooperative product documentation.

## Layout

    ftw_turkiye_eda.ipynb      analysis and output generator
    helpers.py                 geometry, grid, concordance, and XLSX helpers
    supplementary_material.md  supplementary material (Sections S1–S11)
    protocol/                  JSON Schema and validated FTW decision record
    scripts/                   HGM preparation, review-snapshot and revision-figure helpers
    data/download_tr.sh        immutable country-partition download helper
    data/external/             Natural Earth extracts and third-party input provenance
    data/raw/                  large immutable FTW extract (gitignored)
    data/interim/              content-fingerprinted analysis caches (gitignored)
    figures/                   generated figures
    figures/src/               TikZ source of the workflow diagram
    tables/                    generated tables and the SHA-256 artifact manifest
