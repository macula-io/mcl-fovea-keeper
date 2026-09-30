#!/bin/sh
# keep: one keeper run, the image's entrypoint. Brings the records clone up to
# date, fetches every slot in the keeper's configuration, and commits and pushes
# what it kept. Everything it runs is in this image; the records repository it
# works on is data only.
#
#   /records                     a clone of mcl-fovea-records (read-write)
#   /etc/fovea-keeper/keeper.json   what to fetch (local config, read-only)
#   /etc/fovea-keeper/deploy_key    the key that writes only the records repo
#   /etc/fovea-keeper/known_hosts   GitHub's pinned host key
#
# Exits non-zero when the keeper or the push fails, after committing whatever
# the run logged, so a failure is loud and its fetch log line is still kept.
set -eu
conf=/etc/fovea-keeper
export GIT_SSH_COMMAND="ssh -i $conf/deploy_key -o IdentitiesOnly=yes -o UserKnownHostsFile=$conf/known_hosts -o StrictHostKeyChecking=yes"
git config --global user.name "fovea keeper"
git config --global user.email "fovea-keeper@users.noreply.github.com"
git config --global --add safe.directory /records

cd /records
git pull --quiet --ff-only
mkdir -p records endorsements
git clone --quiet https://github.com/macula-io/mcl-fovea-assessments.git /tmp/assessments
status=0
keeper -config "$conf/keeper.json" -root . -fovea fovea -assessments /tmp/assessments || status=$?

git add -- records endorsements
if ! git diff --cached --quiet; then
  git commit --quiet -m "keep: $(date -u +%Y-%m-%dT%H:%MZ)"
  pushed=0
  for attempt in 1 2 3; do
    if git push --quiet; then pushed=1; break; fi
    git pull --quiet --rebase
  done
  [ "$pushed" = 1 ] || { echo "keep: push failed after 3 attempts" >&2; status=1; }
fi
[ "$status" = 0 ] || echo "keep: the run failed (exit $status); see the fetch logs" >&2
exit "$status"
