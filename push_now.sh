#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  推送每日更新到 GitHub                                   ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd ~/Documents/GitHub/steeltrending.github.io

echo "推送中..."
if git push origin main; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✨ 成功！鋼鐵潮流網站已更新！                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 今日更新已上線："
    echo "  ✅ 速報圖卡已發佈"
    echo "  ✅ 完整報告已發佈"
    echo "  ✅ 網站元數據已更新"
else
    echo "❌ 推送失敗"
    echo ""
    echo "建議："
    echo "1. 檢查網路連線"
    echo "2. 驗證 GitHub 認證"
    echo "3. 執行: git config --global credential.helper osxkeychain"
fi
