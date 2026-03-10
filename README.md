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

Mở trình duyệt tại: **http://localhost:8000**

## Sử dụng

1. Mở dashboard tại `http://localhost:8000`
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

API Docs: `http://localhost:8000/docs`

## Công nghệ sử dụng

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI/ML**: sentence-transformers, scikit-learn, HDBSCAN
- **Data**: httpx, BeautifulSoup4
- **Frontend**: Vanilla JS, Chart.js
