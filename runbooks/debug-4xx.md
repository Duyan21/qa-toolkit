# Debug: API 4xx Errors

Dùng khi `api_checker` báo ❌ với status 400, 401, 403, 404, 422.
Không chắc đây là vấn đề của bạn? → [triage.md]

> 4xx = lỗi phía client. Kiểm tra request trước, không cần đào log server ngay.

---

## Bước 0 — Xác định status code

| Code | Nghĩa                    | Hướng debug đầu tiên              |
|------|--------------------------|-----------------------------------|
| 400  | Bad Request              | Kiểm tra format / schema của body |
| 401  | Unauthorized             | Kiểm tra token / API key          |
| 403  | Forbidden                | Kiểm tra permission / role        |
| 404  | Not Found                | Kiểm tra URL, resource có tồn tại không |
| 422  | Unprocessable Entity     | Kiểm tra validation rules của API |

---

## Bước 1 — Kiểm tra request

- [ ] URL có đúng không? (typo, trailing slash, version `/v1` vs `/v2`)
- [ ] Method đúng chưa? (GET / POST / PUT / PATCH / DELETE)
- [ ] Headers đầy đủ chưa? (`Content-Type`, `Authorization`, `Accept`)
- [ ] Body đúng format chưa? (JSON valid, required fields có đủ không)

---

## Bước 2 — Theo status code cụ thể

### 401 Unauthorized
- [ ] Token còn hạn không?
- [ ] Token được gửi đúng chỗ chưa? (`Bearer` prefix, header name đúng không)
- [ ] API key đúng environment chưa? (staging key dùng cho production?)

### 403 Forbidden
- [ ] User/service account có đúng role/permission không?
- [ ] Resource có bị restrict theo IP / org / plan không?

### 404 Not Found
- [ ] Resource có tồn tại không? (đã bị xóa, chưa được tạo, hay sai ID?)
- [ ] URL path có đúng không? So sánh với API docs

### 422 Unprocessable Entity
- [ ] Đọc kỹ response body — thường có field `errors` liệt kê rõ lỗi gì
- [ ] So sánh body đang gửi với schema mà API yêu cầu

---

## Bước 3 — Reproduce và isolate

- [ ] Thử gọi thẳng bằng `curl` hoặc Postman để loại trừ code issue
- [ ] Lỗi xảy ra với mọi user hay chỉ một số? (nếu chỉ một số → permission issue)
- [ ] Lỗi xảy ra ở mọi environment hay chỉ production? (nếu chỉ prod → config khác biệt)

---

## Bước 4 — Escalate nếu cần

⏱ Nếu sau **30 phút** chưa xác định được → escalate  
Chuẩn bị: raw request + raw response để paste ngay khi hỏi

→ Xem thông tin escalation tại [triage.md]

---

## Bước 5 — Verify fix

- [ ] Reproduce lại → response đúng như mong đợi?
- [ ] Test với các user/role khác nhau nếu là permission issue

```
Root cause   : 
Fix applied  : 
Follow-up    : [ ] Yes  [ ] No  →
```
