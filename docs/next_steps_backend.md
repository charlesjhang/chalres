# Backend Next Steps (Phase 2)

## 1) 身份與權限
- 建立 `teams`, `team_members`, `user_profiles`。
- 將目前暫時性 RLS (`authenticated can all`) 改為「同團隊隔離」。

## 2) 核心 API
- 建立 `rpc_mark_project_delivered(project_id uuid)`：
  - 自動更新案件狀態
  - 檢查尾款是否未收
  - 產生回訪任務（14/30/90 天）

## 3) 自動化可觀測性
- `automation_runs` 表記錄每次流程執行結果。
- 失敗時寫入錯誤訊息並告警。

## 4) 測試
- 加上 migration test（CI）
- 加上 KPI SQL snapshot test（每月口徑不被改壞）
