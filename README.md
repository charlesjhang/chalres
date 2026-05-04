# 查爾斯影像｜商業攝影管理系統（MVP 啟動版）

這份文件是第一版「可落地開工」規格，目標是在 14 天內完成可用的 MVP，先解決：

- 客戶資料集中化
- 案件流程可追蹤
- 報價與收款可管理
- 交付節點可查詢
- 每週可產出營運摘要

---

## 1) MVP 範圍（第一階段）

第一版先做 5 個核心頁面：

1. 客戶資料庫（Customers）
2. 案件看板（Projects + Tasks）
3. 報價管理（Quotes）
4. 收款管理（Payments）
5. 營運總覽 Dashboard（基本 KPI）

> 原則：先做「能賺錢、能收款、能交付」的流程，再做進階大屏與 AI 助理。

---

## 2) 資料表設計（MVP 7 張表）

以下欄位可直接用於 Airtable / Supabase。

### A. `customers`（客戶主檔）

- `id` (uuid, pk)
- `name` (text, required)
- `type` (enum: `B2B` / `B2C`, required)
- `industry` (text)
- `contact_name` (text)
- `phone` (text)
- `line_id` (text)
- `email` (text)
- `source` (enum: `IG` / `Website` / `BNI` / `Referral` / `Ads` / `Partner` / `Other`)
- `tier` (enum: `A` / `B` / `C` / `Strategic`)
- `status` (enum: `active` / `inactive` / `lost`)
- `last_contact_at` (date)
- `total_revenue` (number, default 0)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

### B. `leads`（詢問與潛在客戶）

- `id` (uuid, pk)
- `customer_id` (fk -> customers.id, nullable)
- `lead_name` (text, required)
- `source` (same as customers.source)
- `need_type` (enum: `商品攝影` / `人像` / `美食` / `影片` / `AI合成` / `其他`)
- `budget_range` (enum: `<10k` / `10k-30k` / `30k-50k` / `50k+`)
- `status` (enum: `新詢問` / `已回覆` / `已報價` / `追蹤中` / `已成交` / `已流失`)
- `lost_reason` (text)
- `next_followup_at` (date)
- `owner` (text)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

### C. `projects`（案件主檔）

- `id` (uuid, pk)
- `customer_id` (fk -> customers.id, required)
- `lead_id` (fk -> leads.id, nullable)
- `name` (text, required)
- `project_type` (enum: `商品攝影` / `人像` / `美食` / `影片` / `AI合成` / `其他`)
- `owner` (text)
- `shoot_date` (date)
- `due_date` (date)
- `status` (enum: `待拍攝` / `拍攝中` / `修圖中` / `待交付` / `已結案`)
- `quoted_amount` (number, default 0)
- `cost_amount` (number, default 0)
- `drive_link` (url)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

### D. `tasks`（案件任務）

- `id` (uuid, pk)
- `project_id` (fk -> projects.id, required)
- `stage` (enum: `需求確認` / `企劃` / `拍攝準備` / `拍攝` / `初選` / `修圖` / `交付` / `結案`)
- `title` (text, required)
- `assignee` (text)
- `due_date` (date)
- `status` (enum: `未開始` / `進行中` / `已完成` / `延遲`)
- `priority` (enum: `low` / `medium` / `high`)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

### E. `quotes`（報價單）

- `id` (uuid, pk)
- `project_id` (fk -> projects.id, required)
- `quote_no` (text, unique)
- `version` (int, default 1)
- `amount` (number, required)
- `status` (enum: `草稿` / `已送出` / `待修改` / `已確認` / `已取消`)
- `sent_at` (datetime)
- `confirmed_at` (datetime)
- `valid_until` (date)
- `cancel_reason` (text)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

### F. `payments`（收款）

- `id` (uuid, pk)
- `project_id` (fk -> projects.id, required)
- `payment_type` (enum: `訂金` / `尾款` / `其他`)
- `amount` (number, required)
- `status` (enum: `待收款` / `已收款`)
- `due_date` (date)
- `paid_at` (datetime)
- `method` (enum: `現金` / `轉帳` / `LINE Pay` / `信用卡` / `其他`)
- `invoice_status` (enum: `未開` / `已開` / `免開`)
- `note` (text)
- `created_at`, `updated_at` (timestamp)

### G. `deliveries`（交付）

- `id` (uuid, pk)
- `project_id` (fk -> projects.id, required)
- `version` (text, ex: `V1`, `V2`, `Final`)
- `delivery_date` (datetime)
- `content_summary` (text)
- `link` (url)
- `client_confirm_status` (enum: `未確認` / `已確認` / `需修改`)
- `revision_count` (int, default 0)
- `license_scope` (text)
- `notes` (long text)
- `created_at`, `updated_at` (timestamp)

