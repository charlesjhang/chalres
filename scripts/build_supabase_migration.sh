#!/usr/bin/env bash
set -euo pipefail

OUT="supabase/migrations/202605040001_init.sql"

echo "-- Auto-generated from sql/schema.sql + sql/views.sql" > "$OUT"
cat sql/schema.sql >> "$OUT"
printf "\n" >> "$OUT"
cat sql/views.sql >> "$OUT"
cat >> "$OUT" <<'SQL'

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
SQL

echo "Wrote $OUT"
