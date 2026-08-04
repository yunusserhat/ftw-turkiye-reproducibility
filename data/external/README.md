# External administrative reference data

## Turkish General Directorate of Mapping surface areas

`il_ilce_alanlari_2026_hgm.xlsx` is the province and district surface-area workbook
published by the Turkish General Directorate of Mapping and accessed on 18 July 2026.
The notebook verifies its SHA-256 digest before use:

`e6054762f2e03e72b56ef85cb430ea00b012ccc5eba3a8fea08e3a631d3b6447`

- Source page: https://www.harita.gov.tr/il-ve-ilce-yuzolcumleri
- Basis: areas calculated from the 2026 1:1,000,000 administrative map
- Province rows: 81
- Province-area total: 780,043 km²
- Role: primary denominator for mapped-unit density

The workbook states that its boundaries and calculated areas are indicative and do not
have legal official status. It also states that legal responsibility for determining
and publishing administrative boundaries rests with the Ministry of Interior under
Law No. 5442. The analysis preserves that qualification.

## HGM 2026 administrative-boundary linework

`hgm_turkiye_mulki_idare_sinirlari_2026.rar` is the 2026 HGM *Türkiye Mülki
İdare Sınırları* product downloaded on 31 July 2026. Its fixed SHA-256 digest is:

`da8efe4dcbe47e5e8a8a34068e1e729832420634b519fab62303b86254471284`

- Product page: https://www.harita.gov.tr/urun/turkiye-mulki-idare-sinirlari/232
- Archive contents used: country-boundary lines, province-boundary lines and
  province-capital/settlement points
- Role: primary reporting geometry for exhaustive point-on-surface assignment

The source product contains linework, not 81 ready-made province polygons.
`scripts/prepare_hgm_provinces.py` verifies the archive and workbook digests, extracts
the RAR5 archive with 7-Zip, polygonizes the HGM country and province linework, labels
principal faces from HGM province-capital points, and writes complete face-level
selection and assignment ledgers. The derivation uses HGM inputs only; Natural Earth
is a later sensitivity/display source and no external administrative geometry selects
or labels an HGM component.

The HGM country-line layer contains Turkish and neighbouring-country faces but omits
the country-name field described by its XML metadata. For this pinned 2026 archive,
all positive-length boundary contributors with source `OBJECTID` at most 60 discover
57 of 130 polygonized faces. Because `OBJECTID` is an internal sequence rather than a
semantic contract, the discovery result is frozen as an exact 57-face normalized-WKB
SHA-256 manifest. The script requires the discovery set to equal that manifest, covers
all 1,003 HGM settlement points, and fails closed for any later archive. This audit
includes Garip Adası (source `OBJECTID` 32), which a previous auxiliary mask omitted.
The resulting HGM-linework area is 780,043.008572 km², only +0.008572 km²
(+0.00000110%) from the independent HGM workbook total of 780,043 km².

The selected country union and HGM province lines produce 353 province faces. HGM
province-capital points label 81 principal faces. Minimum source-CRS distance to those
principal faces, with province-code tie-breaking, assigns 52 other material faces and
216 microscopic line-network faces. Four water-separated material faces are explicitly
adjudicated to Çanakkale or İstanbul from HGM district points, island-cluster geometry
and province-area reconciliation. Every face records the nearest and second-nearest
principal code, distance, margin, selected candidate rank, settlement evidence and any
override rationale. Garip Adası is assigned to İzmir by the nearest-principal rule.

The source-CRS province union has zero symmetric difference from the selected HGM
country faces. After WGS84 reprojection, structure-preserving validity repair is
applied only to 12 invalid geometries. Equal-area round-trip diagnostics record
44.020 m² of gap, 0.768 m² total pairwise overlap and a −43.252 m² repair-area
change, all negligible relative to the 780,043 km² reporting surface and retained
in metadata.

The deterministic outputs are:

- `hgm_2026_province_boundaries_wgs84.geojson`: 81 valid province geometries,
  SHA-256 `ae7734d90958810fae9718322788e2932290a7b7f0a9ab2affca0b3938d8c51e`
- `hgm_2026_province_boundaries_metadata.json`: derivation and validation record,
  SHA-256 `1600d96c750efda2bc8a87549986f9a0aafd9cfe6eaa7432c2d0492a17f8e829`
- `hgm_2026_country_face_selection_audit.csv`: all 130 country-face decisions,
  SHA-256 `e50c816dd53195f1ee63e02d9f4298b0ffddad6c280f15fee119b55177c8aa39`
- `hgm_2026_component_assignment_audit.csv`: all 353 province-face decisions,
  SHA-256 `bddd8887bc1e135eb39a1a78141669d0d9d4b638959914526ca0d6b5e9bed3d9`
- `scripts/prepare_hgm_provinces.py`: deterministic derivation,
  SHA-256 `1b086807ad90c577e9acf138099320fc9b0e22101834f8412cf922ece87d8405`

Mean absolute province-area difference from the workbook is 0.01163%; the maximum
is 0.11704% (Yalova). Two repository runs and one unrelated temporary-directory run
reproduced all four output files byte for byte. The published workbook values remain
the primary density denominators.

HGM states that this product is indicative rather than legally official and permits
free use and distribution outside commercial activities with attribution. These source
terms are not replaced by this repository's licences. This repository therefore does not
redistribute the HGM archive, the area workbook, the derived province GeoJSON or the
spatial face ledgers. Obtain them from the HGM product pages above under HGM's terms,
verify them against the SHA-256 digests recorded here, and rebuild the derivative with
`scripts/prepare_hgm_provinces.py`, which fails closed on any digest mismatch.

## Natural Earth provinces

`ne_10m_admin_1_turkiye.geojson` is the 81-feature Türkiye subset of Natural Earth
Admin 1 States and Provinces at 1:10m scale. The notebook recreates it from the
upstream archive if it is absent.

- Source: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-1-states-provinces/
- Pinned archive URL: https://naturalearth.s3.amazonaws.com/10m_cultural/ne_10m_admin_1_states_provinces.zip
- Pinned archive SHA-256: `efc59726337323058f9446210adc96673179cd344e053666ee3d28cb58ba2b05`
- Türkiye Admin-1 derivative SHA-256: `18a5afb0feb78423953fd7d210842cf8876c12d8cbd811b4fe92e64de9275283`
- Türkiye display-boundary derivative SHA-256: `478432047dbc06c6d99112b08adb596b2cd045cd76711b9e3f3d9c9f386e89a3`
- Source release label: not supplied by the upstream archive; identity is pinned by URL and hash
- Licence: public domain
- Join key: `iso_3166_2`, consisting of `TR-` and the two-digit province code
- Roles: public-domain map display and a quantitative boundary-source sensitivity
  comparison

Natural Earth is not the primary province-density denominator in the revised analysis.
It is also not the primary spatial-assignment boundary. The two country-boundary
GeoJSON files are retained for the national density-map outline.
