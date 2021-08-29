#!/bin/bash

[ -e ~/registry ] && (cd ~/registry; git pull) || git clone https://git:$1@git.dn42.dev/dn42/registry ~/registry --depth 1 --single-branch

mkdir -p data

wget https://github.com/isjerryxiao/rushed_dn42_map/blob/pages/parsed.jsonl.bz2?raw=true -O data/table.jsonl.bz2

python3 main.py

rm -f data/table.jsonl.bz2
rm -rf data/table

mkdir -p data/registry
java -jar wizard/RegistryWizard.jar ~/registry hierarchicalPrefixes v4 true > data/registry/prefix.4.json
java -jar wizard/RegistryWizard.jar ~/registry hierarchicalPrefixes v6 > data/registry/prefix.6.json
java -jar wizard/RegistryWizard.jar ~/registry inetnumMetadata v4 true > data/registry/meta.4.json
java -jar wizard/RegistryWizard.jar ~/registry inetnumMetadata v6 > data/registry/meta.6.json
