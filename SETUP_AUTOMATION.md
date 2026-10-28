# 鋼鐵潮流自動化更新設置指南

自動化腳本 `auto_update.sh` 已準備就緒。要完成設置，請按照以下步驟操作。

## 📋 前置需求

- macOS 系統
- Git 已安裝
- Python 3 環境
- 存儲庫位置：`~/Documents/GitHub/steeltrending.github.io`

## 🔧 設置步驟

### 步驟 1: 生成 GitHub Personal Access Token

1. 訪問：https://github.com/settings/tokens/new
2. 填寫設置：
   - **Token name**: `Steel Trending Auto Update`
   - **Expiration**: `No expiration`
   - **Scopes**: 勾選 `repo` (完整倉庫訪問)
3. 點擊 "Generate token"
4. **重要**：複製生成的 token（只顯示一次！）

### 步驟 2: 設置 Git Credential Helper

在終端機執行：

```bash
git config --global credential.helper osxkeychain
```

這會將認證信息存儲在 macOS 鑰匙圈中。

### 步驟 3: 手動執行一次 git push（存儲憑證）

1. 開啟終端機
2. 執行：
```bash
cd ~/Documents/GitHub/steeltrending.github.io
git push origin main
```

3. 當提示輸入時：
   - **Username**: 輸入你的 GitHub 用戶名
   - **Password**: 貼上第 1 步生成的 Personal Access Token

4. 如果成功，系統會將憑證存儲到鑰匙圈

### 步驟 4: 測試自動化腳本

在終端機執行測試：

```bash
~/Documents/GitHub/steeltrending.github.io/auto_update.sh
```

預期輸出應該包含：
```
✅ 鋼鐵潮流 - 每日更新開始
✅ 處理日期: 2026-10-28
✅ 找到圖卡文件
✅ 圖卡文件已複製
✅ add_card.py 執行成功
✅ latest.json 已更新
✅ 文件已暫存
✅ 變更已提交
✅ 成功推送到 GitHub
✅ 每日更新完成
```

### 步驟 5: 設置自動定時執行

選擇以下兩種方式之一：

#### 方案 A: 使用 cron（推薦 - 簡單）

1. 開啟終端機
2. 編輯 crontab：
```bash
crontab -e
```

3. 添加以下一行（每天上午 8:00 執行）：
```
0 8 * * * /Users/chen/Documents/GitHub/steeltrending.github.io/auto_update.sh >> /Users/chen/Documents/GitHub/steeltrending.github.io/logs/cron.log 2>&1
```

4. 保存退出（VI 編輯器：按 Esc，輸入 `:wq`，按 Enter）

5. 驗證設置：
```bash
crontab -l
```

#### 方案 B: 使用 launchd（推薦 - 更可靠）

1. 創建配置文件：
```bash
cat > ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist << 'PLIST'
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
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/chen/Documents/GitHub/steeltrending.github.io/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/chen/Documents/GitHub/steeltrending.github.io/logs/launchd_error.log</string>
</dict>
</plist>
PLIST
```

2. 加載任務：
```bash
launchctl load ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

3. 驗證：
```bash
launchctl list | grep steeltrending
```

4. 要停用任務：
```bash
launchctl unload ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

## 📊 監控和日誌

### 查看最近的日誌

```bash
tail -f ~/Documents/GitHub/steeltrending.github.io/logs/update_*.log
```

### 手動執行並查看輸出

```bash
~/Documents/GitHub/steeltrending.github.io/auto_update.sh
```

## 🔍 故障排除

### 問題: "找不到圖卡文件"

**原因**: 指定日期的資料夾不存在
**解決**: 確保 `/Users/chen/Desktop/AI專案資料夾/鋼鐵日報/YYYY-MM-DD/` 資料夾存在

### 問題: "推送到 GitHub 失敗"

**原因**: 可能是以下幾個：
1. GitHub Personal Access Token 未正確設置
2. credential helper 未啟用

**解決**:
```bash
# 驗證 credential helper 設置
git config --global credential.helper

# 手動測試推送
cd ~/Documents/GitHub/steeltrending.github.io
git push origin main
```

### 問題: 定時任務未執行

**檢查 cron 日誌（macOS）**:
```bash
log stream --predicate 'process == "cron"' --level debug
```

**檢查 launchd 日誌**:
```bash
cat ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
tail -f /Users/chen/Documents/GitHub/steeltrending.github.io/logs/launchd*.log
```

## ✅ 完成確認清單

- [ ] 生成了 GitHub Personal Access Token
- [ ] 設置了 credential helper (`git config --global credential.helper osxkeychain`)
- [ ] 手動執行過一次 `git push` 並存儲了憑證
- [ ] 測試了 `auto_update.sh` 腳本（成功完成）
- [ ] 設置了定時任務（cron 或 launchd）
- [ ] 驗證了日誌文件位置和權限

完成以上所有步驟後，自動化更新就會每天自動運行！

