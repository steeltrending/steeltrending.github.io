#!/bin/bash

################################################################################
# 自動推送腳本 - 無需交互式認證
# 此腳本使用已儲存的 GitHub 認證進行自動推送
################################################################################

REPO_DIR="/Users/chen/Documents/GitHub/steeltrending.github.io"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  自動推送到 GitHub                                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$REPO_DIR"

# 檢查是否有未提交的變更
echo "檢查 Git 狀態..."
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 所有變更已提交"
else
    echo "⚠️  發現未提交的文件，自動提交..."
    git add -A
    git commit -m "自動提交 $(date '+%Y-%m-%d %H:%M:%S')"
fi

echo ""
echo "推送到 GitHub..."

# 嘗試使用 credential helper 推送
if git push origin main 2>&1; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║  ✨ 推送成功！                                            ║"
    echo "║  鋼鐵潮流網站已更新                                     ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    exit 0
else
    # 如果推送失敗，嘗試使用 gh cli
    if command -v gh &> /dev/null; then
        echo "嘗試使用 GitHub CLI..."
        gh auth status && git push origin main && exit 0
    fi
    
    # 如果上述都失敗，使用 SSH
    if command -v ssh-add &> /dev/null; then
        echo "嘗試使用 SSH..."
        eval "$(ssh-agent -s)"
        ssh-add ~/.ssh/id_rsa 2>/dev/null
        git push origin main && exit 0
    fi
    
    echo ""
    echo "❌ 推送失敗"
    echo ""
    echo "建議："
    echo "1. 驗證 GitHub 認證："
    echo "   git config --global credential.helper osxkeychain"
    echo ""
    echo "2. 手動推送："
    echo "   cd ~/Documents/GitHub/steeltrending.github.io"
    echo "   git push origin main"
    exit 1
fi
