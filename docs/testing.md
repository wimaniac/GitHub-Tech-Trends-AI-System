# Testing & Edge Cases

## 1. Tiêu chí Pass/Fail (Acceptance Criteria)

### A. Thu thập dữ liệu (Collector)
- **PASS**: 
  - Lấy thành công tối thiểu 500 repository từ GitHub API + Github Trending trong mỗi lượt chạy.
  - Tự động detect Rate Limit (HTTP 403/429) và lùi thời gian retry (Exponential Backoff).
- **FAIL**: Hệ thống crash vì sai định dạng HTML khi trang GitHub thay đổi cấu trúc, hoặc throw Exception unhandled khi hết Rate Limit.

### B. AI Engine & NLP
- **PASS**:
  - Trích xuất được ít nhất 150 keywords công nghệ chính xác từ mô tả.
  - Tạo embedding cho 100 văn bản mất dưới 30s trên CPU.
  - Phân cụm HDBSCAN hoạt động bình thường, Silhouette score > 0.3.
- **FAIL**:
  - Out of Memory do batch size quá lớn.
  - Tất cả repos dạt vào duy nhất một cụm nhiễu (noise cluster -1).

### C. Backend API & Frontend
- **PASS**:
  - Thời gian phản hồi của mọi GET request dưới 500ms.
  - UI render dữ liệu cực mượt, Dashboard initial load mất dưới 2 giây.
- **FAIL**: Memory leak do không đóng DB connection; UI bị đơ khi nhấn nút "Collect".

---

## 2. Các Edge Cases cần xử lý

1. **Repo không có Description / README**:
   - Dữ liệu rác có thể đánh lừa thuật toán AI. Phải bỏ qua repo trống hoặc dùng title repo làm fallback text.
2. **Ký tự đặc biệt, Emoji, Ngôn ngữ lạ**:
   - Text cần được normalize (loại bỏ markdown, html tags) trước khi feed vào sentence-transformers.
3. **Mới khởi tạo dự án - Dữ liệu lịch sử rỗng**:
   - Biểu đồ timeline sẽ không vẽ được. API phải trả về placeholder an toàn. Thuật toán dự đoán (`predictor.py`) bỏ qua mô hình Machine Learning khi số điểm dữ liệu < 3.
4. **Trùng lặp tên Technologies (Synonyms)**:
   - "React.js", "ReactJS", "React" cần được nhóm về chung một chuẩn "React".
5. **Vượt dung lượng SQLite**:
   - Khi chạy lâu dài (vài tháng), SQLite phình to. Phải có module xóa log cũ, hoặc cảnh báo người dùng migrate sang PostgreSQL.