---

## 3) 三條核心狀態流程（先定死）

### Lead Funnel

`新詢問 -> 已回覆 -> 已報價 -> 追蹤中 -> 已成交 / 已流失`

### Project Pipeline

`待拍攝 -> 拍攝中 -> 修圖中 -> 待交付 -> 已結案`

### Payment Pipeline

`待收款(訂金) -> 已收訂金 -> 待收尾款 -> 已收清`

---

## 4) 自動化流程（n8n / Make）

### Flow 1：新案件建立自動建資料夾

觸發：`projects` 新增紀錄

動作：
1. 在 Google Drive 建立 `客戶_案件_日期` 資料夾
2. 自動建立 8 個子資料夾（客供、企劃、RAW、初選、精修、確認、交付、合約）
3. 將資料夾 URL 回寫到 `projects.drive_link`

### Flow 2：報價追蹤提醒

觸發：`quotes.status = 已送出`

動作：
- 第 3 天無回覆：提醒追蹤
- 第 7 天無回覆：二次提醒
- 第 14 天無回覆：更新為 `待修改` 或標記風險

### Flow 3：尾款提醒

觸發：`payments.status = 待收款` 且 `due_date` 到期

動作：
- 每日固定時間提醒負責人
- 逾期 3 天標紅
- 逾期 7 天升級高風險

---

## 5) Dashboard（V1 必要 KPI）

每週至少追這 8 項：

1. 本月已入帳金額
2. 本月成交金額
3. 應收款總額
4. 本月新詢問數
5. 報價成交率
6. 進行中案件數
7. 3 日內待交付案件數
8. 準時交付率

KPI 計算範例：

- 報價成交率 = `已確認報價數 / 總送出報價數`
- 準時交付率 = `準時交付案件數 / 總交付案件數`
- 應收款 = `status=待收款 的 payments.amount 加總`

---

## 6) 14 天啟動計畫

### Day 1-2
- 建立 7 張資料表與欄位
- 鎖定 enum 狀態值

### Day 3-5
- 完成客戶頁、案件看板、報價頁、收款頁

### Day 6-8
- 串接 3 條自動化流程（Drive / 報價提醒 / 尾款提醒）

### Day 9-11
- 建立 Dashboard V1（8 KPI）

### Day 12-14
- 實際試跑 1 週資料
- 移除無用欄位
- 輸出 v1.0 SOP

---

## 7) 技術選型建議

### 快速上線（推薦）
- 資料：Airtable
- 自動化：Make 或 n8n
- 報表：Looker Studio
- 檔案：Google Drive

### 可擴充版（第二階段）
- Frontend: Next.js
- Backend: Supabase (PostgreSQL/Auth/Storage)
- Automation: n8n
- Dashboard: Metabase 或自建

---

## 8) 下一步（立刻可做）

1. 建立 MVP Base（Airtable 或 Supabase 二選一）
2. 匯入至少 20 筆歷史案件測試資料
3. 跑一輪報價 -> 案件 -> 收款 -> 交付流程
4. 每週固定檢討 KPI，優化狀態與欄位

> 核心原則：不是先做最炫功能，而是先讓資料「每天被正確記錄」。

---

## 9) Repo 內建檔案（可直接使用）

- `sql/schema.sql`：Supabase/PostgreSQL 可直接執行的建表腳本。
- `sql/seed.sql`：最小測試資料。
- `docs/kpi_dictionary.md`：KPI 定義字典。
- `automations/README.md`：三條自動化流程規格。
- `sql/views.sql`：可直接給儀表板使用的營運視圖。
- `sql/queries.sql`：Dashboard 常用查詢片段。
- `docs/setup.md`：資料庫初始化與驗收步驟。
- `supabase/migrations/202605040001_init.sql`：可用於 Supabase 的初始化 migration（含 RLS）。
- `scripts/check_sql_assets.sh`：快速檢查 SQL/文件資產是否齊全。
- `docs/next_steps_backend.md`：第二階段後端實作路線。
- `web/index.html`：前端樣式 Demo（MVP 中控台視覺稿）。

## 10) 前端 Demo 預覽方式

### 本機快速預覽
```bash
bash scripts/preview_web.sh 4173
```

開啟瀏覽器：
- `http://localhost:4173/web/index.html`

### 操作重點（你可以先看這 4 區）
1. 上方 KPI（本月入帳、成交、應收、準時率）
2. 中間案件看板（待拍攝/拍攝中/修圖中/待交付）
3. 右側風險提醒（尾款、交期、報價追蹤）
4. RWD（縮小瀏覽器看手機版排版）
