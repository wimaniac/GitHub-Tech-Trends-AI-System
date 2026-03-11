# Product — GitHub Tech Trends AI System

## Mục tiêu sản phẩm

### Tầm nhìn
Xây dựng hệ thống AI tự động thu thập, phân tích và trực quan hóa xu hướng công nghệ từ GitHub, giúp lập trình viên, nhà nghiên cứu và người học công nghệ nắm bắt được:
- Công nghệ nào đang **nổi lên** trong cộng đồng
- Công nghệ nào đang **tăng trưởng mạnh** nhất
- **Dự đoán** xu hướng công nghệ trong tương lai gần

### Mục tiêu cụ thể

| # | Mục tiêu | Đo lường |
|---|----------|----------|
| 1 | Thu thập repos GitHub trending & phổ biến | ≥ 500 repos/lần crawl |
| 2 | Phát hiện công nghệ/framework từ nội dung repo | ≥ 150 công nghệ trong knowledge base |
| 3 | Phân cụm repos theo chủ đề tự động (unsupervised) | Silhouette score ≥ 0.3 |
| 4 | Tính trend score và ranking công nghệ | Top 50 xu hướng cập nhật mỗi 6h |
| 5 | Dự đoán xu hướng ngắn hạn | Confidence score ≥ 0.4 |
| 6 | Dashboard trực quan, realtime | Thời gian load < 2s |

### Đối tượng sử dụng
- **Lập trình viên**: Muốn biết nên học công nghệ gì tiếp theo
- **Tech Lead / CTO**: Đánh giá công nghệ mới cho dự án
- **Nhà nghiên cứu**: Theo dõi xu hướng trong lĩnh vực AI/ML, Web, v.v.
- **Sinh viên / Người học**: Khám phá công nghệ trending để định hướng học tập

---

## User Flow

### Flow 1: Xem xu hướng (Primary)
```
Người dùng → Mở Dashboard (localhost:8000)
           → Xem Stats Bar (tổng repos, trends, rising, emerging)
           → Duyệt Trends Grid (top công nghệ ưu tiên hiển thị theo "Tốc độ tăng trưởng" - Growth Rate để thấy rõ sự Mới Nổi)
           → Lọc theo Category (AI/ML, Web Frontend, DevOps, ...)
           → Thay đổi Sắp xếp theo Trend Score / Growth Rate / Stars
           → Click vào trend → Xem Detail Modal (metrics, timeline chart)
```

### Flow 2: Thu thập dữ liệu
```
Người dùng → Nhấn nút "Thu thập" trên Dashboard
           → Hệ thống gửi POST /api/collect
           → Background: Scrape GitHub Trending (Random Languages) + Search API (Random Categories)
           → Background: NLP → Extract technologies → Embeddings → Clustering
           → Background: Tính Trend Score → Lưu DB
           → Dashboard auto-refresh sau 60s → Hiển thị dữ liệu mới
```

### Flow 3: Xem dự đoán
```
Người dùng → Cuộn xuống phần "Dự đoán xu hướng"
           → Xem danh sách công nghệ được sắp xếp theo "Kỳ vọng tăng trưởng" (Predicted Score - Current Score) cao nhất
           → Xem predicted score vs current score
           → Xem momentum indicator (🚀 Tăng mạnh, 📈 Đang tăng, ...)
           → Xem confidence bar
```

### Flow 4: Tìm kiếm
```
Người dùng → Gõ tên công nghệ vào Search Box
           → Dashboard filter realtime (debounce 300ms)
           → Hiển thị kết quả matching
```

### Flow 5: Sử dụng API
```
Developer → GET /api/trends?category=AI/ML&sort_by=growth_rate
          → Nhận JSON { count, trends[] }
          → Tích hợp vào ứng dụng / bot / newsletter
```

---

## Constraints (Ràng buộc)

### Kỹ thuật
| Constraint | Chi tiết |
|------------|----------|
| **GitHub API Rate Limit** | 60 req/h (unauthenticated), 5000 req/h (có token). Phải implement retry + backoff |
| **Scraping GitHub Trending** | HTML structure có thể thay đổi, cần fallback graceful |
| **Embedding Model Size** | `all-MiniLM-L6-v2` ~80MB, tải lần đầu, chạy local (CPU) |
| **SQLite Concurrency** | Single writer; đủ cho prototype, upgrade PostgreSQL nếu scale |
| **AI Integration** | Core ML (Embeddings, Clustering, NLP) chạy local 100%. Gemini API dùng làm AI Assistant tương tác với Context. |

### Hiệu năng
| Metric | Target |
|--------|--------|
| Dashboard initial load | < 2 giây |
| API response time | < 500ms cho GET endpoints |
| Data collection cycle | < 10 phút cho 500 repos (đã có Rate Limit/Backoff) |
| Embedding batch (100 texts) | < 30 giây (CPU) |

### Phạm vi MVP (Cập nhật Phase 10)
- ✅ Thu thập an toàn từ GitHub Trending + Search API (Rate Limited)
- ✅ Phân tích NLP (Từ điển + Embedding Similarity) + Tech Ecosystem Clustering
- ✅ Dự đoán xu hướng với Exponential Momentum
- ✅ Dashboard web tĩnh tích hợp Dark/Light theme & i18n
- ✅ Tích hợp Gemini AI Chatbot hiểu Data DB
- ❌ Chưa có: Authentication, user accounts
- ❌ Chưa có: Real-time WebSocket updates
- ❌ Chưa có: Multi-language NLP cho source code (hiện ưu tiên tiếng Anh)
