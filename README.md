# GitHub Tech Trends AI System

Hệ thống AI tự động thu thập và phân tích xu hướng công nghệ từ GitHub.

## Tính năng

- 🔍 **Thu thập dữ liệu** từ GitHub Trending và Search API
- 🤖 **Phân tích AI** bằng NLP, embeddings và clustering
- 📊 **Dashboard** trực quan với charts và filters
- 🔮 **Dự đoán** xu hướng công nghệ tương lai
- ⚡ **API** RESTful cho tích hợp

## Cài đặt

```bash
# Cài Python dependencies
pip install -r requirements.txt

# (Tùy chọn) Thêm GitHub token để tăng rate limit
# Sửa file .env và thêm token
```

## Chạy

```bash
python run.py
```

Mở trình duyệt tại: **http://localhost:8001**

## Sử dụng

1. Mở dashboard tại `http://localhost:8001`
2. Nhấn **"Thu thập"** để crawl dữ liệu từ GitHub
3. Hệ thống tự động phân tích xu hướng
4. Xem kết quả trên dashboard: trends, charts, predictions

## API Endpoints

| Endpoint | Mô tả |
|---|---|
| `GET /api/trends` | Danh sách xu hướng công nghệ |
| `GET /api/trends/detail/{name}` | Chi tiết 1 công nghệ |
| `GET /api/predictions` | Dự đoán AI |
| `GET /api/categories` | Danh mục công nghệ |
| `GET /api/repos` | Repositories đã thu thập |
| `GET /api/stats` | Thống kê tổng quan |
| `POST /api/collect` | Kích hoạt thu thập |
| `POST /api/analyze` | Kích hoạt phân tích |

API Docs: `http://localhost:8001/docs`

## Các mốc quan trọng (Milestones)

- **Phase 1**: Setup project, Database models, API Server (`app.py`, `routes.py`)
- **Phase 2**: Data collector - Tích hợp GitHub Search API & Trending Scraper
- **Phase 3**: AI Analysis - Nhận diện technologies, Embeddings & HDBSCAN Clustering
- **Phase 4**: Thực hiện Scoring & Time-series prediction cho các Trends
- **Phase 5**: Hoàn thiện Dashboard giao diện Dark Mode hiển thị trực quan dữ liệu
- **Phase 6**: Optimization & Extension - Tự động hóa crawl dữ liệu bằng `APScheduler`, Caching API server dùng `fastapi-cache2`, và viết Unit Tests coverage caoด้วย `pytest`.

## Công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy, SQLite, APScheduler, fastapi-cache2
- **AI/ML**: sentence-transformers, scikit-learn, HDBSCAN
- **Data**: httpx, BeautifulSoup4
- **Frontend**: Vanilla JS, Chart.js
- **Testing**: pytest, pytest-asyncio, pytest-httpx, pytest-cov
