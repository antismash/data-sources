#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

tail +2 rufO.tsv | cut -d"	" -f5 | xargs nad --molecule protein --format fasta -o rufO.faa
