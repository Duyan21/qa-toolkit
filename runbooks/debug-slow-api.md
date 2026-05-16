# Debug: Slow API / Timeout

Dùng khi `api_checker` báo ⚠️ (response time > 500ms) hoặc request không nhận được response.
Không chắc đây là vấn đề của bạn? → [triage.md]

> Slow API và timeout thường không phải lỗi code — thường là infrastructure, data, hoặc external dependency.

---

## Bước 0 — Xác định loại vấn đề

| Triệu chứng                        | Hướng xử lý                     |
|------------------------------------|----------------------------------|
| Response time > 500ms nhưng có trả về | Slow response → check performance |
| Connection timeout (không có response) | Network / service down          |
| Chỉ chậm một endpoint cụ thể       | Query / logic của endpoint đó    |
| Toàn bộ service chậm               | Infrastructure / resource issue  |

---

## Bước 1 — Đo và isolate

- [ ] Response time cụ thể là bao nhiêu? (500ms? 2s? 10s?)
- [ ] Chỉ chậm endpoint này hay nhiều endpoint?
- [ ] Chỉ chậm ở một environment hay tất cả?
- [ ] Chậm liên tục hay chỉ ở một số thời điểm (peak hours)?

---

## Bước 2 — Check theo từng layer

### Network
- [ ] Ping / traceroute đến host có bình thường không?
- [ ] DNS resolution có chậm không?

### Application
- [ ] Endpoint này xử lý logic nặng không? (nhiều vòng lặp, nhiều transform)
- [ ] Có external API call nào bên trong endpoint này không?

### Database
- [ ] Query đang chạy có index chưa?
- [ ] Kích thước data lớn bất thường không? (full table scan?)
- [ ] Connection pool có bị exhausted không?

### Infrastructure
- [ ] CPU / memory của server có bình thường không?
- [ ] Có traffic spike nào gần đây không?

---

## Bước 3 — Reproduce và đo lại

- [ ] Gọi lại endpoint nhiều lần — response time có ổn định không hay dao động?
- [ ] Thử với payload nhỏ hơn — thời gian có giảm không?
- [ ] Thử vào giờ thấp traffic — vẫn chậm không?

---

## Bước 4 — Escalate nếu cần

⏱ Nếu sau **30 phút** chưa xác định được layer nào gây chậm → escalate  
Chuẩn bị: response time log từ `api_checker`, environment, thời điểm xảy ra

→ Xem thông tin escalation tại [triage.md]

---

## Bước 5 — Verify fix

- [ ] Chạy lại `api_checker` → response time dưới threshold?
- [ ] Đo trong ít nhất 3-5 lần liên tiếp để confirm ổn định

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
