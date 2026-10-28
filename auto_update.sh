#!/bin/bash

################################################################################
# Steel Trending Daily Update Automation Script
# 自動化更新鋼鐵潮流網站的每日圖卡與報告
#
# 用途: 在 Mac 上每日執行，自動更新網站內容到 GitHub
# 位置: ~/Documents/GitHub/steeltrending.github.io/auto_update.sh
# 執行: 通過 cron 或 launchd 每日自動執行
#
# 必須先執行以下設定:
# 1. GitHub Personal Access Token 設置
# 2. git config --global credential.helper osxkeychain
# 3. 手動執行一次 git push 以儲存憑證
################################################################################

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

SOURCE_FOLDER="/Users/chen/Desktop/AI專案資料夾/鋼鐵日報"
REPO_FOLDER="/Users/chen/Documents/GitHub/steeltrending.github.io"
LOG_FILE="$REPO_FOLDER/logs/update_$(date '+%Y-%m-%d').log"

# Create logs directory if it doesn't exist
mkdir -p "$REPO_FOLDER/logs"

# ============================================================================
# Functions
# ============================================================================

# Convert Western date to ROC (民國) date format
# Input: 2026-10-28
# Output: 1151028
convert_to_roc_folder() {
    local western_date="$1"
    local year=$(echo "$western_date" | cut -d'-' -f1)
    local month=$(echo "$western_date" | cut -d'-' -f2)
    local day=$(echo "$western_date" | cut -d'-' -f3)
    
    # ROC year = Western year - 1911
    local roc_year=$((year - 1911))
    
    # Format: YYMMDD (e.g., 1151028)
    printf "%d%s%s" "$roc_year" "$month" "$day"
}

log_message() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

print_status() {
    local status="$1"
    local message="$2"
    case "$status" in
        success)
            echo "✅ $message"
            log_message "✅ $message"
            ;;
        info)
            echo "ℹ️  $message"
            log_message "ℹ️  $message"
            ;;
        warning)
            echo "⚠️  $message"
            log_message "⚠️  $message"
            ;;
        error)
            echo "❌ $message"
            log_message "❌ $message"
            ;;
    esac
}

error_exit() {
    local message="$1"
    print_status "error" "$message"
    exit 1
}

# ============================================================================
# Main Process
# ============================================================================

print_status "info" "=========================================="
print_status "info" "鋼鐵潮流 - 每日更新開始"
print_status "info" "=========================================="

# Calculate today's date in YYYY-MM-DD format
DATE=$(date '+%Y-%m-%d')
ROC_DATE=$(convert_to_roc_folder "$DATE")
print_status "info" "處理日期: $DATE (民國文件夾: $ROC_DATE)"

# Check if source folder exists
if [ ! -d "$SOURCE_FOLDER" ]; then
    error_exit "來源資料夾不存在: $SOURCE_FOLDER"
fi

# Check if repository exists
if [ ! -d "$REPO_FOLDER" ]; then
    error_exit "倉庫資料夾不存在: $REPO_FOLDER"
fi

# Check for source files (using ROC date format for folder name)
SOURCE_IMAGE="$SOURCE_FOLDER/$ROC_DATE/steel_social.jpg"
SOURCE_PDF="$SOURCE_FOLDER/$ROC_DATE/steel_full_report.pdf"

if [ ! -f "$SOURCE_IMAGE" ]; then
    error_exit "找不到圖卡文件: $SOURCE_IMAGE"
fi

print_status "success" "找到圖卡文件"

# Check for PDF (optional but log if missing)
if [ ! -f "$SOURCE_PDF" ]; then
    print_status "warning" "找不到報告文件: $SOURCE_PDF (將只更新圖卡)"
    HAS_PDF=false
else
    print_status "success" "找到報告文件"
    HAS_PDF=true
fi

# ============================================================================
# Copy files to repository
# ============================================================================

print_status "info" "複製文件到倉庫..."

cp "$SOURCE_IMAGE" "$REPO_FOLDER/data/steel_social.jpg"
print_status "success" "圖卡文件已複製"

if [ "$HAS_PDF" = true ]; then
    mkdir -p "$REPO_FOLDER/data/report/$DATE"
    cp "$SOURCE_PDF" "$REPO_FOLDER/data/report/$DATE/report.pdf"
    print_status "success" "報告文件已複製"
fi

# ============================================================================
# Execute add_card.py
# ============================================================================

print_status "info" "執行 add_card.py 處理..."

cd "$REPO_FOLDER"

if [ "$HAS_PDF" = true ]; then
    python3 tools/add_card.py "$REPO_FOLDER/data/steel_social.jpg" "$DATE" "$REPO_FOLDER/data/report/$DATE/report.pdf" 2>&1 | tee -a "$LOG_FILE" || error_exit "add_card.py 執行失敗"
else
    python3 tools/add_card.py "$REPO_FOLDER/data/steel_social.jpg" "$DATE" 2>&1 | tee -a "$LOG_FILE" || error_exit "add_card.py 執行失敗"
fi

print_status "success" "add_card.py 執行成功"

# ============================================================================
# Update latest.json with current date
# ============================================================================

print_status "info" "更新 latest.json..."

python3 << PYTHON_SCRIPT
import json
import os
from datetime import datetime

repo_folder = "/Users/chen/Documents/GitHub/steeltrending.github.io"
latest_json_path = os.path.join(repo_folder, "data/latest.json")
date_str = "$DATE"

try:
    with open(latest_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    data['updated'] = datetime.now().isoformat()
    if 'social' not in data:
        data['social'] = {}
    data['social']['date'] = date_str
    
    with open(latest_json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ latest.json 已更新，日期設為 {date_str}")
except Exception as e:
    print(f"❌ latest.json 更新失敗: {e}")
    exit(1)
PYTHON_SCRIPT

print_status "success" "latest.json 更新完成"

# ============================================================================
# Git operations
# ============================================================================

print_status "info" "配置 Git 並提交變更..."

cd "$REPO_FOLDER"

# Configure git user for this repo
git config user.email "noreply@anthropic.com"
git config user.name "Steel Trending Auto Bot"

# Stage all changes
git add -A
print_status "success" "文件已暫存"

# Check if there are changes to commit
if git diff --cached --quiet; then
    print_status "warning" "沒有新的變更要提交"
else
    # Commit with timestamp
    COMMIT_MESSAGE="更新卡片與報告 $DATE"
    git commit -m "$COMMIT_MESSAGE"
    print_status "success" "變更已提交: $COMMIT_MESSAGE"
    
    # ========================================================================
    # Push to GitHub
    # ========================================================================
    
    print_status "info" "推送到 GitHub..."
    
    # Use the credential helper to authenticate
    if git push origin main 2>&1 | tee -a "$LOG_FILE"; then
        print_status "success" "成功推送到 GitHub"
    else
        error_exit "推送到 GitHub 失敗 - 請檢查 GitHub 設置"
    fi
fi

# ============================================================================
# Final Status
# ============================================================================

print_status "success" "=========================================="
print_status "success" "每日更新完成"
print_status "success" "日期: $DATE"
print_status "success" "時間: $(date '+%Y-%m-%d %H:%M:%S')"
print_status "success" "=========================================="

log_file_size=$(wc -c < "$LOG_FILE")
echo ""
echo "📋 完整日誌已保存至:"
echo "   $LOG_FILE"

exit 0
