-- minimal sample data
insert into customers (name, type, industry, contact_name, source, tier)
values
('DR.CINK', 'B2B', '保養品', '王小姐', 'IG', 'A'),
('王小明', 'B2C', '個人品牌', '王小明', 'Website', 'B');

insert into leads (lead_name, source, need_type, budget_range, status, owner)
values ('DR.CINK 主視覺案', 'IG', '商品攝影', '30k-50k', '已成交', 'Charles');
