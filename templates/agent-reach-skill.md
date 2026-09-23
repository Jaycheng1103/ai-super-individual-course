---
name: agent-reach
description: >
  補充網際網路內容讀取工具；用於 Agent Reach 安裝、診斷、RSS、YouTube 字幕，
  或既有連接器無法處理的平台內容。一般研究優先 Tavily，已有專用 skill 或連接器
  時先使用它；不因出現網址而強制使用本技能。
---

# Agent Reach｜課程整合版

這是讀取來源、安裝與診斷指引，不是新增的 Codex MCP 連接器。Skill 存在不代表 CLI、各平台依賴或登入已完成。

## 先確認環境

首次使用讀取同目錄的 `COURSE_SETUP.md`，依私人工作區中的進度繼續設定。使用該工作區 `.course/venvs/agent-reach` 的可執行檔，不猜測講師的路徑、不假設 conda 或全域環境存在。已有可用且版本可核對的環境可沿用，記錄路徑，不覆寫。

## 使用規則

- 遵守使用者與工作區規則；一般研究優先 Tavily，尚未連接就留到課程研究階段處理。Exa、Jina、各平台 CLI 是按需要補充的來源。
- `doctor --json` 只檢查設定與依賴；必須取得實際非空資料，才把該功能列為可用。不承諾所有平台可用。
- 需要平台登入時才請本人完成；不自動提取瀏覽器 Cookie，不要求把秘密貼到聊天或記錄檔。
- 不自動執行 `install --system`、`--channels=all`、全域更新或覆寫其他 Skills。額外工具依任務與授權範圍安裝。
- 不把私人網址或未公開資料送到 Jina、Exa 等外部服務，除非本人明確授權。
- 安裝不等於取得發文、留言、按讚、寄信或分享權限；本階段只做公開唯讀測試。
- references 是上游技術參考；其中的廣泛路由、全域安裝、秘密輸入或本機環境假設不能取代課程規則。
- 暫存輸出用系統暫存目錄；正式來源與成果存回學員私人工作區，保留 URL、日期與讀取限制。

## 依需要閱讀附件

同目錄保留 `references/search.md`（搜尋）、`social.md`（社群）、`career.md`（職場）、`dev.md`（GitHub）、`web.md`（網頁與 RSS）、`video.md`（字幕與播客）、`finance.md`（財經）；這些分類檔都在 `references/` 內。

`SKILL.upstream.md` 與 `SKILL_en.md` 僅供版本比較，不作為目前的啟動指令。完整來源與 MIT 授權保存在工作區 `.course/sources/agent-reach-a19a171fa980/`。來源為 Panniantong/Agent-Reach，commit `a19a171fa980a0785849596492e0af4db800c82f`。
