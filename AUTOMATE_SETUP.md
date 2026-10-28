# 鋼鐵潮流 - 完整自動化設置指南

自動化腳本已經準備就緒。請按照以下步驟完成最後的設置。

## ✅ 已完成的步驟

- [x] auto_update.sh 腳本已創建
- [x] Git credential helper (osxkeychain) 已設置
- [x] Launchd 配置文件已創建
- [ ] GitHub Personal Access Token （需要您設置）
- [ ] 手動推送一次以儲存凭證 （需要您執行）
- [ ] 加載定時任務 （需要您執行）

---

## 🔐 步驟 1: 生成 GitHub Personal Access Token

### 在網頁上進行：

1. 訪問: https://github.com/settings/tokens/new

2. 填寫以下設置：
   - **Token name**: `Steel Trending Auto Update`
   - **Expiration**: `No expiration`
   - **Scopes**: 勾選 `repo` (完整倉庫訪問權限)

3. 點擊 "Generate token" 按鈕

4. **重要！複製生成的 token**（只會顯示一次）

---

## 📤 步驟 2: 手動推送一次以儲存凭證

在 Mac 終端機執行以下命令：

```bash
cd ~/Documents/GitHub/steeltrending.github.io
git push origin main
```

系統會提示輸入：
- **Username**: 輸入您的 GitHub 用戶名
- **Password**: 粘貼第 1 步生成的 Personal Access Token

✅ 成功後，凭證會自動保存到鑰匙圈。

---

## ⏰ 步驟 3: 加載定時任務

完成上面的認證後，在終端機執行：

```bash
launchctl load ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

驗證任務已加載：

```bash
launchctl list | grep steeltrending
```

應該能看到類似的輸出：
```
-   0   com.steeltrending.autoupdate
```

---

## 🧪 步驟 4: 測試自動化腳本

手動運行一次以驗證腳本是否正常工作：

```bash
~/Documents/GitHub/steeltrending.github.io/auto_update.sh
```

預期輸出：
```
✅ 鋼鐵潮流 - 每日更新開始
✅ 處理日期: 2026-10-28 (民國: 1151028)
✅ 找到圖卡文件
✅ 圖卡文件已複製
✅ add_card.py 執行成功
✅ latest.json 已更新
✅ 文件已暫存
✅ 變更已提交: 更新卡片與報告 2026-10-28
✅ 成功推送到 GitHub
✅ 每日更新完成
```

---

## 📊 監控自動化任務

### 查看最近的日誌

```bash
tail -f ~/Documents/GitHub/steeltrending.github.io/logs/update_*.log
```

### 查看 Launchd 的日誌

```bash
cat ~/Documents/GitHub/steeltrending.github.io/logs/launchd.log
```

### 檢查任務狀態

```bash
launchctl list com.steeltrending.autoupdate
```

---

## ⏸️ 暫停或停止自動化

如果需要暫時停止自動任務：

```bash
# 停止任務
launchctl unload ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist

# 重新啟用任務
launchctl load ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

---

## 🔄 修改執行時間

如果想改變每日執行時間，編輯 plist 文件：

```bash
nano ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

找到這一段並修改時間（24 小時制）：
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>8</integer>        <!-- 改成想要的小時 (0-23) -->
    <key>Minute</key>
    <integer>30</integer>       <!-- 改成想要的分鐘 (0-59) -->
</dict>
```

修改後重新加載：
```bash
launchctl unload ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
launchctl load ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist
```

---

## ✅ 完成確認清單

完成以下所有步驟後，自動化就會正式啟動：

- [ ] 1. 生成了 GitHub Personal Access Token
- [ ] 2. 執行 `git push origin main` 並儲存了凭證
- [ ] 3. 執行 `launchctl load ~/Library/LaunchAgents/com.steeltrending.autoupdate.plist`
- [ ] 4. 手動測試了 auto_update.sh 腳本
- [ ] 5. 驗證了日誌輸出

完成後，**鋼鐵潮流網站就會每天自動更新**，無需您再手動操作！

---

## 🆘 故障排除

### 問題 1: 任務未執行

**檢查**:
```bash
# 查看任務狀態
launchctl list com.steeltrending.autoupdate

# 查看錯誤日誌
cat ~/Documents/GitHub/steeltrending.github.io/logs/launchd_error.log
```

**常見原因**:
- 凭證未正確儲存（重新執行 git push）
- 腳本權限不正確（執行 `chmod +x ~/Documents/GitHub/steeltrending.github.io/auto_update.sh`）

### 問題 2: "找不到圖卡文件"

**檢查源文件夾**:
```bash
ls ~/Desktop/AI專案資料夾/鋼鐵日報/$(date '+%Y%m%d')/
```

---

祝您設置順利！有任何問題請參考上述故障排除部分。
