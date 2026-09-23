# 讓 AI 取得公開教材

本 repo 可以匿名閱讀、下載與 clone，不需要 GitHub 邀請或帳號。將連結與首頁啟動句交給 AI，由 AI 取得完整教材。

## AI 取得方式

已有本機教材就先讀回，保留既有修改，不重複下載。只有連結時，在目前專案中選擇尚不存在的教材子目錄，再執行：

```sh
git clone https://github.com/Jaycheng1103/ai-super-individual-course.git ./ai-super-individual-course
```

沒有 Git 時，可使用公開的 [完整 ZIP](https://github.com/Jaycheng1103/ai-super-individual-course/archive/refs/heads/main.zip)，或瀏覽器 Code → Download ZIP，解壓完整資料夾。不需要為了下載教材安裝 gh 或登入 GitHub。

取得後讀回 AGENTS.md、START_HERE.md、course-map.json、scripts 與 stages。只有 README 預覽不代表已取得可執行的完整教材。教材與私人第二大腦分開；不要把背景訪談、作品、金鑰或進度提交到公開 repo。

## 只有實際失敗才排錯

| 問題 | 下一步 |
|---|---|
| 工具要求 GitHub 登入 | 改用公開 HTTPS／ZIP；某個連接器要求登入不代表教材需要權限 |
| 404 或找不到 repo | 核對完整網址與 main 分支；用公開網頁重試，不要求學員接受邀請 |
| 網路或 TLS 錯誤 | 處理連線與憑證，不關閉驗證、不把網路問題當成帳號問題 |
| agent 無法操作本機檔案 | 帶學員開啟有本機讀寫與執行能力的 AI 工具，不宣稱已安裝 |
| 目的地已存在 | 核對原檔與進度，保留修改；不刪除後重新 clone |

## 更新與接續

新版公開庫從乾淨歷史開始，不包含完整書稿或 PDF。曾 clone 私人版的學員，請下載公開版到新的教材目錄，不用 force pull，也不合併舊私人歷史到公開庫。私人工作區、作品與 `.course` 留在原位；AI 核對後更新進度中的 course_repo 位置，接續原階段。

已經使用公開版者，先確認 git status 無自己的修改，再 git pull --ff-only；ZIP 使用者下載到新版本目錄。已有修改時先比較，不覆寫。
