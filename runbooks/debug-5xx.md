# Debug: API 5xx Errors

Dùng khi `api_checker` báo ❌ với status 500, 502, 503, 504.
Không chắc đây là vấn đề của bạn? → [triage.md]

---

## Bước 0 — Reproduce (làm trước mọi thứ)

- [ ] Đã reproduce được chưa?
- [ ] Tỉ lệ reproduce: 100% / intermittent / chỉ một endpoint cụ thể?
- [ ] Nếu chưa reproduce được → **dừng lại**, thu thập log thêm trước khi debug tiếp

---

## Bước 1 — Đọc response

- [ ] Status code chính xác là bao nhiêu? (500 / 502 / 503 / 504)
- [ ] Response body nói gì? (error message, stack trace nếu có)
- [ ] Error message có đủ context hay chỉ là generic message?

> **Phân biệt nhanh:**
> - `500` Internal Server Error → lỗi trong code của service
> - `502` Bad Gateway → service phía sau không response được
> - `503` Service Unavailable → service đang overload hoặc down
> - `504` Gateway Timeout → service phía sau quá chậm

---

## Bước 2 — Thu thập thông tin

- [ ] Request: URL, method, headers, body đầy đủ
- [ ] Timestamp và timezone của request lỗi
- [ ] Environment: local / staging / production?
- [ ] Frequency: luôn fail hay intermittent?
- [ ] Có deploy hoặc config change nào gần đây không?

---

## Bước 3 — Check logs

- [ ] Server log trong khoảng thời gian xảy ra lỗi
- [ ] Có pattern không — lỗi tương tự đã xảy ra trước đó?
- [ ] Dùng `log_watcher` hoặc `log_reader` để parse nếu log volume lớn

> **Với hệ thống có BFF layer:**
> - HTTP 200 không có nghĩa là success
> - Luôn check response body — có thể có `status`/`code`/`error` field bên trong
> - Trace request qua từng layer: FE → BFF → Service

---

## Bước 4 — Escalate nếu cần

⏱ Nếu sau **30 phút** chưa xác định được nguyên nhân → escalate ngay

- [ ] Tóm tắt được: "Lỗi X xảy ra ở Y, tần suất Z, đã thử A và B"
- [ ] Xác định đúng team đang control service đó
- [ ] → Xem thông tin escalation tại [triage.md]

---

## Bước 5 — Verify fix

- [ ] Reproduce lại scenario gốc → lỗi không còn xảy ra?
- [ ] Check các endpoint liên quan — không có regression?
- [ ] Đã có test case cover case này chưa? Nếu chưa → cần thêm

**Ghi lại sau khi fix:**

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
