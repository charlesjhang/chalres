# Automation Specs

## A1 新案件自動建立 Drive 資料夾
- Trigger: 新增 `projects`。
- Action: 建立主資料夾與 8 個子資料夾，回填 `projects.drive_link`。

## A2 報價追蹤提醒
- Trigger: `quotes.status = 已送出`。
- Action: 第 3 / 7 / 14 天提醒，14 天可標記風險。

## A3 尾款追蹤提醒
- Trigger: `payments.status = 待收款` 且到期。
- Action: 每日提醒，逾期 3 天標紅，逾期 7 天升級高風險。
