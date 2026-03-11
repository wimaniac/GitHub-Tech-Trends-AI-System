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

    # Sắp xếp theo mức độ tăng trưởng kì vọng (predicted_score - current_score)
    # Tức là ưu tiên "Dự đoán sẽ tăng mạnh nhất" thay vì "Điểm to nhất"
    predictions.sort(key=lambda x: x["predicted_score"] - x["current_score"], reverse=True)
    
    # Lọc bỏ những cái dự đoán không tăng (hoặc giảm) nếu muốn, nhưng ở đây cứ lấy top N tăng mạnh nhất
    result = predictions[:top_n]

    print(f"[Predictor] Đã tạo {len(result)} predictions")
    return result


async def _predict_single(trend) -> Optional[dict]:
    """Dự đoán cho 1 công nghệ."""
    try:
        # Lấy timeline data
        timeline = await get_trend_timeline(tech_name=trend.technology_name)
        scores = [t["score"] for t in timeline]

        if len(scores) >= 5:
            # Đủ dữ liệu => dùng mô hình Momentum/Exponential Growth (EMA crossover)
            predicted_score = _momentum_forecast(scores)
            confidence = _calculate_confidence(scores)
            method = "exponential_momentum"
        elif len(scores) >= 2:
            # Ít dữ liệu => dùng exponential smoothing cơ bản
            predicted_score = _exponential_smooth(scores)
            confidence = 0.4 + (min(len(scores), 5) * 0.05)
            method = "exponential_smoothing"
        else:
            # Không đủ timeline => dùng trend_score hiện tại và cộng biên độ
            base_score = scores[-1] if scores else trend.trend_score
            predicted_score = base_score * 1.05
            confidence = 0.3
            method = "extrapolation"

        # Xác định momentum string hiển thị
        momentum = _calculate_momentum(trend)

        # Predicted status (đối chiếu với base lúc này)
        base_for_status = scores[-1] if scores else trend.trend_score
        
        if predicted_score > base_for_status * 1.15:
            predicted_status = "rising"
        elif predicted_score > base_for_status * 0.95:
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


def _ema(values: list[float], span: int) -> list[float]:
    """Tính toán Exponential Moving Average."""
    if not values:
        return []
        
    alpha = 2 / (span + 1)
    ema_vals = [values[0]]
    for val in values[1:]:
        ema_vals.append(alpha * val + (1 - alpha) * ema_vals[-1])
    return ema_vals


def _momentum_forecast(scores: list[float]) -> float:
    """
    Dự báo bằng mô hình Momentum (dựa trên EMA Crossover).
    Cực nhạy với các trend bùng nổ (exponential growth).
    """
    short_span = max(2, min(3, len(scores) // 2))
    long_span = max(3, min(5, len(scores)))
    
    ema_short = _ema(scores, short_span)
    ema_long = _ema(scores, long_span)
    
    if not ema_short or not ema_long:
        return scores[-1] if scores else 0.0
        
    # Velocity (gia tốc) = khoảng cách phân kỳ giữa EMA ngắn và dài
    current_velocity = ema_short[-1] - ema_long[-1]
    
    # Base prediction = EMA ngắn hạn gần nhất (phản ánh xu hướng gần đây nhất)
    base = ema_short[-1]
    
    # Kiểm tra exponential momentum
    if current_velocity > 0:
        # Nếu đang trong uptrend (đường ngắn cắt lên đường dài)
        trend_ratio = ema_short[-1] / (ema_long[-1] + 1e-5)
        # Hệ số gia tốc (compound factor): giới hạn [1.0 -> 1.5] để không over-predict
        compound_factor = min(max(trend_ratio, 1.0), 1.5)
        predicted = base + (current_velocity * compound_factor)
    else:
        # Đang downtrend hoặc chững lại
        predicted = base + current_velocity
        
    return float(max(0, predicted))


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
