# Supplementary material

## A due diligence protocol for open geospatial products derived by artificial intelligence applied to Fields of The World in Türkiye

**Companion manuscript:** submitted to *Discover Geoscience*  
**Protocol version:** 1.1.0  
**Analysis snapshot date:** 1 August 2026

This supplement records the protocol derivation, evidence-to-decision crosswalk and
reproducibility contract. Machine-readable analytical results are supplied as CSV rather than
being transcribed into this document. `tables/artifact_manifest.csv` is the authoritative index
of generated tables and figures. This version accompanies the first revision of the
article, prepared in October 2026. The figures added in that revision and the table of their
example sites are indexed separately in `tables/artifact_manifest_revision1.csv` (Section S11).

## S1. What the protocol adds to existing frameworks

The protocol complements rather than replaces the standards and reporting frameworks below.
Its distinct contribution is to convert available producer information and user-side tests into
an explicit decision for a declared use. Incomplete evidence is retained as `indeterminate`; it
is not silently counted as a pass.

| Framework | Primary concern | What it already supplies | Gap addressed by this protocol |
|---|---|---|---|
| [ISO 19157-1:2023](https://www.iso.org/standard/78900.html) | Geographic-data quality | Principles, components, procedures and reporting for evaluating conformance to a product specification | Sequences the evidence from a prospective user's position and connects each result to a use decision |
| [ISO 19131:2022](https://www.iso.org/standard/85092.html) | Geographic-data product specifications | Requirements and guidance for specifying a product so it can be understood and assessed for intended purpose | Tests what happens when the distributed product or documentation is incomplete, ambiguous or internally inconsistent |
| [FAIR principles](https://doi.org/10.1038/sdata.2016.18) | Findability, accessibility, interoperability and reuse | High-level stewardship principles, including identifiers, licences, provenance and domain standards | Distinguishes accessible/reusable data from data demonstrated to be fit for a particular decision |
| [W3C PROV-O](https://www.w3.org/TR/prov-o/) | Provenance representation | A formal representation of entities, activities and agents | Requires provenance claims to resolve to executable inputs, code revisions and evidence artefacts |
| [Model Cards](https://doi.org/10.1145/3287560.3287596) | Model reporting | Intended uses, evaluation conditions, limitations and disaggregated performance | Audits a released geospatial product even when a complete model card is absent and propagates gaps to a user action |
| [Datasheets for Datasets](https://doi.org/10.1145/3458723) and [Data Cards](https://arxiv.org/abs/2204.01075) | Dataset documentation | Motivation, composition, collection/production, recommended uses and limitations | Checks whether documented claims agree with the delivered schema, geometry and spatial population |
| Design-based accuracy assessment | Independent accuracy inference | Sampling designs and estimators for omission, commission and thematic/boundary accuracy | Defines what can be screened before reference data exist and forces `external validation required` when the intended use needs accuracy inference |

The protocol is therefore not an alternative accuracy estimator. It is a pre-validation decision
workflow that determines whether a product may be used provisionally, only under restrictions,
only after external validation, or not at all for the declared purpose.

## S2. Normative evidence and decision model

Every completed record contains:

1. a product version and immutable input identifier;
2. a declared use, risk level, mandatory requirements and prohibited inferences;
3. nine stage records (0–8), each with evidence required, acceptance criterion, observed
   evidence, `pass/fail/indeterminate`, allowed action and evidence artefact identifiers;
4. explicit machine-readable restrictions when the action is conditional; and
5. one final action: `adopt`, `adopt_with_restrictions`,
   `external_validation_required`, or `reject_for_declared_use`.

The normative machine-readable structure is
`protocol/protocol_decision_record.schema.json`. The FTW demonstration is flattened to
`tables/table_0_protocol_decision_record.csv` for publication and inspection. Draft 2020-12
schema validation is followed by semantic rules that check stage outcome/action pairs and
their consistency with the final action.

### S2.1 Audit completeness is not product fitness

A test may be executed successfully while the product fails the use requirement. Conversely,
missing evidence produces an `indeterminate` product-quality result even when the analytical
workflow itself passes. The decision record therefore keeps separate fields for observed
evidence, evidence outcome and permitted action.

### S2.2 Thresholds are use-conditioned

The protocol does not impose universal accuracy, coverage or timeliness thresholds. In a
prospective application, Stage 0 requires these to be declared before examining the product
result. This worked case is a retrospective method demonstration: its decision tolerances are
fully disclosed but were not preregistered and are not empirical error bounds. A low-risk
exploratory use may tolerate incomplete confidence metadata if the missingness is reported; a
rights-affecting eligibility decision cannot. The same product can consequently receive
different actions for different declared uses without contradiction.

## S3. Stage-to-evidence crosswalk for the FTW Türkiye case

| Stage | Decision question | Principal generated evidence | FTW case action |
|---:|---|---|---|
| 0 | What use, risk and evidence requirements govern the decision? | `table_0_protocol_decision_record.csv` | Separate exploratory, quantitative-monitoring and rights-affecting decisions |
| 1 | What product/version/population/target ontology is being evaluated? | product characteristics, schema, annual-layer split and provider-recipe provenance tables, with the pinned feature catalogue for input compositing (Section S11.4) | Restrict interpretation to seasonal/annual target crops; retain recipe ambiguity as an explicit use restriction and record the compositing-window discrepancy |
| 2 | Do administrative attributes agree with spatial scope? | source code counts, deterministic sample audit, exhaustive HGM point-on-surface assignment, provider-to-spatial crosswalk and exception ledger | Preserve provider codes as provenance but use exhaustive spatial assignment for aggregation; exclude points outside the reporting geometry |
| 3 | Are geometries and supplied metrics internally reproducible? | geometry-type/quality, ring-aware area/perimeter spot-check and interior-ring tables | Use supplied metrics only after independent ellipsoidal verification |
| 4 | Are conclusions stable under defensible analytical scenarios? | area-floor sensitivity for distributed, 50, 100, 200, documented 400 and 800 m² scenarios, with model inputs and outputs inside the two largest units (Section S11) | Do not present absolute count or median as threshold-independent |
| 5 | Are rates and reporting units tied to an explicit denominator? | HGM-derived reporting geometry, province lookup, HGM/Natural Earth comparison and region crosswalk | Name total province area as the denominator; do not call the resulting measure agricultural density |
| 6 | What does each quality attribute mean and where is it available? | pinned metadata verification and both-year confidence coverage/sensitivity tables | Do not apply a national confidence filter where approximately 97.3% of records have no value |
| 7 | How stable are different nominal layers in rank and level? | complete-population province comparison, cross-layer metrics, offsets, ratios and size-band decomposition | Treat results as descriptive cross-layer consistency, not change attribution or polygon correspondence; do not attach sampling confidence intervals to the 81-province census |
| 8 | Can a new environment recreate the evidence? | environment table, immutable input digests, notebook, output manifest and review-snapshot manifest | Claim numerical/semantic reproduction at tested tolerances, not byte-identical PDFs; document HGM inputs without redistributing them, and attribute HGM-derived values under HGM's terms |

## S4. FTW target ontology and interpretation boundary

The global-product paper describes FTW as targeting seasonal or annual field crops. Permanent
grassland, pasture, orchards, vineyards, fallow, forestry and other perennial/tree-crop systems
are excluded from its training/evaluation target. Consequently:

- a missing FTW polygon is not evidence that agriculture is absent;
- sparse output in tea-, hazelnut-, orchard- or vineyard-dominated landscapes cannot be called
  omission without an independent annual-crop reference population;
- national sums describe distributed target-class mapped units, not all agricultural land;
- the product cannot be treated as a cadastral, holding, farm, ownership, registry or subsidy
  unit.

This semantic boundary is applied before any regional interpretation.

## S5. Area scenarios, extreme units and topology

The primary characterisation retains the distributed geometry population after exact-WKB
deduplication and administrative-scope reconciliation. Area floors are sensitivity scenarios,
not undocumented corrections to the provider product. The analysis includes 0, 50, 100 and
200 m², the approximately 400 m² four-pixel scenario documented by the product paper, and
800 m².

For every layer, the topology evidence records:

- count and summed-area share in predeclared size bands, including 50, 100, 500 and 1,000 ha;
- maximum area and sensitivity of totals and province rankings to extreme-unit exclusion;
- exact topological duplicates and a declared near-duplicate rule;
- summed provider polygon area and unique union area under a tiled, clipped union procedure;
- overlap difference and computational tile parameters.

Large units are not labelled errors solely because of size. They are treated as a product-risk
stratum whose influence must be visible before a use decision is made.

## S6. Metric verification with interior rings

The initial exterior-ring-only perimeter recomputation was replaced. The revised check uses an
ellipsoidal perimeter that includes exterior and interior rings, after explicitly correcting the
CRS84 longitude–latitude axis order. Exterior-ring length is computed separately with the
ellipsoidal line-length function; assertions require it to be positive, no greater than the
ring-aware total, and equal to that total for polygons without holes. Samples follow a recorded,
deterministic hash ordering. The evidence table separately reports units with interior rings and
all-unit versus hole-bearing-unit ratio summaries. Shape index is interpreted as boundary
complexity including unmapped inclusions, not merely exterior-outline compactness.

## S7. Cross-layer descriptive estimand

The 2024 and 2025 labels are different nominal product layers, not two software releases for an
identical reference period. Province statistics therefore mix possible real annual-crop
difference, imagery/compositing difference, model behaviour and post-processing difference.
The analysis cannot identify those components.

Pearson correlation, Spearman rank correlation, Lin concordance and absolute/relative offsets
are reported separately. Because all 81 reporting provinces are included, these are descriptive
finite-population statistics rather than estimates from an independent random sample. The
pipeline therefore reports no bootstrap confidence interval or significance test. In particular,
non-overlap of separate marginal intervals is not used as a difference test.

## S8. Reproducibility contract

### S8.1 Immutable and versioned inputs

| Input | Identifier used by the workflow |
|---|---|
| FTW Türkiye alpha GeoParquet | S3 object version, 5,907,043,512 bytes, SHA-256 `423c5e780d26c2bfc0a1c84bcf9b68029452be8a0e524a4395fde9c5d745774d` |
| FTW vector metadata | Pinned Git commit recorded in the notebook |
| HGM province-area workbook | SHA-256 `e6054762f2e03e72b56ef85cb430ea00b012ccc5eba3a8fea08e3a631d3b6447` |
| HGM 2026 administrative-boundary archive | SHA-256 `da8efe4dcbe47e5e8a8a34068e1e729832420634b519fab62303b86254471284`; source terms retained |
| Derived HGM 81-province GeoJSON | SHA-256 `ae7734d90958810fae9718322788e2932290a7b7f0a9ab2affca0b3938d8c51e`; HGM-only derivation with an exact 57-of-130 country-face manifest and 353-face province assignment ledger |
| Natural Earth Türkiye Admin-1 extract | Source archive SHA-256 `efc59726337323058f9446210adc96673179cd344e053666ee3d28cb58ba2b05`; local Türkiye GeoJSON SHA-256 `18a5afb0feb78423953fd7d210842cf8876c12d8cbd811b4fe92e64de9275283`; public-domain source |

### S8.2 Reproduction levels

- **Exact:** integer counts, categorical outcomes, input digests and code/data identifiers.
- **Tolerance-tested:** floating-point geodesic, correlation and topology values, using declared
  absolute/relative tolerances.
- **Content-equivalent:** plots and PDFs whose metadata or renderer can change output bytes.

The manuscript does not claim byte-identical PDF regeneration.

### S8.3 Complete non-interactive execution

The review snapshot excludes the large upstream GeoParquet and derived cache. The download
script retrieves the pinned object version and refuses a size or digest mismatch. Because HGM's
terms permit distribution only outside commercial activities, the snapshot also excludes the HGM
source archive/workbook, HGM-derived province geometry and face-level ledgers (Section S8.4). It retains the preparation script, immutable hashes,
source locations and non-spatial derivation description. Recreating the compact derivative therefore
requires lawful local access to the pinned HGM RAR5 archive and workbook, plus 7-Zip. Country and
province component selection uses only the pinned HGM products; Natural Earth is a later public-domain
sensitivity/display source. The notebook uses content-hash cache signatures, fixed source-access
dates, a concise direct-dependency specification, a hash-locked transitive pip resolution and no
gitignored paper-text dependency. The workflow additionally asserts that every provider
bounding box exactly equals its geometry envelope before bounding boxes are used to enumerate
tiles for the national union.

The final complete non-interactive run on 1 August 2026 reused only the cleaned and exhaustive
spatial-assignment caches whose content fingerprints matched the current source and inputs; it
was therefore a complete cache-validated execution, not a zero-cache or from-scratch run. With
Python 3.13.14 and the standard `python3` kernelspec, `nbconvert` exited 0 after 5,350.42 s
(01:29:10.42; user 20,023.35 s, sys 255.14 s). A separate monitor recorded a peak notebook-
kernel RSS of 56,859,568 KiB (54.23 GiB) and VSZ of 89,341,724 KiB (85.20 GiB); these are
kernel-process, not whole-job, peaks. All 17 code cells executed in order without an error or
traceback. The run wrote 80 manifest-controlled artefacts: 69 tables, ten figure files and one
protocol JSON record. The 38,833-byte `tables/artifact_manifest.csv` has SHA-256
`bb43f0c9e7e1a196e89eed0839d29b615dff0988263aa2fd0ea78dab7cbbf957`; every listed path,
size and digest was independently revalidated, and the protocol 1.1.0 record passed both its
Draft 2020-12 schema and cross-stage semantic checks.

### S8.4 Review snapshot

`scripts/build_review_snapshot.sh` creates a deterministic archive with sorted paths, fixed
timestamps, a file-level SHA-256 manifest and an archive SHA-256. The archive contains code,
environment files, protocol schema, derived analytical tables/figures and this supplement,
together with public-domain Natural Earth inputs. It does not contain the 5.9 GB FTW object,
derived cache, HGM inputs or HGM-derived geometry, or spatial face ledgers. The snapshot
submitted with the original manuscript, `ftw-turkiye-review-snapshot-2026-08-01-r1.tar.gz`,
also contained the manuscript sources and the compiled manuscript PDF. It passed its internal
manifest validation and two consecutive builds produced byte-identical archives.

For the first revision the snapshot was rebuilt as
`ftw-turkiye-review-snapshot-2026-10-28-r2.tar.gz`, which is Online Resource 1 of the revised
article. It also contains the revision-figure script and its requirements, the TikZ
source of the workflow diagram, the revision figures, `tables/table_r1_example_sites.csv` and
`tables/artifact_manifest_revision1.csv`. The manuscript sources and the compiled manuscript
were removed from the repository at this revision because the journal holds the article, so
they are not part of this snapshot. Every file listed in either manifest is checked for
size and SHA-256 before packaging. The cached Zarr windows are not included, but their digests are
recorded in the example-site table (Section S11.3). Two consecutive builds of the revised
snapshot again produced byte-identical archives. Each archive's external `.sha256` sidecar
carries its release digest so that the archive does not contain a self-referential checksum.

### S8.5 HGM terms of use and HGM-derived content

HGM publishes both the *Türkiye Mülki İdare Sınırları* boundary product and the *İl ve İlçe Yüz
Ölçümleri* province-area workbook free of charge. The terms on the boundary-product page were
checked on 27 October 2026 and are translated here from Turkish. They state that the product is
free of charge and that HGM retains copyright. Any user may use ("fair use") and distribute the
product outside commercial activities, and HGM must be cited as the source whenever the product
is used or distributed.

The same page states that the boundaries are derived for display purposes from various sources
and that neither they nor any data derived from them have official status. The determination
and publication of administrative boundaries is governed by Law No. 5442. The area page carries
the same statement on official status.

This study uses the HGM products within those terms. The analysis is non-commercial scholarly
research, and HGM is cited wherever HGM-derived values appear. The HGM archive, the workbook,
the derived province geometry and the face-level ledgers are not redistributed, and the
published figures draw province outlines only from public-domain Natural Earth boundaries.

The published HGM-derived content consists of analytical results. These are province
assignments of FTW mapped units, counts and areas aggregated by HGM-derived province or region,
statistics computed from those aggregates, and rates that use HGM province areas as
denominators. The HGM area values needed to document those denominators are published alongside
them. These values remain subject to HGM's terms, which the repository licences do not replace.
They appear in the following files and parts of the article.

- The province and region aggregates are `tables/table_3_province_metrics_2024.csv`,
  `tables/table_s5_province_metrics_all_layers.csv` and `tables/table_s7_region_metrics_2024.csv`
  (also with HGM-area denominators), `tables/table_s9_province_confidence_coverage_2024_2025.csv`,
  `tables/table_s12_province_cross_layer_comparison_wide.csv`,
  `tables/table_s_province_cross_layer_ratios.csv`,
  `tables/table_s_province_summed_area_rank_cap_sensitivity.csv`,
  `tables/table_s_province_summed_area_rank_cap_sensitivity_summary.csv`,
  `tables/table_s_zero_count_provinces_by_layer.csv` and the province-level statistics in
  `tables/table_5_cross_layer_consistency_2024_2025.csv`.
- The province of individual units and the assignment audit are recorded in
  `tables/table_s14_largest_polygons_by_layer.csv`,
  `tables/table_s_provider_to_spatial_subdivision_crosswalk.csv`,
  `tables/table_s_spatial_assignment_exceptions.csv`,
  `tables/table_s_spatial_assignment_candidate_multiplicity.csv`,
  `tables/table_s_subdivision_spatial_assignment_summary.csv`,
  `tables/table_s_subdivision_code_reconciliation.csv`,
  `tables/table_s_subdivision_reassignment_ids.csv`,
  `tables/table_s_subdivision_reassignment_summary.csv`,
  `tables/table_s_hgm_vs_natural_earth_assignment_crosswalk.csv` and
  `tables/table_s_hgm_vs_natural_earth_assignment_summary.csv`.
- `tables/table_s_province_area_denominator_comparison.csv` compares the published and derived
  HGM province areas.
- In the article, Fig. 6 (province statistics and the panel (b) denominator), Table 8 and Fig. 8
  (province-level cross-layer statistics) carry an HGM credit in their captions. The choice of
  example site T also depends on HGM-derived province assignments (Section S11.2).

Natural Earth assignments and equal-area denominators are reported alongside as a public-domain
sensitivity, so every HGM-dependent quantity has a documented alternative.

The decision record generated on 1 August 2026 (`protocol/ftw_turkiye_decision_record.json`)
lists the restriction "Do not redistribute HGM-dependent material through a commercial publisher
until written rights clearance". Its stage 8 record states that public redistribution of the
HGM-derived reporting geometry requires written permission or user-supplied derivation. This
revision applies both statements to the HGM files and the HGM-derived geometry. These are not
distributed with the article or the repository, and users derive them locally from the HGM
products. The HGM-derived analytical values listed above are published with attribution under
HGM's terms. The generated record is left unchanged so that its digest in
`tables/artifact_manifest.csv` remains valid.

## S9. Remaining inferential limits

These limits are also stated in the Limitations subsection of the main text. The expanded audit
resolves internal consistency and reproducibility questions; it does not create independent
ground truth. The case still cannot estimate omission, commission, boundary accuracy or annual
agricultural change. Generalisation of the protocol beyond this product and country also remains
to be tested by independent users and additional product classes. These gaps are carried into
the final decision instead of being treated as passed stages.

## S10. File and naming conventions

- Main analytical tables use `table_0` through `table_5` prefixes.
- Detailed evidence tables use `table_s...` prefixes and are indexed by
  `tables/artifact_manifest.csv`.
- Cross-layer outputs use `cross_layer`, not `annual_layer_agreement` or `inter_version`.
- Figures and axes use `mapped unit`, not `field`, except when describing the provider's stated
  target class.
- Each table contains units in column names or a unit field and avoids mixing counts, shares and
  areas without an explicit label.
- Outputs added in the first revision use `fig_r1_` and `table_r1_` prefixes and are indexed by
  `tables/artifact_manifest_revision1.csv`.
- File numbers predate the numbering of the revised article. Article Figs. 1, 2, 3 and 5 are
  `fig_r1_protocol_workflow`, `fig_r1_study_area`, `fig_r1_ftw_multiscale` and
  `fig_r1_visual_examples`. Article Figs. 4, 6, 7 and 8 are `fig_1_national_area_distribution`,
  `fig_2_spatial_patterns_2024`, `fig_3_confidence_2024_2025` and
  `fig_4_cross_layer_consistency_2024_2025`. Article Tables 5–9 draw on `table_1` (dataset and
  processing), `table_2` (national summary), `table_4` (confidence), `table_5` (cross-layer
  consistency) and `table_0` (decision record). The complete province table `table_3` underlies
  panels (a) and (b) of Fig. 6.

The artifact manifests written by the final notebook execution and by the revision-figure script
supersede any file listing in a draft of this supplement.

## S11. Figures added in the first revision

Four figures were added in response to the reviewers. They show the protocol workflow (article
Fig. 1), the study area (Fig. 2), the model inputs and outputs at three nested scales (Fig. 3)
and visual examples at four sites (Fig. 5). They are generated outside the analysis notebook, so
no notebook output and no entry of `tables/artifact_manifest.csv` changed. The figures are visual
illustrations and do not constitute an accuracy assessment.

### S11.1 Sources

`scripts/make_revision_figures.py` uses the dependencies listed in
`scripts/requirements-revision-figures.txt` and reads four kinds of input.

- The pinned FTW Türkiye GeoParquet, after its size and SHA-256 are verified (Section S8.1).
- The Sentinel-2 planting and harvest composites that FTW publishes as model input, from the
  Zarr V3 store `https://data.source.coop/ftw/global-data/features/zarr/alpha/global.zarr`.
- The PRUE class probabilities for field interior, field boundary and background, from
  `https://data.source.coop/ftw/global-data/predictions/zarr/alpha/global.zarr`.
- Natural Earth province and country outlines, together with the province lookup, province
  metrics, density grid and largest-unit tables generated by the notebook.

Both Zarr stores are published by Fields of The World under CC BY 4.0. They were read on
27 October 2026 and share one longitude and latitude grid with a cell size of 8.98 × 10⁻⁵
degrees (about 10 m). The composites are shown as true-colour images from bands B04, B03 and
B02, although the model also uses B08. The national map uses the 64x overview of the probability store (about
640 m), the regional window of Fig. 3 uses its 4x overview (about 40 m), and all other windows
use the full-resolution arrays. Figures that show composites carry the attribution "Contains
modified Copernicus Sentinel data (2024) processed by Fields of The World". The workflow diagram
is drawn in TikZ from `figures/src/fig_r1_protocol_workflow.tex` and uses no data.

No HGM file or geometry is read. The only HGM-dependent inputs are the province ranking used to
choose site T (Section S11.2) and the province labels of units M1 and M2 in
`table_s14_largest_polygons_by_layer.csv`, which agree with the Natural Earth outlines.

### S11.2 Example sites

Each site is chosen by a deterministic rule. Ties between grid cells are broken by the lower
longitude index and then the lower latitude index.

| Site | Rule | Location | Selected feature |
|---|---|---|---|
| T, typical annual cropland | Among 0.1° cells whose centre lies inside the Natural Earth outline of Konya, the cell with the most 2024 units of 1–10 ha, assigning units by bounding-box centre. Konya is the province with the largest 2024 summed mapped area in `table_3_province_metrics_2024.csv`, whose province assignment is HGM-derived (Section S8.5) | 31.65° E, 38.25° N, Konya | 1,417 units of 1–10 ha in the cell |
| M1, largest unit | Interior point farthest from any ring of the 2024 unit ranked first by provider area in `table_s14_largest_polygons_by_layer.csv` | 33.5304° E, 38.5548° N, Aksaray | Unit of 34,895 ha with 288 interior rings, with the point 4.78 km from the nearest ring |
| M2, second-largest unit | As for M1, for the unit ranked second | 31.5186° E, 38.8577° N, Afyonkarahisar | Unit of 17,391 ha with 2,240 interior rings, with the point 1.35 km from the nearest ring |
| F, densest cell | The 0.1° cell with the most 2024 mapped units in `table_s13_density_grid_2024.csv` | 28.35° E, 38.15° N, İzmir | 19,464 units in the cell |

The provider `id` is not unique within a layer, so units M1 and M2 are retrieved from the
GeoParquet by identifier and bounding box together. Their windows lie wholly inside the unit and
contain none of its rings, so every pixel shown belongs to that single mapped unit.

### S11.3 Data windows and checksums

`tables/table_r1_example_sites.csv` records the rule and location of each site. For every window
read from the Zarr stores it also records the bounds, the store and overview, the SHA-256 of the
cached array and the access date. The stores are versioned only by data release (alpha), so these
digests are the record of exactly which values were plotted. The cached arrays are not
distributed. A rerun reads the windows again from the public stores, and its digests can be
compared with the recorded ones.

### S11.4 Documentation discrepancy on input compositing

The product paper sets the planting and harvest windows for each Sentinel-2 tile from WorldCereal
crop calendars. The pinned feature catalogue instead describes medians of approximately five to
ten quality-masked scenes selected by latitude-based day-of-year heuristics. This is the second
discrepancy between the product documents recorded at Stage 1, after the polygonisation recipe
(argmax and connected components in the paper, a softmax threshold of 0.5 in the Source
Cooperative documentation). The article records it under Stage 1, in its product table and in
its Limitations. The figures show the composites as published and do not depend on which
description is correct.

### S11.5 Interpretation

Inside units M1 and M2 the model predicts field interior without any boundary over surfaces that
show no field pattern in the input composites. These units are therefore more consistent with
non-target land mapped as a single unit than with merged crop fields (article Section 7.2). This
reading is visual and is not an accuracy assessment. Only reference data can establish what the
units contain.

### S11.6 Reproduction

    python -m pip install -r scripts/requirements-revision-figures.txt
    bash data/download_tr.sh
    (cd figures/src && pdflatex fig_r1_protocol_workflow.tex && cp fig_r1_protocol_workflow.pdf ..)
    python scripts/make_revision_figures.py

The workflow diagram is compiled first because the script also lists it in
`tables/artifact_manifest_revision1.csv`. The manifest records the size and SHA-256 of each
revision output together with the SHA-256 of the script or TikZ source that produced it. Plots
are reproduced at the content-equivalent level of Section S8.2 and are not expected to match
byte for byte.
