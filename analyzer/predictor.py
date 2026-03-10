"""
Predictor — Dự đoán xu hướng công nghệ trong tương lai.
Sử dụng linear regression và exponential smoothing.
"""
import numpy as np
from datetime import datetime, timedelta
from typing import Optional

from database.db import get_trends, get_trend_timeline


async def predict_trends(top_n: int = 20) -> list[dict]:
    """
    Dự đoán xu hướng công nghệ cho tương lai gần.
    
    Returns:
        List predictions sorted by predicted_score giảm dần
    """
    print("[Predictor] Bắt đầu dự đoán xu hướng...")

    trends = await get_trends(limit=top_n * 2)
    if not trends:
        print("[Predictor] Không có trends để dự đoán.")
        return []

    predictions = []
    for trend in trends:
        prediction = await _predict_single(trend)
        if prediction:
            predictions.append(prediction)

    # Sắp xếp theo predicted score
    predictions.sort(key=lambda x: x["predicted_score"], reverse=True)
    result = predictions[:top_n]

    print(f"[Predictor] Đã tạo {len(result)} predictions")
    return result


async def _predict_single(trend) -> Optional[dict]:
    """Dự đoán cho 1 công nghệ."""
    try:
        # Lấy timeline data
        timeline = await get_trend_timeline(tech_name=trend.technology_name)

        if len(timeline) >= 3:
            # Có đủ dữ liệu time-series => dùng linear regression
            scores = [t["score"] for t in timeline]
            predicted_score = _linear_forecast(scores, steps=1)
            confidence = _calculate_confidence(scores)
            method = "linear_regression"
        elif len(timeline) >= 1:
            # Ít dữ liệu => dùng exponential smoothing
            scores = [t["score"] for t in timeline]
            predicted_score = _exponential_smooth(scores)
            confidence = 0.4  # confidence thấp vì ít data
            method = "exponential_smoothing"
        else:
            # Không có timeline => dùng trend_score hiện tại
            predicted_score = trend.trend_score * 1.05  # assume 5% growth
            confidence = 0.3
            method = "current_extrapolation"

        # Xác định momentum
        momentum = _calculate_momentum(trend)

        # Predicted status
        if predicted_score > trend.trend_score * 1.2:
            predicted_status = "rising"
        elif predicted_score > trend.trend_score * 0.95:
            predicted_status = "stable"
        else:
            predicted_status = "declining"

        return {
            "technology_name": trend.technology_name,
            "category": trend.category,
            "current_score": round(trend.trend_score, 2),
            "predicted_score": round(max(predicted_score, 0), 2),
            "growth_rate": round(trend.growth_rate, 2),
            "confidence": round(confidence, 2),
            "momentum": momentum,
            "predicted_status": predicted_status,
            "method": method,
            "repo_count": trend.repo_count,
            "avg_stars": round(trend.avg_stars, 1),
        }
    except Exception as e:
        print(f"[Predictor] Lỗi dự đoán {trend.technology_name}: {e}")
        return None


def _linear_forecast(values: list[float], steps: int = 1) -> float:
    """Dự đoán bằng linear regression đơn giản."""
    if len(values) < 2:
        return values[-1] if values else 0

    x = np.arange(len(values))
    y = np.array(values)

    # Fit linear regression
    coeffs = np.polyfit(x, y, 1)
    # Predict next step
    next_x = len(values) + steps - 1
    return float(np.polyval(coeffs, next_x))


def _exponential_smooth(values: list[float], alpha: float = 0.3) -> float:
    """Exponential smoothing cho short-term prediction."""
    if not values:
        return 0

    smoothed = values[0]
    for val in values[1:]:
        smoothed = alpha * val + (1 - alpha) * smoothed

    # Predict: add momentum
    if len(values) >= 2:
        trend = values[-1] - values[-2]
        return smoothed + trend * 0.5
    return smoothed


def _calculate_confidence(scores: list[float]) -> float:
    """
    Tính confidence score (0-1) dựa trên:
    - Số lượng data points
    - Độ ổn định (variance thấp = confidence cao)
    """
    if len(scores) < 2:
        return 0.3

    # Data points factor
    data_factor = min(len(scores) / 10.0, 1.0) * 0.5

    # Stability factor (lower variance = higher confidence)
    cv = np.std(scores) / (np.mean(scores) + 1e-8)  # coefficient of variation
    stability_factor = max(1.0 - cv, 0) * 0.5

    return min(data_factor + stability_factor, 1.0)


def _calculate_momentum(trend) -> str:
    """Xác định momentum của trend."""
    if trend.growth_rate > 60:
        return "🚀 Tăng mạnh"
    elif trend.growth_rate > 30:
        return "📈 Đang tăng"
    elif trend.growth_rate > 10:
        return "➡️ Ổn định"
    elif trend.growth_rate > 0:
        return "📊 Chậm lại"
    else:
        return "📉 Giảm"
