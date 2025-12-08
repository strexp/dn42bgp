#!/bin/bash
set -e

REGISTRY_DIR="${HOME}/registry"
DATA_DIR="data"
CACHE_DIR="cache"

if [ -e "$REGISTRY_DIR" ]; then
    (cd "$REGISTRY_DIR" && git pull)
else
    REPO_URL="https://git.dn42.dev/dn42/registry"
    if [ ! -z "$1" ]; then
        REPO_URL="https://git:$1@git.dn42.dev/dn42/registry"
    fi
    git clone "$REPO_URL" "$REGISTRY_DIR" --depth 1 --single-branch
fi

mkdir -p "$DATA_DIR" "$CACHE_DIR"

echo "Downloading route data..."
wget -q "https://github.com/isjerryxiao/rushed_dn42_map/blob/pages/parsed.jsonl.bz2?raw=true" -O "$CACHE_DIR/table.jsonl.bz2"

echo "Running Python generator..."
python3 main.py

echo "Running Registry Wizard..."
mkdir -p "$DATA_DIR/registry"
WIZARD_JAR="wizard/RegistryWizard.jar"

if [ -f "$WIZARD_JAR" ]; then
    java -jar "$WIZARD_JAR" "$REGISTRY_DIR" hierarchicalPrefixes v4 true > "$DATA_DIR/registry/prefix.4.json"
    java -jar "$WIZARD_JAR" "$REGISTRY_DIR" hierarchicalPrefixes v6 > "$DATA_DIR/registry/prefix.6.json"
    java -jar "$WIZARD_JAR" "$REGISTRY_DIR" inetnumMetadata v4 true > "$DATA_DIR/registry/meta.4.json"
    java -jar "$WIZARD_JAR" "$REGISTRY_DIR" inetnumMetadata v6 > "$DATA_DIR/registry/meta.6.json"
else
    echo "Warning: $WIZARD_JAR not found, skipping wizard steps."
fi

echo "Done."
