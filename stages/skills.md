# 07｜安裝行銷與創作能力

階段 ID：`skills`。課堂依據：C4382，13:50–16:53。時間碼為各支影片內位置。Agent Reach 是講師於 2026-09-22 新增的實作項目。

## 現在要做什麼

1. 依序安裝 Marketing Skills、Agent Reach 與內容三件組。
2. 讀回技能及附件；完成 Agent Reach CLI 設定、公開資料讀取與內容規劃測試。

## 需要學員提供

- 目前使用的 agent。
- 下一步要做的內容類型。

## AI 帶領步驟

在教材目錄按 agent 選 codex 或 claude-code：

```sh
python3 scripts/course.py install --workspace "../my-ai-workspace" --component marketing --agent codex
python3 scripts/course.py install --workspace "../my-ai-workspace" --component agent-reach --agent codex
python3 scripts/course.py install --workspace "../my-ai-workspace" --component content --agent codex
python3 scripts/course.py verify --workspace "../my-ai-workspace"
```

依序安裝行銷包、Agent Reach 及 fb-post-writer、reels-script-writer、ig-carousel-writer。完整附件、共用 tools 與授權會保留；同名不同內容會停止，先比較客製內容。

接著依 [Agent Reach 設定與驗收](../docs/agent-reach.md) 安裝隔離 CLI，完成診斷與一次公開 RSS 讀取。helper 只準備 Skill 檔案，不會執行下載的程式；AI 需接續完成 CLI 步驟，不能把檔案完整檢查當成功能測試。若有阻塞，記錄下一步並保留既有成果。已通過此階段的舊學員只補 Agent Reach，不重做訪談或其他套件。

重新載入 agent，讀回選用 SKILL.md 及 references。先用學員的工作目標產出一份三種內容的用途規劃，確認能選到正確技能。安裝行銷包不代表已取得廣告、付款或客戶系統權限。說人話技能留到草稿完成之後安裝。

## 留下什麼、做到什麼才算完成

建議檔案：`.course/installed.json`。已有自己的命名與結構就沿用，在進度中記錄實際位置。

- agent 能讀取指定 SKILL.md 及 references。
- Agent Reach CLI 可執行；公開 RSS 回傳非空標題與網址，結果存入 `.course/agent-reach-check.md`，附版本與未設定平台。
- 用真實工作目標產出一份內容規劃。

## 中途停下來

每完成一個動作或收到一題回答，就保存實際檔案、目前步驟、下一個動作與阻塞原因。訪談另外保存下一題；檔案與答案留在私人工作區。恢復時先讀這些記錄，再接續，不重跑已驗收的步驟。命令見 [START_HERE](../START_HERE.md)。
