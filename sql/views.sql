-- Operational views for dashboard

create or replace view v_project_finance as
select
  p.id as project_id,
  p.name as project_name,
  c.name as customer_name,
  p.quoted_amount,
  coalesce(sum(case when pm.status = '已收款' then pm.amount else 0 end), 0) as received_amount,
  coalesce(sum(case when pm.status = '待收款' then pm.amount else 0 end), 0) as receivable_amount,
  p.cost_amount,
  (p.quoted_amount - p.cost_amount) as gross_profit,
  case
    when p.quoted_amount = 0 then 0
    else round(((p.quoted_amount - p.cost_amount) / p.quoted_amount) * 100, 2)
  end as gross_margin_pct
from projects p
join customers c on c.id = p.customer_id
left join payments pm on pm.project_id = p.id
group by p.id, p.name, c.name, p.quoted_amount, p.cost_amount;

create or replace view v_due_risks_7d as
select
  p.id,
  p.name,
  c.name as customer_name,
  p.due_date,
  p.status,
  case
    when p.due_date < current_date then 'overdue'
    when p.due_date <= current_date + 3 then 'due_3d'
    when p.due_date <= current_date + 7 then 'due_7d'
    else 'normal'
  end as risk_level
from projects p
join customers c on c.id = p.customer_id
where p.status <> '已結案';

create or replace view v_quote_conversion_monthly as
select
  date_trunc('month', coalesce(sent_at, created_at)) as month,
  count(*) filter (where status in ('已送出','待修改','已確認','已取消')) as sent_count,
  count(*) filter (where status = '已確認') as won_count,
  case
    when count(*) filter (where status in ('已送出','待修改','已確認','已取消')) = 0 then 0
    else round(
      (
        count(*) filter (where status = '已確認')::numeric /
        count(*) filter (where status in ('已送出','待修改','已確認','已取消'))::numeric
      ) * 100, 2
    )
  end as win_rate_pct
from quotes
group by 1
order by 1 desc;
