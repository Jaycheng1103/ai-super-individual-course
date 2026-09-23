# Agent Reach｜與行銷技能一起安裝

本項為講師 2026-09-22 新增。AI 在第 7 階段安裝 Marketing Skills 後接著處理，不需要學員另開一堂設定流程。用途是補充網頁、RSS、影片字幕等來源讀取；登入社群與其他額外平台等實際需要時再設定。

## 1. 安裝 Skill 並讀回

先執行本階段的 `--component agent-reach` 指令。helper 會核對來源 SHA-256，保留完整上游原件與 MIT 授權，再裝入課程整合版 Skill、原始 Skill 與全部 references。同名客製版本先比較，不覆寫。

讀回安裝後的 `SKILL.md` 和 `references/web.md`，必要時重新載入 agent。整合版保留 Tavily 優先、學員自己的環境與授權範圍，不套用上游特定電腦的 conda 設定。

## 2. AI 接著安裝隔離 CLI

先確認 Python 3.10 以上。以下指令在**學員私人工作區根目錄**執行，不能在教材 repo 目錄執行。使用前確認 `.course/sources/agent-reach-a19a171fa980` 已由 helper 下載驗證。安裝 Python 套件會連到套件站下載依賴；不需要 API key。上游來源固定，Python 依賴仍由安裝當下解析。

先檢查是否已有可用環境；若已有，核對其版本與來源，沿用並記錄，不重新建立。全新環境在 macOS／Linux：

```sh
python3 -m venv .course/venvs/agent-reach
.course/venvs/agent-reach/bin/python -m pip install ./.course/sources/agent-reach-a19a171fa980
.course/venvs/agent-reach/bin/agent-reach --version
.course/venvs/agent-reach/bin/agent-reach doctor --json
```

Windows PowerShell：

```powershell
py -3 -m venv .course/venvs/agent-reach
& ./.course/venvs/agent-reach/Scripts/python.exe -m pip install ./.course/sources/agent-reach-a19a171fa980
& ./.course/venvs/agent-reach/Scripts/agent-reach.exe --version
& ./.course/venvs/agent-reach/Scripts/agent-reach.exe doctor --json
```

不需要修改系統 Python 或啟用整個 venv。若 Python／venv 不可用，依實際錯誤帶學員處理，不用 sudo 或跳過系統保護。不要為了讓診斷全綠，自動安裝所有平台、讀取瀏覽器登入資訊或執行 `--system`。

## 3. 實際讀一次公開 RSS

用上一步 venv 的 Python 執行下面程式；AI 可存成私人工作區 `.course/check-agent-reach.py` 再執行。這會直連上游公開 GitHub Releases RSS，不傳送私人資料，也不使用學員 Cookie 或付費 API。

```python
import json
import urllib.request
import feedparser
url = 'https://github.com/Panniantong/Agent-Reach/releases.atom'
req = urllib.request.Request(url, headers={'User-Agent': 'AI-Course-Check/1.0'})
with urllib.request.urlopen(req, timeout=30) as response:
    feed = feedparser.parse(response.read())
items = [{'title': e.get('title', ''), 'url': e.get('link', '')}
         for e in feed.entries[:3]]
assert items and all(e['title'] and e['url'] for e in items), '未取得有效 RSS 條目'
print(json.dumps({'source': url, 'items': items}, ensure_ascii=False, indent=2))
```

讀回輸出至少一筆非空標題與網址。來源暫時不可用就記錄阻塞與下一步，不把有安裝 feedparser 當作測試成功。RSS 通過只表示此讀取流程可用，不能推論 YouTube 或社群平台也已通過。之後需要字幕時，再依 `references/video.md` 核對 yt-dlp、JavaScript runtime 與公開影片實測；不預設本機 Node 路徑。

## 4. 保存與接續

將來源 commit、CLI 版本、實際執行檔路徑、測試日期、RSS 標題及網址、未設定的平台存入私人工作區 `.course/agent-reach-check.md`。診斷若包含私人設定，只記必要狀態，不保存秘密。使用課程的 checkpoint 指令記錄下一步。

驗收需同時具備：Skill 與附件可讀、CLI 可執行、公開 RSS 取得非空資料。通過後接續內容三件組與內容規劃，不提前要求申請所有平台帳號。已完成第 7 階段的舊學員只補這一項，保留既有作品與其他完成紀錄。
