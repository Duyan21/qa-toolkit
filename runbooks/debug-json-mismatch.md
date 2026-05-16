# Debug: JSON Mismatch (staging vs production)

Dùng khi `json_diff` báo missing keys hoặc different values giữa hai environment.
Không chắc đây là vấn đề của bạn? → [triage.md]

> JSON mismatch giữa staging và production thường không phải lỗi code —
> thường là config drift, deploy thiếu bước, hoặc data migration chưa chạy.

---

## Đọc output của json_diff

```
Missing keys in production: 1
 - last_login

Different values: 1
 - role: staging='admin' vs production='viewer'

Identical: 3
 status, user_id, email
```

Thu thập ngay:
- [ ] Key nào bị missing? Field nào có giá trị khác nhau?
- [ ] Missing key hay different value — hai trường hợp này có nguyên nhân khác nhau

---

## Bước 1 — Phân loại vấn đề

| Triệu chứng                        | Khả năng nguyên nhân                        |
|------------------------------------|---------------------------------------------|
| Key có trong staging, thiếu ở prod | Deploy chưa đầy đủ / migration chưa chạy   |
| Key có ở prod, thiếu ở staging     | Staging đang chạy version cũ hơn            |
| Cùng key nhưng value khác nhau     | Config khác nhau giữa môi trường            |
| Nhiều key bị missing cùng lúc      | Có thể là schema change chưa được apply     |

---

## Bước 2 — Xác định nguồn gốc

- [ ] Field bị mismatch đến từ đâu? (API response, config file, database, feature flag)
- [ ] Hai environment đang chạy cùng version code không?
- [ ] Có deploy nào gần đây ở một môi trường mà không có ở môi trường kia?
- [ ] Có migration hoặc seed script nào cần chạy ở production chưa?

---

## Bước 3 — Verify thủ công

- [ ] Gọi thẳng endpoint ở cả hai môi trường và compare response
- [ ] Check config / environment variables của hai môi trường
- [ ] Nếu là database field: check schema của hai môi trường có khớp không

---

## Bước 4 — Escalate nếu cần

⏱ Nếu sau **30 phút** không xác định được nguyên nhân → escalate

Chuẩn bị khi escalate:
- Output đầy đủ từ `json_diff`
- Version code đang chạy ở từng môi trường
- Thời điểm mismatch bắt đầu xuất hiện (nếu biết)

→ Xem thông tin escalation tại [triage.md]

---

## Bước 5 — Verify fix

- [ ] Chạy lại `json_diff` sau khi fix → không còn mismatch?
- [ ] Chạy trên cả hai chiều: staging vs prod và prod vs staging

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
