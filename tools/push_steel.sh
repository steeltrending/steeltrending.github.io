#!/bin/bash
# 本機自動推送:雲端排程只提交,這支腳本負責 git push。
REPO="$HOME/Documents/GitHub/steeltrending.github.io"
HELPER="/Volumes/Extreme SSD/AI專案資料夾/.git-helper/credential-steel.sh"
LOG="$HOME/Library/Logs/steel_push.log"
export PATH=/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin
log(){ echo "$(date '+%F %T') $*" >> "$LOG"; }

# 自我更新:倉庫內的 plist 與已安裝的不同時,自動重新載入(免手動安裝)
SRC_PLIST="$REPO/tools/com.steeltrending.push.plist"
DST_PLIST="$HOME/Library/LaunchAgents/com.steeltrending.push.plist"
if [ -f "$SRC_PLIST" ] && ! cmp -s "$SRC_PLIST" "$DST_PLIST"; then
  mkdir -p "$HOME/Library/LaunchAgents"
  nohup bash -c "sleep 3; launchctl unload '$DST_PLIST' 2>/dev/null; cp '$SRC_PLIST' '$DST_PLIST'; launchctl load '$DST_PLIST'" >/dev/null 2>&1 &
  echo "$(date '+%F %T') 偵測到新版排程設定,自動重新載入" >> "$HOME/Library/Logs/steel_push.log"
fi

cd "$REPO" || { log "找不到倉庫"; exit 1; }
rm -f .git/index.lock .git/HEAD.lock 2>/dev/null
if [ -f "$HELPER" ]; then
  G=(git -c "credential.helper=" -c "credential.helper=!sh \"$HELPER\"")
else
  G=(git)   # 外接碟未接上:改用這台 Mac 本身的 git 憑證(鑰匙圈 / gh)
fi

"${G[@]}" fetch origin main -q 2>>"$LOG" || { log "fetch 失敗"; exit 1; }
AHEAD=$(git rev-list --count origin/main..HEAD)
[ "$AHEAD" -eq 0 ] && exit 0   # 沒有待推送提交,保持安靜

for i in 1 2 3; do
  if "${G[@]}" push origin main >>"$LOG" 2>&1; then
    log "推送成功($AHEAD 個提交)"
    osascript -e 'display notification "鋼鐵潮流已推送" with title "steeltrending"' 2>/dev/null
    exit 0
  fi
  log "推送被拒,第 $i 次 rebase 重試"
  "${G[@]}" pull --rebase --autostash -X ours origin main >>"$LOG" 2>&1 || git rebase --abort 2>/dev/null
done
log "推送失敗,請手動檢查"
osascript -e 'display notification "推送失敗,請看 steel_push.log" with title "steeltrending"' 2>/dev/null
exit 1
