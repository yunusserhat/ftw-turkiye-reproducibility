# Springer Nature LaTeX template provenance

The manuscript uses the publisher-supplied `sn-jnl` document class with the
`sn-basic` bibliography style. These template files retain their own publisher
and LaTeX Project Public License notices, are not relicensed by this
repository, and are not redistributed here.

This repository and the rights-minimised review snapshot both carry the
authored `.tex`/`.bib` sources but deliberately exclude the template class and
bibliography-style files. To compile the sources, obtain the current
official Springer Nature LaTeX authoring template through the
[Earth Science Informatics submission guidelines](https://link.springer.com/journal/12145/submission-guidelines)
and place `sn-jnl.cls` and `sn-basic.bst` on the TeX search path.

The locally tested template files used for the 1 August 2026 verification were:

- `sn-jnl.cls`: SHA-256
  `36d0c3273a59d48dc6a9c7b080dfa1ec50dc10229d8751568d1f2e490ffa5ecc`
- `sn-basic.bst`: SHA-256
  `4b368414cc5593169907933b417aacfdb0ce905866a39bdf55d21aad65e9d46c`

These hashes document the tested local build inputs; they do not replace the
publisher's current template or grant redistribution rights.

## Tested PDF build

The final verification uses Tectonic 0.16.9 with its cached default bundle v33:

- Tectonic binary SHA-256:
  `397efac4cabf7dfa02f238fe23681215b535ea665e99ba27d123b8bc655b88cb`
- bundle URL: `https://relay.fullyjustified.net/default_bundle_v33.tar`
- cached bundle identity:
  `6ffe055852f8faf66c0acbe1a7fb27f87b869a90bad1204f3bf4d9683f597c7c`
- build command from `manuscript/`:
  `tectonic -C --keep-logs ftw_turkiye.tex`

The `-C` flag makes the verification fail rather than fetch an unrecorded TeX
resource. The engine and bundle are build inputs, not redistributed project
files, and PDF byte identity is not claimed across different TeX toolchains.
