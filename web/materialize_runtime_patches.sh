#!/bin/sh
# RETIRED by the canonical UI pipeline (docs/architecture/gsf-canonical-ui.md).
#
# This script used to replay the V285–V373 legacy migration chain over the UI
# at build time. The materialized result is now committed as the canonical
# source, so replaying migrations would overwrite current UI files with older
# versions. It fails on purpose if anything tries to run it again.
echo "materialize_runtime_patches.sh is retired: the repository UI files are canonical; do not replay legacy migrations" >&2
exit 1
