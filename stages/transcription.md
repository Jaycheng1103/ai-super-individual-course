# 15｜ElevenLabs 設定與轉錄

階段 ID：`transcription`。課堂依據：C4388，24:20–41:13。時間碼為各支影片內位置。

## 現在要做什麼

1. 建立最小需要權限並測試轉錄。
2. 回聽校對；需要時另設定剪輯工作臺。

## 需要學員提供

- 自己的 ElevenLabs 帳號。
- 允許上傳的 10–20 秒聲音樣本。

## AI 帶領步驟

留下的成果：自己的短音訊與一份已回聽核對的轉錄。

由學員登入 ElevenLabs 建立自己的 API key，啟用這次語音轉文字所需權限。音樂、音效與音色是另外的功能和用量，不一次全開。方案、額度以官方當下資訊為準。

本機測試工具的設定方式：

```sh
python3 scripts/connections.py configure --workspace "../my-ai-workspace" --service elevenlabs
```

由本人在終端輸入，不從聊天或剪貼簿自動讀取。先準備一段 10–20 秒、可傳給 ElevenLabs 的本人聲音，檔案小於 10 MB。說明這次會上傳這段音訊且可能計費，取得同意後執行：

```sh
python3 scripts/connections.py check --workspace "../my-ai-workspace" --service elevenlabs --audio "../my-ai-workspace/sample.wav" --allow-usage --allow-upload
```

本工具使用官方 speech-to-text 端點與 scribe_v2，結果保存在 `.course/checks/elevenlabs-transcript.json`，不把整段轉錄印到 console。請學員回聽並核對工具名、人名與數字。

若在 OpenChatCut 裡使用轉錄，仍需在它的設定入口配置自己的服務；本 helper 成功不代表剪輯工作臺自動讀到同一把金鑰。不要把兩種設定混在一起。

驗收：音訊確實回傳逐字稿，且本人完成一次校對；若要接剪輯工作臺，再在工作臺完成一次短片轉錄。

若這一階段遇到阻塞，保存錯誤種類、已做步驟與下一個動作；不要附上金鑰。完成後依 [接續規則](../START_HERE.md) 保存進度。

## 留下什麼、做到什麼才算完成

建議檔案：`.course/checks/elevenlabs-transcript.json`。已有自己的命名與結構就沿用，在進度中記錄實際位置。

- 短音訊真實回傳逐字稿並經本人核對。
- helper 與剪輯工作臺設定狀態分別記錄。

## 中途停下來

每完成一個動作或收到一題回答，就保存實際檔案、目前步驟、下一個動作與阻塞原因。訪談另外保存下一題；檔案與答案留在私人工作區。恢復時先讀這些記錄，再接續，不重跑已驗收的步驟。命令見 [START_HERE](../START_HERE.md)。
