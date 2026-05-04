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
