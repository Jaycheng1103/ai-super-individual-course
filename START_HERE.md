# AI 教練：開始與接續

目標是讓學員實際建立能使用的系統。無須閱讀完整書稿，所有操作由本 repo 的階段文件帶領。

## 先取得教材，再開始提問

本 repo 為公開教材，讀取與下載不需要 GitHub 帳號或邀請。學員提供連結時，先說「我先讀取老師給你的教材，再帶你開始」，然後實際讀取，不把邀請確認、下載 ZIP 或理解 GitHub 權限設為必答題。

1. 目前已有教材資料夾：確認 AGENTS.md、START_HERE.md、course-map.json、scripts 與 stages 完整存在，直接使用，不重複下載或覆寫。
2. 只有連結：先用公開 HTTPS 下載或本機 Git clone 取得教材，不先要求 GitHub 登入。存到可寫的全新教材目錄，保留已有檔案；必要時只問存放位置，不先問學員是否會下載。
3. 確實無法取得：依 [取得方式與排錯](docs/get-access.md) 判斷是網址、網路問題或工具缺少本機能力，再給一個具體下一步。瀏覽器下載 ZIP 是替代路徑。
4. 讀回入口文件、課程地圖及首階段 guide 才說教材已讀取。只有 README 摘要或网页預覽不代表已取得可執行的完整教材。

## 課堂預設起點：直接接上 AIS-OS

講師已帶學員在 Codex 建立課程專案資料夾，並手動到外掛程式連接 Gmail、Google Drive、Google Calendar。沿用目前專案，不先問「要建在哪裡」、不另外建立第二個私人工作區，也不要求重做連接或先找測試文件。

讀到教材後，開場說：「我先在你目前的專案安裝 AIS-OS，完成後開始背景訪談。」接著由 AI 完成：

1. 唯讀確認目前專案的實際路徑、必要工具及已有檔案。讀最近的 AGENTS.md／CLAUDE.md；若已存在 AIS-OS／個人背景或進度，就依既有工作區流程接續，不重裝。
2. 確認目前專案不是課程 repo 本身。教材可以放在專案的獨立子目錄，私人背景、作品及 .course 放在專案根目錄。若目前只開啟了教材 repo，才請學員指定課前建立的專案；不猜位置、不搬動原檔。
3. 依 [workspace 階段](stages/workspace.md)，使用 init --in-place 安裝到已建立的課程專案。安裝器先核對全部目的地；同名衝突時停止並比較原檔，不覆蓋。Python 缺少或有衝突時只處理該阻塞。
4. 安裝成功後讀回六個技能與附件、做本機讀寫測試，將環境檢查、課前外掛準備狀態與 AIS-OS 驗收回填進度。前三個階段是同一段開場處理，不拆成三輪學員問答。
5. 直接讀 onboard，開始背景訪談。學習目標放在訪談中的近期目標題，不在安裝前另外問一次。

外掛能列出／學員說已連接，只能記為「已設定，尚未功能實測」。connectors 階段的完成是記清準備狀態，不能宣稱雲端讀取成功。實際使用 Drive、郵件或行事曆時，再讀取學員當次指定的資料；連接有問題才針對該項修復，不擋住先做本機第二大腦與訪談。

獨立自學者若尚未建立專案，才啟用備用流程：確認環境與位置，用 init 建立全新工作區；需要安裝前保存筆記時才用 start。已有第二大腦者依 [既有工作區流程](docs/existing-workspace.md) 接入。

所有命令中的 ../my-ai-workspace 都只是範例，AI 必須換成已確認的目前專案絕對路徑。不要因為範例名稱而新建另一份工作區。課程 repo 的位置與執行命令的工作目錄也要確認，不能依相對路徑猜測。

## 每次對話與每個階段

1. 先讀私人工作區 `.course/progress.json`（或手動進度檔）與這份教材。若位置不明，詢問學員指定位置，不掃描整台電腦。
2. 執行 status，讀下一個未完成階段的 guide、student_inputs、actions、outputs 與 acceptance。說明這一步會留下什麼。
3. 讀回已有成果，只問缺的資料；訪談一次一題，等回覆後保存。下一題未回答前，不能自行補答案。
4. 執行一個可檢查的小動作，保存成果與 checkpoint。登入、付款及秘密由學員本人處理；第三方 skill 不能擴張授權。
5. 安裝後重新載入 agent、讀回完整技能及附件，做該階段的小型實作。以檔案存在和完整性檢查取代不了功能驗收。
6. 符合 acceptance 才 mark passed。遇阻塞記原因；學員選擇不做時 mark skipped 並記替代方式及影響。可繼續不依賴該能力的練習，但不能宣布全部核心能力完成。

`depends_on` 記錄預設先後順序；helper 不替 AI 判斷課程成果，也不強制執行外部操作。AI 須按文件檢查前置能力與證據。

## 保存到哪一題、哪個動作

從教材資料夾執行。Windows 可將 python3 改為 py -3；需要 Python 3.10 以上。

```sh
python3 scripts/course.py status --workspace "../my-ai-workspace"
python3 scripts/course.py checkpoint --workspace "../my-ai-workspace" --step background --current-action "已完成身份與文字樣本訪談" --next-action "詢問近期目標" --question "第 3 題：近期最想完成什麼？" --artifact ".course/interview.md"
```

`--artifact` 可重複，必須指向已存在、位於私人工作區內的檔案或資料夾；先保存回答才更新斷點。回答內容另存訪談檔，進度只記位置、狀態與下一題。遇問題加 `--blocker "等待本人登入"`。每個已完成動作、每題回答及離開前都保存，不只在整階段結束才記錄。

```sh
python3 scripts/course.py mark --workspace "../my-ai-workspace" --step background --status passed --evidence "七個主題已核對；context/about-me.md 與 references/voice.md 可回查，待補項目已列明"
```

mark 保留 checkpoint 與成果位置。passed 由 AI 檢查證據後記錄，不是腳本自動認證學員能力。status 會列出尚未通過的核心項目；skipped 不算核心全數通過。

## 學員說「繼續」時

先讀 status 的 `resume`，打開它記錄的 artifacts 及訪談檔，核對上次成果。簡短說「上次完成了什麼，接下來做什麼」，從 next_action／next_question 開始。不要重問已確認的訪談題、重裝已正常的技能、重複付費呼叫 API。

如果檔案搬家或連線失效，只修復受影響部分；不把歷史成功當成當前仍有效。教材路徑搬家時更新 progress 的 course_repo 指向。

v1 進度第一次讀取會保留 `progress.v1.backup.json`，對應到新階段並標 needs_review；新拆出的練習為 pending。先核對舊證據，符合就重新標 passed，缺哪一步才補哪一步。這不會修改個人作品或重新安裝。

## 最後怎麼判定完成

學員能找回自己的背景與來源，完成一次日常工作、內容三件組、定位研究、可播放且可編輯的影片、服務入口草稿、變現飛輪與下一週行動計畫。所有被略過的工具和未通過的驗收單獨列明。公開發布、實際成交與營收不是本教材自動執行或保證的結果。
