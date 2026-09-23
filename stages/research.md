# 10｜Tavily 串接與定位研究

階段 ID：`research`。課堂依據：C4385，00:00–22:23。時間碼為各支影片內位置。

## 現在要做什麼

1. 設定與測試 Tavily。
2. 研究 1–3 個競品，整理定位及產品假設。

## 需要學員提供

- 服務對象與研究問題。
- 自己的 Tavily 帳號及使用選擇。

## AI 帶領步驟

留下的成果：一次成功的公開搜尋與一份有來源的一頁研究。

學員到 Tavily 官方網站註冊，依當下方案建立自己的 API key。若 agent 已有官方 Tavily plugin，直接使用其設定入口；不要因為有官方插件就假定已有金鑰。

沒有現成入口時，提供本 repo 的本機測試工具。由學員在互動式終端執行，輸入不顯示：

```sh
python3 scripts/connections.py configure --workspace "../my-ai-workspace" --service tavily
```

金鑰保存在私人工作區 `.course/secrets`，這只是本機檔案保護，不是加密。不要把工作區同步到共用 Git。原生 agent plugin 需要的設定與這個測試 helper 是分開的。

說明這次會傳送公開測試問題至 Tavily，可能耗用額度，得到學員同意後執行：

```sh
python3 scripts/connections.py check --workspace "../my-ai-workspace" --service tavily --allow-usage
```

成功後用 prompts/classroom.md 的競品研究指令，找 1–3 個同客群服務提供者，閱讀官方原頁，整理對象、問題、交付、公開價格、來源日期及未找到事項。AI 的推論另寫一欄。

驗收：公開搜尋取得網址；研究每個主要結論可回原頁，未公開價格不猜。HTTP 401／403 查金鑰與權限，429 查額度；不反覆自動重試付費請求。

若這一階段遇到阻塞，保存錯誤種類、已做步驟與下一個動作；不要附上金鑰。完成後依 [接續規則](../START_HERE.md) 保存進度。

## 留下什麼、做到什麼才算完成

建議檔案：`outputs/research/positioning.md`。已有自己的命名與結構就沿用，在進度中記錄實際位置。

- 每項主要事實有原始網址與日期。
- 定位與價格提案標為待驗證假設。

## 中途停下來

每完成一個動作或收到一題回答，就保存實際檔案、目前步驟、下一個動作與阻塞原因。訪談另外保存下一題；檔案與答案留在私人工作區。恢復時先讀這些記錄，再接續，不重跑已驗收的步驟。命令見 [START_HERE](../START_HERE.md)。
