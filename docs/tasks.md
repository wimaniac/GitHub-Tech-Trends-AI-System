# Tasks & Tickets

Tài liệu này chia nhỏ dự án thành các ticket cụ thể để tiện theo dõi và triển khai.

## Phase 1: Móng & Database Layer
- [ ] **DB-01**: Setup cấu trúc dự án, môi trường (venv, requirements.txt).
- [ ] **DB-02**: Định nghĩa SQLAlchemy Async Models (`Repository`, `TechTrend`, `TrendSnapshot`).
- [ ] **DB-03**: Viết module `db.py` với các hàm CRUD cơ bản (upsert, get).

## Phase 2: Data Collector Layer
- [ ] **COL-01**: Tích hợp `httpx` gọi GitHub API `/search/repositories` (handle Rate Limit).
- [ ] **COL-02**: Viết cào dữ liệu (Scraping) trang GitHub Trending dùng BeautifulSoup.
- [ ] **COL-03**: Viết `scheduler.py` gom 2 nguồn trên và ném vào Database.

## Phase 3: AI Analysis Engine
- [ ] **AI-01**: Viết `text_processor.py` để làm sạch nội dung Readme/Description, trích xuất keywords.
- [ ] **AI-02**: Tích hợp `sentence-transformers/all-MiniLM-L6-v2` tạo embeddings cho repo content.
- [ ] **AI-03**: Áp dụng thuật toán HDBSCAN/KMeans phân cụm các repo có tính năng tương tự.
- [ ] **AI-04**: Viết thuật toán tính điểm Trend Score (trọng số stars, forks, recent activity).
- [ ] **AI-05**: Viết logic tính Growth Rate so với Snapshot ngày hôm trước.

## Phase 4: API & Backend
- [ ] **API-01**: Khởi tạo app FastAPI, setup CORS, Lifespan handler.
- [ ] **API-02**: Thêm endpoint phục vụ Data (`/api/trends`, `/api/stats`).
- [ ] **API-03**: Thêm endpoint kích hoạt Job (`/api/collect`, `/api/analyze`) dưới dạng Background Tasks.

## Phase 5: Dashboard Frontend
- [ ] **UI-01**: Cắt HTML/CSS Vanilla giao diện Dark Theme / Glassmorphism.
- [ ] **UI-02**: Kết nối Fetch API lấy dữ liệu tĩnh hiển thị lên UI.
- [ ] **UI-03**: Vẽ biểu đồ Trend History bằng `Chart.js`.
- [ ] **UI-04**: Thêm tính năng Filter category và Search realtime.

## Phase 6: Tối ưu & Mở rộng
- [ ] **OPT-01**: Viết cronjob / APScheduler để tự động chạy Data Collector sau mỗi 6 tiếng.
- [ ] **OPT-02**: Add caching (in-memory hoặc Redis) cho GET API endpoint.
- [ ] **OPT-03**: Viết Unit Tests coverage > 80%.
