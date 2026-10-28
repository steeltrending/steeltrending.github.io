#!/bin/bash

################################################################################
# 鋼鐵潮流 - 完整自動化一鍵設置
# 執行此腳本會自動完成所有設置
################################################################################

set -e

REPO_DIR="/Users/chen/Documents/GitHub/steeltrending.github.io"
PLIST_PATH="$HOME/Library/LaunchAgents/com.steeltrending.autoupdate.plist"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  鋼鐵潮流 - 完整自動化設置                               ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# 步驟 1: 設置 Git Credential Helper
# ============================================================================

echo "📋 步驟 1/4: 設置 Git Credential Helper..."
git config --global credential.helper osxkeychain
echo "✅ Credential Helper 已設置"
echo ""

# ============================================================================
# 步驟 2: 提示用戶輸入 GitHub 信息
# ============================================================================

echo "📋 步驟 2/4: GitHub 認證設置"
echo ""
echo "⚠️  需要您的 GitHub 認證信息："
echo ""
echo "1️⃣  如果您還沒有 Personal Access Token，請訪問："
echo "    https://github.com/settings/tokens/new"
echo ""
echo "    設置："
echo "    - Token name: Steel Trending Auto Update"
echo "    - Expiration: No expiration"
echo "    - Scopes: repo"
echo ""

read -p "🔑 請輸入您的 GitHub 用戶名: " GITHUB_USER
read -sp "🔐 請輸入您的 Personal Access Token: " GITHUB_TOKEN
echo ""
echo ""

# ============================================================================
# 步驟 3: 推送到 GitHub（使用提供的 Token）
# ============================================================================

echo "📋 步驟 3/4: 推送到 GitHub..."
cd "$REPO_DIR"

# 設定臨時的 credential
git config --global credential.helper store
echo "https://${GITHUB_USER}:${GITHUB_TOKEN}@github.com" > ~/.git-credentials

# 推送
if git push origin main 2>&1; then
    echo "✅ 成功推送到 GitHub"
else
    echo "❌ 推送失敗，請檢查用戶名和 Token"
    rm -f ~/.git-credentials
    exit 1
fi

# 清理明文存儲，改用 osxkeychain
rm -f ~/.git-credentials
git config --global credential.helper osxkeychain
echo ""

# ============================================================================
# 步驟 4: 設置 Launchd 定時任務
# ============================================================================

echo "📋 步驟 4/4: 設置自動定時任務..."

# 創建 LaunchAgents 目錄
mkdir -p "$HOME/Library/LaunchAgents"

# 創建 plist 文件
cat > "$PLIST_PATH" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.steeltrending.autoupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/chen/Documents/GitHub/steeltrending.github.io/auto_update.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>8</integer>
        <key>Minute</key>
        <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/chen/Documents/GitHub/steeltrending.github.io/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/chen/Documents/GitHub/steeltrending.github.io/logs/launchd_error.log</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
EOF

# 加載定時任務
launchctl load "$PLIST_PATH" 2>/dev/null || launchctl unload "$PLIST_PATH" 2>/dev/null; launchctl load "$PLIST_PATH"
echo "✅ 定時任務已設置 (每天 08:30 執行)"
echo ""

# ============================================================================
# 驗證設置
# ============================================================================

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✨ 自動化設置完成！                                      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 設置摘要："
echo "  ✅ Git Credential Helper: osxkeychain"
echo "  ✅ GitHub 認證: 已儲存"
echo "  ✅ 定時任務: 每天 08:30 自動執行"
echo ""

# 驗證任務已加載
if launchctl list | grep -q "com.steeltrending.autoupdate"; then
    echo "✅ 任務已成功加載"
else
    echo "⚠️  任務加載狀態未知，請執行："
    echo "   launchctl list | grep steeltrending"
fi

echo ""
echo "📖 查看日誌："
echo "   tail -f ~/Documents/GitHub/steeltrending.github.io/logs/update_*.log"
echo ""
echo "🛑 停止自動化："
echo "   launchctl unload ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist"
echo ""
echo "鋼鐵潮流網站現在會每天自動更新！🎉"
