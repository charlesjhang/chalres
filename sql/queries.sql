-- Dashboard query snippets

-- 1) 本月已入帳金額
select coalesce(sum(amount),0) as received_this_month
from payments
where status = '已收款'
  and date_trunc('month', paid_at) = date_trunc('month', now());

-- 2) 本月成交金額
select coalesce(sum(amount),0) as won_quote_amount_this_month
from quotes
where status = '已確認'
  and date_trunc('month', confirmed_at) = date_trunc('month', now());

-- 3) 應收款總額
select coalesce(sum(amount),0) as receivable_total
from payments
where status = '待收款';

-- 4) 3日內待交付案件
select id, name, due_date, status
from projects
where status <> '已結案'
  and due_date <= current_date + 3
order by due_date asc;
