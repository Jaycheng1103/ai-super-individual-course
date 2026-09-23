# 03｜建立 AI 第二大腦

階段 ID：`workspace`。課堂依據：C4378，00:00–03:06。時間碼為各支影片內位置。

## 現在要做什麼

1. 安裝 AIS-OS 並讀回六個技能。
2. 在私人庫完成檔案寫入與讀回。

## 需要學員提供

- 沿用目前 Codex 專案；只有路徑不明時才詢問。

## AI 帶領步驟

預設學員已在 Codex 開啟課程專案，直接在這個專案建立第二大腦，不再選新資料夾。教材 repo 可放在該專案內的獨立子目錄；背景與作品不得放進教材 repo。

AI 先讀目前專案的規則和檔案；已存在第二大腦時依 [接入流程](../docs/existing-workspace.md) 接續。只有新課程專案才執行下列命令。範例假設教材位於目前專案的 ai-super-individual-course 子目錄，執行時須換成已核對的實際路徑：

```sh
python3 ai-super-individual-course/scripts/course.py init --workspace "." --in-place
```

Windows 可改用 py -3。工具下載鎖定 AIS-OS 來源並檢查 SHA-256；寫入前核對所有頂層檔案及資料夾，有同名衝突就整批停止，不覆寫、不自動合併。與 AIS-OS 無關的既有檔案原樣保留；有 AGENTS.md、CLAUDE.md、.agents、.gitignore 等衝突時先比較原件，依既有工作區流程整合，不能為了安裝成功刪掉它們。

安裝後重新載入目前專案的技能，檢查 onboard、audit、grill-me、link、level-up、3d-brain 及附件。寫入中性測試檔再讀回。保存環境與外掛準備紀錄，依各階段驗收回填 environment、connectors、workspace；外掛功能仍可標為未測。

接著直接讀 onboard，開始背景訪談。不要在開始前要求學生先找 Drive 文件、郵件或行程。安裝成功只代表本機檔案準備完成，仍須讀回與載入檢查。

尚無專案的自學者可用 init --workspace 指定不存在的新目錄，不加 --in-place；start 只供需要先保存安裝前進度者使用。已有進度不可重跑初始化。

## 留下什麼、做到什麼才算完成

建議檔案：`AGENTS.md`、`CLAUDE.md`、`aios-intake.md`。已有自己的命名與結構就沿用，在進度中記錄實際位置。

- 六個技能與附件存在。
- 學員能開啟自己的資料與測試摘要。

## 中途停下來

每完成一個動作或收到一題回答，就保存實際檔案、目前步驟、下一個動作與阻塞原因。訪談另外保存下一題；檔案與答案留在私人工作區。恢復時先讀這些記錄，再接續，不重跑已驗收的步驟。命令見 [START_HERE](../START_HERE.md)。
