#!/usr/bin/env bash
set -euo pipefail

# Build a tar.gz bundle with non-Python assets that are not shipped via PyPI.
# This tarball can be uploaded to the FlowMason website and downloaded
# by the runtime via FLOWMASON_ASSETS_URL / DEFAULT_ASSETS_URL_TEMPLATE.
#
# Usage:
#   ./scripts/build_extra_assets_tar.sh 1.0.17
#
# The script will create:
#   dist/flowmason-extra-assets-<version>.tar.gz
#
# and, if ../flowmason-website/public exists, also copy it to:
#   ../flowmason-website/public/downloads/

VERSION="${1:-}"

if [[ -z "${VERSION}" ]]; then
  echo "Usage: $0 <version>"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
ASSETS_NAME="flowmason-extra-assets-${VERSION}.tar.gz"
ASSETS_PATH="${DIST_DIR}/${ASSETS_NAME}"

mkdir -p "${DIST_DIR}"

cd "${ROOT_DIR}"

echo "Building extra assets tarball: ${ASSETS_PATH}"

tar -czf "${ASSETS_PATH}" \
  --exclude='node_modules' \
  --exclude='dist' \
  demos \
  examples \
  manualtesting \
  mobile \
  kubernetes \
  vscode-extension \
  studio/frontend

echo "Created ${ASSETS_PATH}"

WEBSITE_PUBLIC="${ROOT_DIR}/../flowmason-website/public"
if [[ -d "${WEBSITE_PUBLIC}" ]]; then
  mkdir -p "${WEBSITE_PUBLIC}/downloads"
  cp "${ASSETS_PATH}" "${WEBSITE_PUBLIC}/downloads/${ASSETS_NAME}"
  echo "Copied to website public downloads: ${WEBSITE_PUBLIC}/downloads/${ASSETS_NAME}"
else
  echo "Website public directory not found at ${WEBSITE_PUBLIC}, skipping copy."
fi

