#!/usr/bin/env bash
# Moves the keeper's machine to another signed keeper image, by digest, and runs
# the keeper once so the result shows at once instead of at the next timer tick.
# Check the digest's signature first (cosign verify, see the README); this script
# only moves the pin. The old keeper.env is kept beside it, so moving back is the
# same script with the old digest.
#
# usage, on the keeper's machine as the keeper's user:
#   move-keeper-image.sh sha256:<64 hex>
# exit: 1 bad digest, 2 the pull failed, 3 the keeper run failed.
set -euo pipefail

digest="${1:?usage: move-keeper-image.sh sha256:<64 hex>}"
[[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]] || { echo "move-keeper-image: not a sha256 digest: $digest" >&2; exit 1; }

env_file="$HOME/fovea-keeper/keeper.env"
image="ghcr.io/macula-io/mcl-fovea-keeper@$digest"

podman pull --quiet "$image" >/dev/null || { echo "move-keeper-image: could not pull $image" >&2; exit 2; }

old="$(/bin/grep -o 'sha256:[0-9a-f]*' "$env_file" || true)"
[ -z "$old" ] || cp "$env_file" "$env_file.bak-${old:7:8}"
printf 'KEEPER_IMAGE=%s\n' "$image" > "$env_file.new"
mv "$env_file.new" "$env_file"
echo "move-keeper-image: ${old:-none} -> $digest"

systemctl --user start fovea-keeper.service || {
  echo "move-keeper-image: the keeper run failed; journalctl --user -u fovea-keeper.service" >&2
  exit 3
}
echo "move-keeper-image: the keeper ran on $digest"
