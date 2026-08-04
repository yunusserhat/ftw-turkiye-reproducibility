# Supplementary material

## A use-conditioned due-diligence protocol for open AI-derived geospatial products: Fields of The World over Türkiye

**Companion manuscript:** `ftw_turkiye.tex`  
**Protocol version:** 1.1.0
**Analysis snapshot date:** 1 August 2026

This supplement records the protocol derivation, evidence-to-decision crosswalk and
reproducibility contract. Machine-readable analytical results are supplied as CSV rather than
being transcribed into this document. `tables/artifact_manifest.csv` is the authoritative index
of generated tables and figures.

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
| 1 | What product/version/population/target ontology is being evaluated? | product characteristics, schema, annual-layer split and provider-recipe provenance tables | Restrict interpretation to seasonal/annual target crops; retain recipe ambiguity as an explicit use restriction |
| 2 | Do administrative attributes agree with spatial scope? | source code counts, deterministic sample audit, exhaustive HGM point-on-surface assignment, provider-to-spatial crosswalk and exception ledger | Preserve provider codes as provenance but use exhaustive spatial assignment for aggregation; exclude points outside the reporting geometry |
| 3 | Are geometries and supplied metrics internally reproducible? | geometry-type/quality, ring-aware area/perimeter spot-check and interior-ring tables | Use supplied metrics only after independent ellipsoidal verification |
| 4 | Are conclusions stable under defensible analytical scenarios? | area-floor sensitivity for distributed, 50, 100, 200, documented 400 and 800 m² scenarios | Do not present absolute count or median as threshold-independent |
| 5 | Are rates and reporting units tied to an explicit denominator? | HGM-derived reporting geometry, province lookup, HGM/Natural Earth comparison and region crosswalk | Name total province area as the denominator; do not call the resulting measure agricultural density |
| 6 | What does each quality attribute mean and where is it available? | pinned metadata verification and both-year confidence coverage/sensitivity tables | Do not apply a national confidence filter where approximately 97.3% of records have no value |
| 7 | How stable are different nominal layers in rank and level? | complete-population province comparison, cross-layer metrics, offsets, ratios and size-band decomposition | Treat results as descriptive cross-layer consistency, not change attribution or polygon correspondence; do not attach sampling confidence intervals to the 81-province census |
| 8 | Can a new environment recreate the evidence? | environment table, immutable input digests, notebook, output manifest and review-snapshot manifest | Claim numerical/semantic reproduction at tested tolerances, not byte-identical PDFs; keep HGM redistribution permission as an external publication condition |

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
script retrieves the pinned object version and refuses a size or digest mismatch. Until written
HGM rights clearance is obtained, the rights-minimised snapshot also excludes the HGM source archive/workbook, HGM-derived
province geometry and face-level ledgers. It retains the preparation script, immutable hashes,
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
environment files, protocol schema, derived analytical tables/figures, manuscript sources and
the compiled manuscript PDF, together with public-domain Natural Earth inputs. It does not
contain the 5.9 GB FTW object, derived cache, HGM inputs or derivatives, spatial face ledgers,
or the locally installed Springer Nature class/bibliography-style files. Template provenance
and tested hashes are supplied separately. HGM describes its boundary product as indicative, non-official
and freely usable or distributable outside commercial activity with attribution. Those terms are not
replaced by the repository licences. Because the reported tables also depend on HGM spatial
assignment and area denominators, written clearance for a commercial-publisher or unrestricted
public workflow should expressly cover those analytical derivatives, not only the source and
boundary files. Until then the generated archive is rights-minimised, not rights-cleared.
The final `ftw-turkiye-review-snapshot-2026-08-01-r1.tar.gz` passed its internal
manifest validation and two consecutive builds produced byte-identical archives. Its external
`.sha256` sidecar carries the release digest so that the archive does not contain a
self-referential checksum.
Before journal submission, the author must obtain written clearance covering HGM-derived
publication content, deposit the resulting rights-cleared immutable snapshot in Zenodo or an
institutional repository, and add its DOI or persistent link to the manuscript and submission
record.

## S9. Remaining inferential limits

The expanded audit resolves internal consistency and reproducibility questions; it does not
create independent ground truth. The case still cannot estimate omission, commission, boundary
accuracy or annual agricultural change. Generalisation of the protocol beyond this product and
country also remains to be tested by independent users and additional product classes. These
gaps are carried into the final decision instead of being treated as passed stages.

## S10. File and naming conventions

- Main analytical tables use `table_0` through `table_5` prefixes.
- Detailed evidence tables use `table_s...` prefixes and are indexed by
  `tables/artifact_manifest.csv`.
- Cross-layer outputs use `cross_layer`, not `annual_layer_agreement` or `inter_version`.
- Figures and axes use `mapped unit`, not `field`, except when describing the provider's stated
  target class.
- Each table contains units in column names or a unit field and avoids mixing counts, shares and
  areas without an explicit label.

The artifact manifest produced by the final notebook execution supersedes any file listing in a
draft of this supplement.
