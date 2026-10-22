#!/usr/bin/env bash
# 本地一键：下载上游最新 + 应用 overrides.ini + 生成 metafenliu.ini
# 用法：
#   ./sync.sh             只在本目录生成，不推送
#   ./sync.sh --push      生成并提交推送到 GitHub（改完想立刻生效用这个）
set -euo pipefail
cd "$(dirname "$0")"

URL="https://raw.githubusercontent.com/usbog232/clashmetadingyue/main/metafenliu.ini"

echo "==> 下载上游最新 metafenliu.ini"
curl -fsSL "$URL" -o upstream.ini
echo "    $(wc -l < upstream.ini) 行"

echo "==> 应用 overrides.ini"
set +e
python3 apply_overrides.py
RC=$?
set -e

if [ "${1:-}" = "--push" ]; then
  git add -A
  if git diff --cached --quiet; then
    echo "==> 没有变化，不提交"
  else
    git commit -q -m "chore: 同步上游 metafenliu.ini $(date -u +%Y-%m-%d)"
    git push -q
    echo "==> 已推送到 GitHub"
  fi
else
  echo
  echo "==> 只在本地生成了。要立刻生效请跑：./sync.sh --push"
fi

if [ "$RC" -ne 0 ]; then
  echo "==> ⚠️  有改动没生效，按上面提示修正 overrides.ini 后重跑" >&2
  exit "$RC"
fi
echo "==> 完成：$(pwd)/metafenliu.ini"
