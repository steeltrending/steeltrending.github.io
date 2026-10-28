#!/bin/bash
# 由「終端機」App 執行（終端機需有完整磁碟取用權限），完成後自動關閉視窗
cd "$HOME" || exit 1
/bin/bash /Users/chen/Documents/GitHub/steeltrending.github.io/auto_update.sh
osascript -e 'tell application "Terminal" to close (every window whose name contains "run_daily")' >/dev/null 2>&1 &
exit 0
