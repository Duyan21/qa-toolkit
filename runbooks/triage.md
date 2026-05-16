# Triage — Bắt đầu tại đây

Xác định triệu chứng, mở đúng runbook. Không đọc tất cả cùng lúc.

---

## Triệu chứng của tôi là gì?

| Triệu chứng                                      | Runbook                      |
|--------------------------------------------------|------------------------------|
| API trả về `5xx` (500, 502, 503...)              | [debug-5xx.md]               |
| API trả về `4xx` (401, 403, 404, 422...)         | [debug-4xx.md]               |
| API trả về `200` nhưng response time > 500ms     | [debug-slow-api.md]          |
| `log_watcher` bắn 🚨 ALERT                       | [debug-log-alert.md]         |
| `json_diff` phát hiện mismatch staging vs prod   | [debug-json-mismatch.md](debug-json-mismatch.md) |

---

## Không chắc triệu chứng là gì?

Trả lời 3 câu này theo thứ tự:

1. **Tool nào phát hiện vấn đề?**
   - `api_checker` → xem cột "API trả về..." ở trên
   - `log_watcher` → [debug-log-alert.md]
   - `json_diff` → [debug-json-mismatch.md]
   - Người dùng báo → hỏi thêm: status code là gì?

2. **Lỗi xảy ra ở đâu?**
   - Local only → có thể là config / env issue
   - Staging / Production → escalate nhanh hơn

3. **Tần suất?**
   - 100% reproduce → debug được ngay
   - Intermittent → thu thập log trước, reproduce sau

---

## Time-box

> Nếu sau **30 phút** vẫn không xác định được nguyên nhân → escalate.
> Không phải thất bại — đó là quy trình đúng.

---

## Escalation

- Slack: `#incident` hoặc `#backend-oncall` _(cập nhật theo team)_
- Ticket: tạo issue với template [bug-report]
- On-call: xem danh sách tại [đường dẫn rotation] _(cập nhật theo team)_
