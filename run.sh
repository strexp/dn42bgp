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
wget -q "https://mrt42.strexp.net/master4_latest.mrt.bz2" -O "$CACHE_DIR/master4.mrt.bz2"
wget -q "https://mrt42.strexp.net/master6_latest.mrt.bz2" -O "$CACHE_DIR/master6.mrt.bz2"

echo "Running Python generator..."
python3 main.py

echo "Running Registry Wizard..."
mkdir -p "$DATA_DIR/registry"
mkdir -p "$DATA_DIR/roa"

WIZARD="wizard/registry_wizard"

if [ ! -f "$WIZARD" ]; then
    mkdir -p wizard
    curl -sL https://github.com/Kioubit/dn42_registry_wizard/releases/download/v0.4.15/dn42_registry_wizard_v0.4.15_x86_64-unknown-linux-musl.tar.gz | tar xz -C wizard
fi

if [ -f "$WIZARD" ]; then
    $WIZARD "$REGISTRY_DIR" roa json > "$DATA_DIR/roa/roa.json"
    $WIZARD "$REGISTRY_DIR" roa v4 > "$DATA_DIR/roa/bird.4.list"
    $WIZARD "$REGISTRY_DIR" roa v6 > "$DATA_DIR/roa/bird.6.list"
    
    $WIZARD "$REGISTRY_DIR" hierarchical_prefixes v4 > "$DATA_DIR/registry/prefix.4.json"
    $WIZARD "$REGISTRY_DIR" hierarchical_prefixes v6 > "$DATA_DIR/registry/prefix.6.json"
    
    $WIZARD "$REGISTRY_DIR" object_metadata inetnum > "$DATA_DIR/registry/meta.4.json"
    $WIZARD "$REGISTRY_DIR" object_metadata inet6num > "$DATA_DIR/registry/meta.6.json"
else
    echo "Warning: $WIZARD not found, skipping wizard steps."
fi

echo "Done."
