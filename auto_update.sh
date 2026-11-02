#!/bin/bash
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"  # launchd 預設 PATH 找不到 Homebrew 的 pdfinfo／pdftoppm

################################################################################
# Steel Trending Daily Update Automation Script (改進版)
# 自動化更新鋼鐵潮流網站的每日圖卡與報告
#
# 改進點：
# - 自動 Git 推送（含重試機制）
# - 更好的錯誤處理
# - 完整的日誌記錄
################################################################################

set -e

SOURCE_FOLDER="/Users/chen/Desktop/AI專案資料夾/鋼鐵日報"
REPO_FOLDER="/Users/chen/Documents/GitHub/steeltrending.github.io"
LOG_FILE="$REPO_FOLDER/logs/update_$(date '+%Y-%m-%d').log"

mkdir -p "$REPO_FOLDER/logs"

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

print_status "info" "=========================================="
print_status "info" "鋼鐵潮流 - 每日更新開始"
print_status "info" "=========================================="

DATE=$(date '+%Y-%m-%d')
print_status "info" "處理日期: $DATE"

# ROC年份轉換函數
convert_to_roc_folder() {
    local year=$(date '+%Y')
    local month=$(date '+%m')
    local day=$(date '+%d')
    local roc_year=$((year - 1911))
    printf "%d%s%s" "$roc_year" "$month" "$day"
}

ROC_DATE=$(convert_to_roc_folder)

if [ ! -d "$SOURCE_FOLDER" ]; then
    error_exit "來源資料夾不存在: $SOURCE_FOLDER"
fi

if [ ! -d "$REPO_FOLDER" ]; then
    error_exit "倉庫資料夾不存在: $REPO_FOLDER"
fi

SOURCE_IMAGE="$SOURCE_FOLDER/$ROC_DATE/steel_social.jpg"
SOURCE_PDF="$SOURCE_FOLDER/$ROC_DATE/steel_full_report.pdf"

if [ ! -f "$SOURCE_IMAGE" ]; then
    error_exit "找不到圖卡文件: $SOURCE_IMAGE"
fi

print_status "success" "找到圖卡文件"

if [ ! -f "$SOURCE_PDF" ]; then
    print_status "warning" "找不到報告文件: $SOURCE_PDF (將只更新圖卡)"
    HAS_PDF=false
else
    print_status "success" "找到報告文件"
    HAS_PDF=true
fi

# 複製文件到倉庫
print_status "info" "複製文件到倉庫..."

cp "$SOURCE_IMAGE" "$REPO_FOLDER/data/steel_social.jpg"
print_status "success" "圖卡文件已複製"

if [ "$HAS_PDF" = true ]; then
    # 注意：add_card.py 會先清空 data/report/$DATE 再自行複製，故這裡不可預先複製 PDF
    print_status "success" "報告文件已確認（交由 add_card.py 處理）"
fi

# 執行 add_card.py
print_status "info" "執行 add_card.py 處理..."

cd "$REPO_FOLDER"

if [ "$HAS_PDF" = true ]; then
    python3 tools/add_card.py "$REPO_FOLDER/data/steel_social.jpg" "$DATE" "$SOURCE_PDF" 2>&1 | tee -a "$LOG_FILE"
else
    python3 tools/add_card.py "$REPO_FOLDER/data/steel_social.jpg" "$DATE" 2>&1 | tee -a "$LOG_FILE"
fi

if [ ${PIPESTATUS[0]} -eq 0 ]; then
    print_status "success" "add_card.py 執行成功"
else
    print_status "warning" "add_card.py 執行失敗或未找到"
fi

# 更新 latest.json
print_status "info" "更新 latest.json..."

python3 << PYTHON_FINAL
import json
import os
import re

repo_folder = "/Users/chen/Documents/GitHub/steeltrending.github.io"
latest_json_path = os.path.join(repo_folder, "data/latest.json")

