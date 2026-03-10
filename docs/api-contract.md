# API Contract — GitHub Tech Trends

## Base URL
`http://localhost:8000/api`

## Phản hồi chuẩn (Standard Formats)
Tất cả các API tuân theo định dạng JSON.

---

### 1. `GET /trends`
**Mô tả**: Trả về danh sách top xu hướng công nghệ đã được đánh giá và tính điểm.
**Query Params**:
- `category` (string, optional): Lọc theo danh mục cụ thể (vd: "AI/ML", "Web Frontend").
- `limit` (int, default=50): Số lượng kết quả trả về.
- `sort_by` (string, default="trend_score"): Cột dùng để sắp xếp (trend_score, growth_rate, repo_count).

**Response (200 OK)**:
```json
{
  "count": 50,
  "trends": [
    {
      "name": "FastAPI",
      "category": "Backend",
      "trend_score": 85.4,
      "growth_rate": 15.2,
      "repo_count": 320,
      "momentum": "🚀 Tăng mạnh"
    }
  ]
}
```

### 2. `GET /trends/detail/{tech_name}`
**Mô tả**: Trả về thông tin chi tiết của một công nghệ, bao gồm history snapshot.
**Response (200 OK)**:
```json
{
  "name": "FastAPI",
  "category": "Backend",
  "current_score": 85.4,
  "history": [
    {"timestamp": "2026-03-08T00:00:00Z", "score": 75.0},
    {"timestamp": "2026-03-09T00:00:00Z", "score": 80.2},
    {"timestamp": "2026-03-10T00:00:00Z", "score": 85.4}
  ]
}
```

### 3. `GET /stats`
**Mô tả**: Load thông số tổng quan phục vụ cho Dashboard.
**Response (200 OK)**:
```json
{
  "total_repos_analyzed": 1542,
  "total_techs_identified": 185,
  "last_collection_time": "2026-03-10T15:00:00Z",
  "top_emerging": "LangChain"
}
```

### 4. `POST /collect`
**Mô tả**: Kích hoạt worker đi thu thập dữ liệu từ GitHub (Trending & API). Tính toán bất đồng bộ.
**Response (202 Accepted)**:
```json
{
  "status": "processing",
  "message": "Data collection job started in background."
}
```

### 5. `POST /analyze`
**Mô tả**: Kích hoạt quá trình NLP Extraction, Embedding, Clustering và Scoring dựa trên data hiện có.
**Response (202 Accepted)**:
```json
{
  "status": "processing",
  "message": "AI analysis job started."
}
```
