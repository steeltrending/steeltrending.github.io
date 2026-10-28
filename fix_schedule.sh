#!/bin/bash
# 重新安裝每日 09:30 自動更新與推送排程，並立即試跑一次
REPO="/Users/chen/Documents/GitHub/steeltrending.github.io"
LABEL="com.steeltrending.autoupdate"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
UIDN=$(id -u)

chmod +x "$REPO/run_daily.command"
mkdir -p "$HOME/Library/LaunchAgents" "$REPO/logs"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key><array><string>/usr/bin/open</string><string>-a</string><string>Terminal</string><string>$REPO/run_daily.command</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>9</integer><key>Minute</key><integer>30</integer></dict>
  <key>StandardOutPath</key><string>$REPO/logs/launchd.log</string>
  <key>StandardErrorPath</key><string>$REPO/logs/launchd_error.log</string>
</dict></plist>
PL

launchctl bootout "gui/$UIDN/$LABEL" 2>/dev/null
launchctl bootstrap "gui/$UIDN" "$PLIST" && echo "已載入排程（每天 09:30）"
: > "$REPO/logs/launchd_error.log"
launchctl kickstart -k "gui/$UIDN/$LABEL" && echo "已試跑，等待 60 秒…"
sleep 60
echo "---- launchd_error.log ----"; cat "$REPO/logs/launchd_error.log"
echo "---- 最新 log ----"; ls -t "$REPO"/logs/update_*.log 2>/dev/null | head -1 | xargs -I{} tail -15 {}
