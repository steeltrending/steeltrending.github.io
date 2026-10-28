#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  重新加載自動化任務 (執行時間: 09:30)                    ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

PLIST_PATH="$HOME/Library/LaunchAgents/com.steeltrending.autoupdate.plist"

echo "1️⃣ 卸載舊的任務..."
launchctl unload "$PLIST_PATH" 2>/dev/null && echo "✅ 舊任務已卸載" || echo "ℹ️  任務未運行"
echo ""

echo "2️⃣ 加載新的任務..."
launchctl load "$PLIST_PATH" && echo "✅ 新任務已加載" || echo "❌ 加載失敗"
echo ""

echo "3️⃣ 驗證任務狀態..."
if launchctl list | grep -q "com.steeltrending.autoupdate"; then
    echo "✅ 任務已成功加載"
    launchctl list | grep steeltrending
else
    echo "⚠️  任務狀態未知"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✨ 任務已重新配置！                                      ║"
echo "║  執行時間: 每天 09:30                                     ║"
echo "╚════════════════════════════════════════════════════════════╝"