# latest.json 的 items／updated 由 GitHub Actions（fetch_futures.py）寫入。
# 本機只改 social.date 這一個值，並用文字替換保留原排版，避免整份重寫造成合併衝突。
try:
    with open(latest_json_path, 'r', encoding='utf-8') as f:
        text = f.read()
    json.loads(text)

    new_text, n = re.subn(r'("social"\s*:\s*\{\s*"date"\s*:\s*)"[^"]*"', r'\g<1>"$DATE"', text, count=1)
    if n == 0:
        raise ValueError("找不到 social.date 欄位，未修改 latest.json")
    json.loads(new_text)

    if new_text != text:
        with open(latest_json_path, 'w', encoding='utf-8') as f:
            f.write(new_text)

    print("✅ latest.json 已更新")
except Exception as e:
    print(f"❌ latest.json 更新失敗: {e}")
    exit(1)
PYTHON_FINAL

print_status "success" "latest.json 更新完成"

# Git 操作
print_status "info" "配置 Git 並提交變更..."

cd "$REPO_FOLDER"

git config user.email "noreply@anthropic.com"
git config user.name "Steel Trending Auto Bot"

# Stage 所有變更
git add -A
print_status "success" "文件已暫存"

# 檢查是否有變更需要提交
if git diff --cached --quiet; then
    print_status "warning" "沒有新的變更要提交"
else
    COMMIT_MESSAGE="自動更新 $DATE 鋼鐵日報圖卡與報告"
    git commit -m "$COMMIT_MESSAGE"
    print_status "success" "變更已提交: $COMMIT_MESSAGE"
    
    # ========================================================================
    # Git 推送 (含重試機制)
    # ========================================================================
    
    print_status "info" "準備推送到 GitHub..."
    
    # 嘗試拉取遠程更新 (避免衝突)
    print_status "info" "檢查遠程更新..."
    # 與 GitHub Actions 一致使用 rebase；失敗就中止 rebase、不推送，避免留下衝突狀態
    sync_remote() {
        # --autostash：logs/ 已被 git 追蹤且執行中持續寫入，否則 rebase 會因未暫存變更而拒絕
        git pull --rebase --autostash origin main 2>&1 | tee -a "$LOG_FILE"
        if [ "${PIPESTATUS[0]}" -eq 0 ]; then
            return 0
        fi
        git rebase --abort >/dev/null 2>&1 || true
        return 1
    }

    # 推送到 GitHub (最多重試 3 次，每次推送前先 rebase 同步)
    PUSH_SUCCESS=false
    for attempt in 1 2 3; do
        if sync_remote; then
            print_status "success" "遠程同步完成"
        else
            print_status "error" "遠程同步失敗（已中止 rebase），本次不推送"
            break
        fi

        print_status "info" "推送嘗試 [$attempt/3]..."

        git push origin main 2>&1 | tee -a "$LOG_FILE"
        if [ "${PIPESTATUS[0]}" -eq 0 ]; then
            print_status "success" "✨ 成功推送到 GitHub"
            PUSH_SUCCESS=true
            break
        else
            if [ $attempt -lt 3 ]; then
                print_status "warning" "推送失敗，${attempt}秒後重試..."
                sleep 2
            fi
        fi
    done
    
    if [ "$PUSH_SUCCESS" = false ]; then
        print_status "error" "推送 GitHub 失敗"
        print_status "warning" "本地提交已保存，請稍後手動推送："
        print_status "warning" "  cd $REPO_FOLDER && git push origin main"
    fi
fi

# 最終狀態
print_status "success" "=========================================="
print_status "success" "每日更新完成"
print_status "success" "日期: $DATE"
print_status "success" "時間: $(date '+%Y-%m-%d %H:%M:%S')"
print_status "success" "=========================================="

echo ""
echo "📋 完整日誌已保存至:"
echo "   $LOG_FILE"

exit 0
