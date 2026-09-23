# 講師分享與維護

直接把 [repo 首頁](https://github.com/Jaycheng1103/ai-super-individual-course) 與首頁啟動句傳給學員。不需要逐一收集 email、邀請協作者或要求 GitHub 登入。

課前依課堂安排建立 Codex 專案、連接 Google 外掛；學員把啟動句交給自己的 AI，由 AI 取得教材、安全安裝 AIS-OS 並開始訪談。自學者尚未完成課前準備時，依環境階段補齊。

公開閱讀不等於取得主庫寫入權限，學員不需成為 collaborator。個人背景、作品、API key 與 `.course` 都留在自己的私人工作區，不放進 GitHub issues、PR 或公開 repo。

## 維護版本

- 教材、流程地圖、來源與腳本一起版本管理。完整書稿與 PDF 獨立保存，不加入這個 repo。
- 公開版不含舊私人庫的提交歷史。更新時不要把舊私人分支合併或推送到這裡。
- 來源固定 commit 與 archive SHA-256，改版後先做隔離安裝與功能測試。
- 助教只收集階段、作業系統、agent 及遮蔽敏感資訊的錯誤摘要，不收集金鑰。
- 維護前執行 `python3 -m unittest discover -s tests -v` 與 `python3 scripts/validate_repo.py`。
- 原創程式與教材採 MIT；第三方工具、商標與素材依原作者授權，不因本 repo 開源而重新授權。

已有私人版教材的學員請依 [取得與更新指引](get-access.md) 換到新版，保留個人進度與成果。
