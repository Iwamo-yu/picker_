#!/usr/bin/env bash
# Re-fetch public reference files. Run on a machine with normal internet access.
# Pinned commits are the ones inspected on 2026-09-25 (see docs/source_manifest.md).
set -euo pipefail
cd "$(dirname "$0")"
clone() { [ -d "$2" ] || git clone https://github.com/$1.git "$2"; git -C "$2" checkout -q "$3"; }
clone grexai/SpheroidPicker SpheroidPicker f1204766fe9577ebac20df356853093fb6dbabd8
clone grexai/AutomaticSpheroidPickerSoftware AutomaticSpheroidPickerSoftware 0058bd90ad957e2e645e25817c286b0539485ab4
mkdir -p zenodo standards manuals
# Blocked in the authoring session - fetch manually/with wider network policy:
curl -L -o zenodo/14679243.json https://zenodo.org/api/records/14679243 || true
curl -L -o zenodo/16536353.json https://zenodo.org/api/records/16536353 || true
for n in 1-2004_FootprintDimensions 2-2004_HeightDimensions 4-2004_WellPositions; do
  curl -L -o standards/ANSI_SLAS_$n.pdf "https://www.slas.org/SLAS/assets/File/public/standards/ANSI_SLAS_$n.pdf" || true; done
curl -L -o manuals/AX8157_13_IX73_INST_E.pdf https://adobeassets.evidentscientific.com/content/dam/mis/ix73/manuals/AX8157_13_IX73_INST_E.pdf || true
curl -L -o standards/Corning_7007.pdf https://certs-ecatalog.corning.com/life-sciences/product-descriptions/7007.pdf || true
echo "Zenodo files: see zenodo/*.json -> files[].links.self"
