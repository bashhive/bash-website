#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
rm -rf dist
mkdir -p dist

cp -R \
  index.html \
  robots.txt \
  sitemap.xml \
  favicon.ico \
  apple-touch-icon.png \
  icon-192.png \
  bash-logo.png \
  bashhive-favicon-64.png \
  bashhive-logo.png \
  bashhive-logo.svg \
  bashhive-mark-512.png \
  bashhive-mark.svg \
  bash-heritage-lockup.svg \
  hivesec-mark.svg \
  hivesec-seal.svg \
  dist/

if [[ -d alerts ]]; then
  cp -R alerts dist/
fi
