# Pablo QA Orchestrator 圖資總覽

> 目的：集中保存目前架構圖/流程圖/治理圖/部署拓樸圖（draw.io 可直接開啟與編輯）。
> 狀態：Redmine/TestLink read-only phase。

## 1) 完整結構治理圖（含 read-only 與水箱策略）

- 說明：呈現 Source / Orchestrator / Execution / Evidence 四層，並標示 `Water tank policy` 分流。  
- draw.io 連結：

https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#create=%7B%22type%22%3A%22mermaid%22%2C%22compressed%22%3Atrue%2C%22data%22%3A%22dVNdb6MwEPw1PFaKWlV9poRUlZILpai5t2pjDFgYG9mGlH9%2FuzY5kkvuBfDs7Idnh0rqE2vAuOhxtc2jVWyHY22gb%2FD8mSfR8%2BunHgzjdJys452NntdIy3cYynnZCUUxw6HEl1ZyCvFii%2FGCW7cVqr1H4Kq87rb33T5i%2BjSswVQDThs8ZnCUOmS9%2FyqQ9K4ctNQWFBUFKWrVceUCZxdnyNlB3wtVY1hYOxDZYUkGlj5bPp20KQM%2F29OsmZaCTRjjqqY73R8y%2FZ0iN%2F3hbHBCKxpOwpmdp9meVNFH7fyV%2B3nqfHMBbwx0HLu3IeaHjXHWoQvAOv3y0oJEcslH4cWvwHT%2Fm%2BlrTTONouSKLaq86ZEbBQT5vMR3SqB3gyGW1LXFl2WGc2Ub7ehERfS84iKnFRrwNTtwRvyc1fwW5YWg4TRrOocoLXyit0QFzH0PRoTCb3GRhiuWqLSlvjU46sK0Upw5MQo3%2BabnHfLldkbY9lIJdOLj6uEhekrxTf7w5vsXoueCkUWCURaMbBDMsGB%2Bo%2FNiL9BN2OmC%2BHJX1WiLYZcLlnhacsUr8ptBPISPBfGCzbpdjLG7xQq6wyF6eT2goPTvOPC%2FXx%2Fc%2FbK%2BueLBJ%2Fgz2a2CQZJLq0GS%2FyQfuTz%2Ftze6%2FM3TrvHdTnNXcoX1C1QD3Mkv8j8%3D%22%7D

---

## 2) Traceability 欄位流程圖（issue_id → testcase_id → keyword_id → trace_id → artifact_uri）

- 說明：呈現資料契約與 evidence 流向，含 Readiness Gate 與 P0 remediation。  
- draw.io 連結：

https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#create=%7B%22type%22%3A%22mermaid%22%2C%22compressed%22%3Atrue%2C%22data%22%3A%22ZVLLbhsxDPyaPQYwGhg5r2PnaRtBEqDHgpa4NhFZ2urhxH9fktqkanNZUdyZ0fAxuPBuDhBz92P2uuxmfd%2FNF89oj%2BSRU5RSwV9kJfRjEVREkGvw7tzNlxxdXHSXKz4XzHzFlNfk3%2FiaOTSQJnbKOKbv7Fm%2FaBSuWeGFgRyOEBP5PUfghWDAB08GnGRMpuAr%2FbqhL5n%2BiOf3EIVxhHGsCm81J0aU05peMWf1gaaopPj7Xdi4%2BI9g8Iuzajg30qKwC%2FnLXc9PlaPQi9fqaqVi1uKJDKaqctOo3LJKHzMNXI50xoW9HMlERJ8OQZMnshhq38YQ8yRz28jcNTJ8LZFEi0cAe6zouwZ9LzOSwmBHjvJZ%2B5QjfegTRjqnnPuG89Bd8UaA5Y1IYmUPGbsrQT1UlExL%2F3wyHnWHHPL0P%2FE6QUtW4vk%2F3AHINdw1c59maueIlmCai06Dzx23VbbLB%2F6gtMdr3oe6m2MMthjauemZDZv%2FyY9G0QBdzFjc5L9dno2CJ08WByhOFIfixJ3DE7Yuly3aq8O%2FnP%2FBWy5pA77oPujmS8fyoTrctuP5Aw%3D%3D%22%7D

---

## 3) 部署拓樸圖（Control / CI / Device / Evidence Plane）

- 說明：呈現 Redmine/TestLink、Repo/CI、Appium/ADB/WDA、Real Device、Artifact/Report/Trace Store 的部署與資料流。  
- draw.io 連結：

https://app.diagrams.net/?grid=0&pv=0&border=10&edit=_blank#create=%7B%22type%22%3A%22mermaid%22%2C%22compressed%22%3Atrue%2C%22data%22%3A%22bVLRjoIwEPwaHk2IFz8ABD0T7yS93t1zgSoboSWl6Pn3t9tiBPSlhJnZ7XRnj7W%2BFpUwNliGPA7CqOvzkxFthf9rzvbBKl5rZY2uEchqoWSwSlB2YGukMpHXGgltikp21girjefZB9JMlg1gxTI0UpSkU%2FXN85w6c6zZgzq%2FEmzfUbAF67hWd4CtB0qqcmZ0h9q4h5paCEUntZ46Zt%2Bf9JgdNeyVknejGzKqc03yjRGNvGpz9iILzVAcZaiK2hb6BqlKY%2FPXVpL0hxom8gKFnBqIkpiaqNJoIIu5gfJEGkeQ4jeJUAGHrzHrQF%2FPJvU4MgqldFd1XrPD2nuHV%2Fyz34jTnekFSqmeHDNONxoLR1HQfDoMQZzuA02zIcMhI7dE9MF7fchuSbgRhRQ51GBvKGiENfA3NJNjW7gzy3CxCN5S%2FNKCuTWZQ7gYD4hC9cs4x%2BgcYRsf9QPBRF2sIySJ5xDN3gc3lrEhqgdGY%2FcBjXQ4PB%2FIHJv6cBCdI7dp9oRx9%2FjpSz3Gp693tXROBvcP%22%7D

---

## 使用建議

- 若要長期維護版本，建議把每張圖另存 `.drawio` 檔並回存到 repo。  
- 若要避免 Mermaid 特殊字元解析錯誤，優先用簡單 label（避免 `[]` 等）。  
- 目前規則：水箱僅「預設滿水位/水位在高」列 automation candidate，其餘 manual-only。
