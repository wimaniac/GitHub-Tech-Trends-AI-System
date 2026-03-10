"""
Entry point cho GitHub Tech Trends AI System.
"""
import uvicorn
from config import API_HOST, API_PORT


def main():
    print("=" * 60)
    print("  🔍 GitHub Tech Trends AI System")
    print("  📊 Phân tích xu hướng công nghệ từ GitHub")
    print("=" * 60)
    print(f"\n  Dashboard: http://localhost:{API_PORT}")
    print(f"  API Docs:  http://localhost:{API_PORT}/docs")
    print(f"\n  Các bước sử dụng:")
    print(f"  1. Mở dashboard tại URL trên")
    print(f"  2. Nhấn 'Thu thập dữ liệu' để crawl GitHub")
    print(f"  3. Chờ phân tích AI hoàn tất")
    print(f"  4. Xem xu hướng công nghệ trên dashboard")
    print("=" * 60)

    uvicorn.run(
        "api.app:app",
        host=API_HOST,
        port=API_PORT,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
