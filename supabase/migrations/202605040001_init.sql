-- Auto-generated from sql/schema.sql + sql/views.sql
-- Charles Imaging MVP schema (PostgreSQL / Supabase)

create extension if not exists "pgcrypto";

-- enums
create type customer_type as enum ('B2B','B2C');
create type customer_tier as enum ('A','B','C','Strategic');
create type active_status as enum ('active','inactive','lost');
create type lead_status as enum ('新詢問','已回覆','已報價','追蹤中','已成交','已流失');
create type need_type as enum ('商品攝影','人像','美食','影片','AI合成','其他');
create type budget_range as enum ('<10k','10k-30k','30k-50k','50k+');
create type project_status as enum ('待拍攝','拍攝中','修圖中','待交付','已結案');
create type task_stage as enum ('需求確認','企劃','拍攝準備','拍攝','初選','修圖','交付','結案');
create type task_status as enum ('未開始','進行中','已完成','延遲');
create type quote_status as enum ('草稿','已送出','待修改','已確認','已取消');
create type payment_type as enum ('訂金','尾款','其他');
create type payment_status as enum ('待收款','已收款');
create type payment_method as enum ('現金','轉帳','LINE Pay','信用卡','其他');
create type invoice_status as enum ('未開','已開','免開');
create type confirm_status as enum ('未確認','已確認','需修改');

create table customers (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  type customer_type not null,
  industry text,
  contact_name text,
  phone text,
  line_id text,
  email text,
  source text,
  tier customer_tier default 'B',
  status active_status default 'active',
  last_contact_at date,
  total_revenue numeric(12,2) not null default 0,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table leads (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid references customers(id) on delete set null,
  lead_name text not null,
  source text,
  need_type need_type,
  budget_range budget_range,
  status lead_status not null default '新詢問',
  lost_reason text,
  next_followup_at date,
  owner text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table projects (
  id uuid primary key default gen_random_uuid(),
  customer_id uuid not null references customers(id) on delete restrict,
  lead_id uuid references leads(id) on delete set null,
  name text not null,
  project_type need_type,
  owner text,
  shoot_date date,
  due_date date,
  status project_status not null default '待拍攝',
  quoted_amount numeric(12,2) not null default 0,
  cost_amount numeric(12,2) not null default 0,
  drive_link text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint due_after_shoot check (due_date is null or shoot_date is null or due_date >= shoot_date)
);

create table tasks (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  stage task_stage not null,
  title text not null,
  assignee text,
  due_date date,
  status task_status not null default '未開始',
  priority smallint not null default 2 check (priority between 1 and 3),
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table quotes (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  quote_no text not null unique,
  version int not null default 1,
  amount numeric(12,2) not null,
  status quote_status not null default '草稿',
  sent_at timestamptz,
  confirmed_at timestamptz,
  valid_until date,
  cancel_reason text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table payments (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  payment_type payment_type not null,
  amount numeric(12,2) not null,
  status payment_status not null default '待收款',
  due_date date,
  paid_at timestamptz,
  method payment_method,
  invoice_status invoice_status not null default '未開',
  note text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table deliveries (
  id uuid primary key default gen_random_uuid(),
  project_id uuid not null references projects(id) on delete cascade,
  version text not null,
  delivery_date timestamptz,
  content_summary text,
  link text,
  client_confirm_status confirm_status not null default '未確認',
  revision_count int not null default 0,
  license_scope text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_projects_status on projects(status);
create index idx_projects_due_date on projects(due_date);
create index idx_leads_status on leads(status);
create index idx_quotes_status on quotes(status);
create index idx_payments_status_due on payments(status, due_date);

-- updated_at trigger
create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger set_updated_at_customers before update on customers for each row execute procedure set_updated_at();
create trigger set_updated_at_leads before update on leads for each row execute procedure set_updated_at();
create trigger set_updated_at_projects before update on projects for each row execute procedure set_updated_at();
create trigger set_updated_at_tasks before update on tasks for each row execute procedure set_updated_at();
create trigger set_updated_at_quotes before update on quotes for each row execute procedure set_updated_at();
create trigger set_updated_at_payments before update on payments for each row execute procedure set_updated_at();
create trigger set_updated_at_deliveries before update on deliveries for each row execute procedure set_updated_at();

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

-- Row Level Security
alter table customers enable row level security;
alter table leads enable row level security;
alter table projects enable row level security;
alter table tasks enable row level security;
alter table quotes enable row level security;
alter table payments enable row level security;
alter table deliveries enable row level security;

-- Temporary MVP policy (replace with team-scoped policies in phase 2)
create policy "customers_all_auth" on customers for all to authenticated using (true) with check (true);
create policy "leads_all_auth" on leads for all to authenticated using (true) with check (true);
create policy "projects_all_auth" on projects for all to authenticated using (true) with check (true);
create policy "tasks_all_auth" on tasks for all to authenticated using (true) with check (true);
create policy "quotes_all_auth" on quotes for all to authenticated using (true) with check (true);
create policy "payments_all_auth" on payments for all to authenticated using (true) with check (true);
create policy "deliveries_all_auth" on deliveries for all to authenticated using (true) with check (true);
