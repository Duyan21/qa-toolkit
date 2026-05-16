# Debug: Log Watcher Alert

Dùng khi `log_watcher` bắn 🚨 ALERT — error frequency vượt ngưỡng trong sliding window.
Không chắc đây là vấn đề của bạn? → [triage.md]

---

## Thông tin cần đọc từ alert

Khi `log_watcher` bắn alert, nó in ra:

```
🚨 ALERT: 5 errors in 60 seconds
   From: 10:00:05 → 10:00:58
```

Thu thập ngay:
- [ ] Bao nhiêu errors trong khoảng thời gian nào?
- [ ] Error type là gì? (xem summary bên dưới alert)
- [ ] Thời điểm bắt đầu — có gì xảy ra trước đó không? (deploy, cron job, traffic spike)

---

## Bước 1 — Đọc session summary

`log_watcher` in summary định kỳ và session report khi exit:

```
Total errors: 7
  - Database connection failed: timeout (x4)
  - Auth service unreachable (x3)
```

- [ ] Error nào chiếm tỉ lệ cao nhất?
- [ ] Có một loại error tăng đột biến hay nhiều loại cùng lúc?
  - Một loại tăng → vấn đề ở service cụ thể
  - Nhiều loại cùng lúc → có thể là infrastructure issue

---

## Bước 2 — Xác định severity

| Tình huống                              | Mức độ          | Hành động           |
|-----------------------------------------|-----------------|---------------------|
| Error rate tăng nhưng đang giảm dần     | Low             | Monitor thêm        |
| Error rate ổn định ở mức cao            | Medium          | Debug ngay          |
| Error rate đang tăng liên tục           | High            | Escalate ngay       |
| Toàn bộ service không response          | Critical        | Escalate + wake oncall |

---

## Bước 3 — Route đến đúng runbook

Dựa vào error message trong log:

- Lỗi liên quan đến API / HTTP status → [debug-5xx.md] hoặc [debug-4xx.md]
- Lỗi liên quan đến response time / timeout → [debug-slow-api.md]
- Lỗi database / connection → check database layer trực tiếp
- Lỗi auth / token → [debug-4xx.md] → section 401

---

## Bước 4 — Escalate nếu cần

⏱ Nếu severity là **High hoặc Critical** → không cần đợi 30 phút, escalate ngay

Chuẩn bị khi escalate:
- Copy paste đoạn alert + summary từ `log_watcher`
- Thời điểm bắt đầu và tần suất hiện tại

→ Xem thông tin escalation tại [triage.md]

---

## Bước 5 — Verify ổn định

- [ ] Error rate đã về 0 hoặc về mức bình thường chưa?
- [ ] `log_watcher` không còn bắn alert trong 10 phút tiếp theo?

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
