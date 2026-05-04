# Setup (Supabase / PostgreSQL)

## 1) 初始化資料庫
1. 一般 Postgres：依序執行 `sql/schema.sql`、`sql/views.sql`、`sql/seed.sql`。
2. Supabase Migration：直接套用 `supabase/migrations/202605040001_init.sql`。
3. 若 schema 或 view 有異動，先執行 `scripts/build_supabase_migration.sh` 重新產生 migration。

## 2) 驗收檢查
- `quotes` 可新增草稿、送出與確認狀態
- `payments` 可新增訂金/尾款並標記收款
- `v_project_finance` 可正確計算每案應收與毛利
- `v_due_risks_7d` 可正確標示逾期/近3天/近7天

## 3) Dashboard 串接
可直接使用 `sql/queries.sql` 的查詢，先完成：
- 本月已入帳
- 本月成交
- 應收款
- 3日內待交付
