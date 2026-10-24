#!/usr/bin/env bash
# Publish the checked-out commit to the apps VM and rebuild the containers.
set -Eeuo pipefail

trap 'echo "Error on line $LINENO: command '\''$BASH_COMMAND'\'' failed with exit code $?" >&2' ERR

if [ $# -ne 2 ]; then
  echo "Usage: $0 WORKSPACE FULL_SHA" >&2
  exit 1
fi

workspace="$1"
sha="$2"
dest=/opt/apps/utictactoe
work_root=/home/github-runner/actions-runner-utictactoe/_work

if [[ ! "$sha" =~ ^[0-9a-f]{40}$ ]]; then
  echo "Error: SHA '$sha' must be 40 hexadecimal characters" >&2
  exit 1
fi

workspace="$(realpath "$workspace")"
case "$workspace" in
  "$work_root"/*) ;;
  *)
    echo "Error: workspace must be inside $work_root" >&2
    exit 1
    ;;
esac

if [ ! -f "$workspace/compose.production.yml" ]; then
  echo "Error: $workspace/compose.production.yml is missing" >&2
  exit 1
fi

mkdir -p /run/lock
exec 9>/run/lock/utictactoe-deploy.lock
if ! flock -n 9; then
  echo "Error: another utictactoe deploy is running" >&2
  exit 1
fi

install -m 755 "$workspace/ops/deploy/deploy-utictactoe.sh" /usr/local/sbin/deploy-utictactoe

mkdir -p "$dest"
rsync -a --delete \
  --exclude '.git/' \
  --exclude 'backend/weights/' \
  --exclude 'backend/datasets/' \
  --exclude 'backend/runs/' \
  "$workspace/" "$dest/"

docker compose -f "$dest/compose.production.yml" --project-directory "$dest" up -d --build --remove-orphans

curl --fail --retry 20 --retry-delay 3 --retry-connrefused -sS http://10.20.0.12:5100/health
echo
curl --fail --retry 20 --retry-delay 3 --retry-connrefused -sS -o /dev/null http://10.20.0.12:3100/
echo "Deployed $sha"
