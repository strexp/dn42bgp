#!/bin/bash
set -e

export DN42_REGISTRY="${DN42_REGISTRY:-$HOME/registry}"
DATA_DIR="./data"
CACHE_DIR="./cache"

if [ -e "$DN42_REGISTRY" ]; then
    echo "Updating registry at $DN42_REGISTRY..."
    (cd "$DN42_REGISTRY" && git pull)
else
    REPO_URL="https://git.dn42.dev/dn42/registry"
    if [ ! -z "$1" ]; then
        REPO_URL="https://git:$1@git.dn42.dev/dn42/registry"
    fi
    git clone "$REPO_URL" "$DN42_REGISTRY" --single-branch
fi

echo "Downloading route data..."
mkdir -p "$CACHE_DIR"

wget -q "https://mrt42.strexp.net/master4_latest.mrt.bz2" -O "$CACHE_DIR/master4.mrt.bz2"
wget -q "https://mrt42.strexp.net/master6_latest.mrt.bz2" -O "$CACHE_DIR/master6.mrt.bz2"

echo "Running Python generator..."
python3 main.py

echo "Running Registry Wizard..."
mkdir -p "$DATA_DIR/registry" "$DATA_DIR/roa" "wizard"

WIZARD="wizard/registry_wizard"

if [ ! -f "$WIZARD" ]; then
    curl -f -L https://github.com/Kioubit/dn42_registry_wizard/releases/download/v0.4.15/dn42_registry_wizard_v0.4.15_x86_64-unknown-linux-musl.tar.gz | tar xz -C wizard
    chmod +x "$WIZARD"
fi

if [ -x "$WIZARD" ]; then
    "$WIZARD" "$DN42_REGISTRY" roa json > "$DATA_DIR/roa/roa.json"
    "$WIZARD" "$DN42_REGISTRY" roa v4 > "$DATA_DIR/roa/bird.4.list"
    "$WIZARD" "$DN42_REGISTRY" roa v6 > "$DATA_DIR/roa/bird.6.list"
    
    "$WIZARD" "$DN42_REGISTRY" hierarchical_prefixes v4 > "$DATA_DIR/registry/prefix.4.json"
    "$WIZARD" "$DN42_REGISTRY" hierarchical_prefixes v6 > "$DATA_DIR/registry/prefix.6.json"
    
    "$WIZARD" "$DN42_REGISTRY" object_metadata inetnum > "$DATA_DIR/registry/meta.4.json"
    "$WIZARD" "$DN42_REGISTRY" object_metadata inet6num > "$DATA_DIR/registry/meta.6.json"
else
    echo "Warning: $WIZARD not found, skipping wizard steps."
fi

echo "Done."
