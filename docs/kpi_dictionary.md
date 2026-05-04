# KPI Dictionary (V1)

1. 本月已入帳金額 = `payments.status='已收款'` 且 `paid_at` 在本月的 `amount` 加總。
2. 本月成交金額 = `quotes.status='已確認'` 且 `confirmed_at` 在本月的 `amount` 加總。
3. 應收款總額 = `payments.status='待收款'` 的 `amount` 加總。
4. 本月新詢問數 = `leads.created_at` 在本月的筆數。
5. 報價成交率 = `已確認報價數 / 已送出報價數`。
6. 進行中案件數 = `projects.status in ('待拍攝','拍攝中','修圖中','待交付')` 的筆數。
7. 3日內待交付案件數 = `projects.due_date <= current_date + 3` 且狀態非`已結案`。
8. 準時交付率 = `準時交付案件數 / 總交付案件數`。
