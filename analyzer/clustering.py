"""
Clustering — Phân cụm repositories theo nội dung sử dụng embeddings.
"""
import numpy as np
from collections import Counter
from typing import Optional

from config import MIN_CLUSTER_SIZE, CLUSTERING_MIN_SAMPLES


def cluster_repositories(embeddings: list[list[float]], labels: list[str] = None) -> dict:
    """
    Phân cụm repos dựa trên embeddings.
    
    Args:
        embeddings: List các embedding vectors
        labels: Tên/ID tương ứng cho mỗi embedding (optional)
    
    Returns:
        Dict chứa cluster assignments và thống kê
    """
    valid = [(i, emb) for i, emb in enumerate(embeddings) if emb is not None]
    if len(valid) < MIN_CLUSTER_SIZE:
        print(f"[Clustering] Không đủ dữ liệu ({len(valid)} < {MIN_CLUSTER_SIZE})")
        return {"clusters": {}, "noise": list(range(len(embeddings)))}

    indices = [v[0] for v in valid]
    X = np.array([v[1] for v in valid])

    # Thử HDBSCAN trước, fallback sang KMeans
    try:
        cluster_labels = _hdbscan_cluster(X)
    except Exception as e:
        print(f"[Clustering] HDBSCAN failed ({e}), dùng KMeans...")
        cluster_labels = _kmeans_cluster(X)

    # Tổ chức kết quả
    clusters = {}
    noise = []

    for i, cl in enumerate(cluster_labels):
        original_idx = indices[i]
        if cl == -1:
            noise.append(original_idx)
        else:
            if cl not in clusters:
                clusters[cl] = []
            clusters[cl].append(original_idx)

    print(f"[Clustering] Tìm thấy {len(clusters)} clusters, {len(noise)} noise points")
    return {
        "clusters": clusters,
        "noise": noise,
        "n_clusters": len(clusters),
    }


def _hdbscan_cluster(X: np.ndarray) -> list[int]:
    """Clustering bằng HDBSCAN."""
    try:
        import hdbscan
        clusterer = hdbscan.HDBSCAN(
            min_cluster_size=MIN_CLUSTER_SIZE,
            min_samples=CLUSTERING_MIN_SAMPLES,
            metric="cosine",
        )
        return clusterer.fit_predict(X).tolist()
    except ImportError:
        raise RuntimeError("hdbscan chưa được cài đặt")


def _kmeans_cluster(X: np.ndarray, max_clusters: int = 15) -> list[int]:
    """Clustering bằng KMeans với tự chọn k tối ưu."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    n_samples = len(X)
    if n_samples < 4:
        return [0] * n_samples

    best_k = 3
    best_score = -1

    k_range = range(2, min(max_clusters, n_samples // 2 + 1))

    for k in k_range:
        try:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            score = silhouette_score(X, labels)
            if score > best_score:
                best_score = score
                best_k = k
        except Exception:
            continue

    final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    return final_kmeans.fit_predict(X).tolist()


def label_clusters(clusters: dict, repo_technologies: dict) -> dict:
    """
    Gán label cho mỗi cluster dựa trên công nghệ phổ biến nhất.
    
    Args:
        clusters: Dict {cluster_id: [repo_indices]}
        repo_technologies: Dict {repo_index: [tech_names]}
    
    Returns:
        Dict {cluster_id: {"label": str, "top_techs": list, "size": int}}
    """
    cluster_info = {}

    for cl_id, indices in clusters.items():
        all_techs = []
        for idx in indices:
            techs = repo_technologies.get(idx, [])
            all_techs.extend(techs)

        tech_counts = Counter(all_techs)
        top_techs = tech_counts.most_common(5)

        label = top_techs[0][0] if top_techs else f"cluster-{cl_id}"

        cluster_info[cl_id] = {
            "label": label,
            "top_techs": [{"name": t, "count": c} for t, c in top_techs],
            "size": len(indices),
        }

    return cluster_info
