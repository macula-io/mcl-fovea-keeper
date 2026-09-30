# mcl-fovea-keeper

*This exists so that anyone can check, at any time, that fovea's security verdicts about the Macula fleet were made continuously and not only when convenient.*

The keeper fetches fovea's signed observations from the mesh every 15 minutes, keeps every record the released `fovea verify` accepts, logs every fetch with its time, and commits the result to [mcl-fovea-records](https://github.com/macula-io/mcl-fovea-records), which holds data only. What a kept record proves, and what the keeper's own gaps look like, is in that repository's README and in [macula-fovea spec v0.5, 15-observations](https://github.com/macula-io/macula-fovea/blob/main/spec/v0.5/15-observations.md).

## What is here

| Path | What |
| --- | --- |
| `main.go` | The keeper: one run fetches every slot, keeps new records `fovea verify` accepts (refused ones apart), logs the fetch, and writes each slot's `fovea verify --chain` verdict. |
| `keep.sh` | The image's entrypoint, one run: pulls the records clone, clones [mcl-fovea-assessments](https://github.com/macula-io/mcl-fovea-assessments), runs the keeper, commits and pushes what it kept. |
| `Containerfile` | The image: the keeper, the released `fovea` (v0.3.0) and `keep.sh`. |
| `systemd/` | The user timer (7, 22, 37 and 52 past) and the unit that runs the image by digest. |

## The image

CI builds `ghcr.io/macula-io/mcl-fovea-keeper` on every push to `main` (`:latest`) and every `v*` tag (`:<version>`), each also as `:git-<sha>`, and signs it by digest with an SPDX SBOM and SLSA provenance (macula-ci-images' `attest-image.yml`). Check a digest yourself:

```sh
cosign verify ghcr.io/macula-io/mcl-fovea-keeper@sha256:<digest> \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  --certificate-identity-regexp '^https://github\.com/macula-io/macula-ci-images/\.github/workflows/attest-image\.yml@' \
  --certificate-github-workflow-repository macula-io/mcl-fovea-keeper
```

## Running a keeper

Anyone can run one and compare what they keep with ours. The image brings the code, the records repository the policy, the machine only its key and paths:

| Mounted at | What |
| --- | --- |
| `/records` | A clone of mcl-fovea-records (your fork, for your own keeper), read-write. Its `keeper.json` is the keeping policy: realm, profile, the stations it asks, the slots it keeps. |
| `/etc/fovea-keeper/deploy_key` | An ssh key that can push to that clone's origin, and nothing else |
| `/etc/fovea-keeper/known_hosts` | GitHub's pinned host key |

The container needs an IPv6 route to the stations (they are IPv6-only). Our keeper runs on a Macula lab machine as the user units in `systemd/`: `~/fovea-keeper/keeper.env` names the image by digest (`KEEPER_IMAGE=ghcr.io/macula-io/mcl-fovea-keeper@sha256:...`), the podman network `fovea-keeper` gives it an IPv6 route to the stations and none to the machine's own services, and the deploy key, generated on the machine, writes only mcl-fovea-records.

## Honest limits

Our keeper runs on our own box: off the observer's box and off every station it observes, but **not independent of us**. Independent keepers, run by others, are what make a withheld record visible to everyone.
