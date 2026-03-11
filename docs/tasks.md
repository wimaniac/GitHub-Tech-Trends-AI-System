# Tasks & Tickets

Tài liệu này chia nhỏ dự án thành các ticket cụ thể để tiện theo dõi và triển khai.

## Phase 1: Móng & Database Layer
- [x] **DB-01**: Setup cấu trúc dự án, môi trường (venv, requirements.txt).
- [x] **DB-02**: Định nghĩa SQLAlchemy Async Models (`Repository`, `TechTrend`, `TrendSnapshot`).
- [x] **DB-03**: Viết module `db.py` với các hàm CRUD cơ bản (upsert, get).

## Phase 2: Data Collector Layer
- [x] **COL-01**: Tích hợp `httpx` gọi GitHub API `/search/repositories` (handle Rate Limit).
- [x] **COL-02**: Viết cào dữ liệu (Scraping) trang GitHub Trending dùng BeautifulSoup.
- [x] **COL-03**: Viết `scheduler.py` gom 2 nguồn trên và ném vào Database.

## Phase 3: AI Analysis Engine
- [x] **AI-01**: Viết `text_processor.py` để làm sạch nội dung Readme/Description, trích xuất keywords.
- [x] **AI-02**: Tích hợp `sentence-transformers/all-MiniLM-L6-v2` tạo embeddings cho repo content.
- [x] **AI-03**: Áp dụng thuật toán HDBSCAN/KMeans phân cụm các repo có tính năng tương tự.
- [x] **AI-04**: Viết thuật toán tính điểm Trend Score (trọng số stars, forks, recent activity).
- [x] **AI-05**: Viết logic tính Growth Rate so với Snapshot ngày hôm trước.

## Phase 4: API & Backend
- [x] **API-01**: Khởi tạo app FastAPI, setup CORS, Lifespan handler.
- [x] **API-02**: Thêm endpoint phục vụ Data (`/api/trends`, `/api/stats`).
- [x] **API-03**: Thêm endpoint kích hoạt Job (`/api/collect`, `/api/analyze`) dưới dạng Background Tasks.

## Phase 5: Dashboard Frontend
- [x] **UI-01**: Cắt HTML/CSS Vanilla giao diện Dark Theme / Glassmorphism.
- [x] **UI-02**: Kết nối Fetch API lấy dữ liệu tĩnh hiển thị lên UI.
- [x] **UI-03**: Vẽ biểu đồ Trend History bằng `Chart.js`.
- [x] **UI-04**: Thêm tính năng Filter category và Search realtime.

## Phase 6: Tối ưu & Mở rộng
- [x] **OPT-01**: Viết cronjob / APScheduler để tự động chạy Data Collector sau mỗi 6 tiếng.
- [x] **OPT-02**: Add caching (in-memory hoặc Redis) cho GET API endpoint.
- [x] **OPT-03**: Viết Unit Tests coverage > 80%.

## Phase 7: Config & Backend (Gemini & Search AI)
- [x] Thêm cấu hình `GEMINI_API_KEY`.
- [x] Thêm các endpoint `/api/chat`, `/api/search/suggestions`, `/api/repos/search`.
- [x] Mở rộng DB & Backend cho Chatbot và Autocomplete.

## Phase 8: Frontend Redesign
- [x] Toggle Dark/Light theme, Hỗ trợ đa ngôn ngữ i18n (Tiếng Việt / English).
- [x] Pagination, Autocomplete Search dropdown kết nối API.
- [x] Category Grid Cards và Widget Chatbot AI (Gemini).

## Phase 9: Verification & Bug Fixes
- [x] Kiểm thử toàn bộ API Backend & Frontend UI.

## Phase 10: Advanced Analytics & Robustness
- [x] **Crawler**: Rate Limiting, Backoff/Retry, Random Jitter.
- [x] **NLP**: Tích hợp Embedding Similarity để tự rò tìm công nghệ mới.
- [x] **Scoring**: Composite Trend Score (Velocity, Traction, Frequency, Breadth).
- [x] **Clustering**: Tech Ecosystems Clustering thay vì Repo Clustering.
- [x] **Predictor**: Exponential Momentum Forecasting (EMA Crossover).
