# 12｜安裝剪輯工作臺與母版

階段 ID：`editor`。課堂依據：C4387，02:38 起。時間碼為各支影片內位置。

## 現在要做什麼

1. 安裝 OpenChatCut 與兩個技能。
2. 連接 MCP、匯入母版並複製工程。

## 需要學員提供

- OS 與 CPU 架構。
- 上一階段原片。

## AI 帶領步驟

留下的成果：能開啟的剪輯工作臺、可連線的 agent，以及一份可編輯母版。

預設走官方桌面安裝檔：https://github.com/0xsline/OpenChatCut/releases/latest 。先判斷 OS 和 CPU 架構，下載對應版本。安裝與系統權限由本人完成；遇作業系統安全警告，不提供關閉安全機制或繞過警告的指令。

若學員明確選擇原始碼安裝，先讀鎖定來源版本 README_ZH.md／package.json；本次確認上游需要 Node.js 24.x，不能直接用未知舊版。依上游步驟在獨立工具資料夾執行 npm install、建立 .env.local、npm run dev。不要把工具程式裝進課程 repo 或背景資料庫。

安裝兩個專案技能：

```sh
python3 scripts/course.py install --workspace "../my-ai-workspace" --component openchatcut --agent codex
python3 scripts/course.py install --workspace "../my-ai-workspace" --component talking-video --agent codex
```

依 openchatcut Skill 的 references/getting-started.md 設定 MCP。預設本機端點 `http://localhost:5199/api/external-mcp/mcp`，若環境不同以正在執行的實例為準。保留現有 agent 設定，不覆蓋整份 config。

啟動工作臺，先呼叫 openchatcut_status 與 list_projects。學員指定測試工程後才進入編輯。使用 manual 審查模式，完成後由本人預覽與批准。工具名稱若變動，以當前 MCP 工具清單和官方說明為準。

在已安裝的 openchatcut-talking-video 資料夾找到 jieshao-portrait-master.ccproj，使用工作臺的 Import project 匯入，再複製成自己的測試工程。保留母版，不直接改資料庫。這份教學母版不含講師影片，不要把預留區當成素材遺失。

驗收：狀態與工程列表可讀；母版中的標題、字幕、重點字與結尾文字可編輯；自己的測試影片能播放。

若這一階段遇到阻塞，保存錯誤種類、已做步驟與下一個動作；不要附上金鑰。完成後依 [接續規則](../START_HERE.md) 保存進度。

## 留下什麼、做到什麼才算完成

建議檔案：`outputs/video/project-notes.md`。已有自己的命名與結構就沿用，在進度中記錄實際位置。

- MCP 狀態與工程列表可讀。
- 母版與自己的素材能在工作臺開啟。

## 中途停下來

每完成一個動作或收到一題回答，就保存實際檔案、目前步驟、下一個動作與阻塞原因。訪談另外保存下一題；檔案與答案留在私人工作區。恢復時先讀這些記錄，再接續，不重跑已驗收的步驟。命令見 [START_HERE](../START_HERE.md)。
