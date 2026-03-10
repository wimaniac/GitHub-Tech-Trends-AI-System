"""
Text Processor — Tiền xử lý văn bản và trích xuất từ khóa công nghệ.
"""
import re
from collections import Counter
from typing import Optional


# Danh sách công nghệ/framework/tool phổ biến để detect
KNOWN_TECHNOLOGIES = {
    # AI / ML
    "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
    "huggingface", "transformers", "langchain", "llamaindex", "openai",
    "stable-diffusion", "diffusers", "onnx", "mlflow", "wandb",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
    "jupyter", "colab", "kaggle", "fastai", "jax", "flax",

    # LLM / GenAI
    "gpt", "llama", "mistral", "claude", "gemini", "chatgpt",
    "ollama", "vllm", "llm", "rag", "vector-database", "embedding",
    "fine-tuning", "lora", "qlora", "prompt-engineering",

    # Web Frontend
    "react", "vue", "angular", "svelte", "nextjs", "nuxt", "remix",
    "astro", "solid", "qwik", "htmx", "alpine", "tailwind",
    "bootstrap", "material-ui", "chakra-ui", "shadcn",

    # Web Backend
    "express", "fastapi", "django", "flask", "spring", "nestjs",
    "gin", "fiber", "actix", "axum", "rocket", "rails",
    "laravel", "graphql", "trpc", "hono",

    # Mobile
    "flutter", "react-native", "kotlin", "swift", "swiftui",
    "jetpack-compose", "expo", "capacitor", "ionic",

    # DevOps / Cloud
    "docker", "kubernetes", "terraform", "ansible", "jenkins",
    "github-actions", "gitlab-ci", "argocd", "helm",
    "aws", "azure", "gcp", "vercel", "netlify", "cloudflare",

    # Database
    "postgresql", "mongodb", "redis", "elasticsearch", "supabase",
    "prisma", "drizzle", "sqlite", "cassandra", "neo4j",
    "pinecone", "weaviate", "qdrant", "chroma", "milvus",

    # Languages
    "rust", "golang", "typescript", "python", "java", "kotlin",
    "swift", "zig", "gleam", "elixir", "clojure", "haskell",

    # Tools
    "git", "vscode", "neovim", "tmux", "wasm", "webassembly",
    "grpc", "protobuf", "kafka", "rabbitmq", "nats",
    "bun", "deno", "turbo", "vite", "webpack", "esbuild",
}

# Mapping categories
CATEGORY_MAP = {
    "AI/ML": {
        "tensorflow", "pytorch", "keras", "scikit-learn", "xgboost", "lightgbm",
        "huggingface", "transformers", "langchain", "llamaindex", "openai",
        "stable-diffusion", "diffusers", "mlflow", "wandb", "fastai", "jax", "flax",
        "gpt", "llama", "mistral", "claude", "gemini", "chatgpt", "ollama", "vllm",
        "llm", "rag", "vector-database", "embedding", "fine-tuning", "lora", "qlora",
        "prompt-engineering", "deep-learning", "machine-learning", "neural-network",
        "computer-vision", "nlp", "reinforcement-learning",
    },
    "Web Frontend": {
        "react", "vue", "angular", "svelte", "nextjs", "nuxt", "remix",
        "astro", "solid", "qwik", "htmx", "alpine", "tailwind",
        "bootstrap", "material-ui", "chakra-ui", "shadcn",
    },
    "Web Backend": {
        "express", "fastapi", "django", "flask", "spring", "nestjs",
        "gin", "fiber", "actix", "axum", "rocket", "rails",
        "laravel", "graphql", "trpc", "hono",
    },
    "Mobile": {
        "flutter", "react-native", "kotlin", "swiftui",
        "jetpack-compose", "expo", "capacitor", "ionic",
    },
    "DevOps": {
        "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "github-actions", "gitlab-ci", "argocd", "helm",
        "aws", "azure", "gcp", "vercel", "netlify", "cloudflare",
    },
    "Database": {
        "postgresql", "mongodb", "redis", "elasticsearch", "supabase",
        "prisma", "drizzle", "sqlite", "cassandra", "neo4j",
        "pinecone", "weaviate", "qdrant", "chroma", "milvus",
    },
    "Languages": {
        "rust", "golang", "typescript", "python", "java",
        "swift", "zig", "gleam", "elixir", "clojure", "haskell",
    },
    "Tools": {
        "git", "vscode", "neovim", "wasm", "webassembly",
        "grpc", "protobuf", "kafka", "rabbitmq", "nats",
        "bun", "deno", "turbo", "vite", "webpack", "esbuild",
    },
}


def clean_text(text: str) -> str:
    """Làm sạch nội dung text/markdown."""
    if not text:
        return ""
    # Xóa URLs
    text = re.sub(r'https?://\S+', ' ', text)
    # Xóa markdown images
    text = re.sub(r'!\[.*?\]\(.*?\)', ' ', text)
    # Xóa markdown links nhưng giữ text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    # Xóa markdown headers
    text = re.sub(r'#+\s*', '', text)
    # Xóa code blocks
    text = re.sub(r'```[\s\S]*?```', ' ', text)
    text = re.sub(r'`[^`]+`', ' ', text)
    # Xóa HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # Xóa ký tự đặc biệt
    text = re.sub(r'[^\w\s\-\.]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def extract_technologies(text: str, topics: list = None) -> list[str]:
    """Trích xuất tên công nghệ từ text và topics."""
    found = set()
    text_lower = text.lower() if text else ""

    # Tìm trong text
    for tech in KNOWN_TECHNOLOGIES:
        # Tạo pattern tìm kiếm
        pattern = r'\b' + re.escape(tech.replace("-", r"[\s\-]?")) + r'\b'
        if re.search(pattern, text_lower):
            found.add(tech)

    # Tìm trong topics
    if topics:
        for topic in topics:
            topic_lower = topic.lower().strip()
            if topic_lower in KNOWN_TECHNOLOGIES:
                found.add(topic_lower)
            # Kiểm tra partial matches
            for tech in KNOWN_TECHNOLOGIES:
                if tech in topic_lower or topic_lower in tech:
                    found.add(tech)

    return sorted(found)


def get_category(tech_name: str) -> str:
    """Xác định category cho 1 công nghệ."""
    tech_lower = tech_name.lower()
    for category, techs in CATEGORY_MAP.items():
        if tech_lower in techs:
            return category
    return "Other"


def extract_keywords(text: str, top_n: int = 20) -> list[tuple]:
    """Trích xuất từ khóa quan trọng (đơn giản, không dùng TF-IDF nặng)."""
    if not text:
        return []

    text = clean_text(text).lower()
    # Loại bỏ stop words phổ biến
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "shall", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "this", "that",
        "these", "those", "it", "its", "and", "but", "or", "not", "no",
        "all", "each", "every", "both", "few", "more", "most", "other",
        "some", "such", "only", "own", "same", "than", "too", "very",
        "just", "about", "also", "how", "what", "when", "where", "who",
        "which", "why", "use", "using", "used", "new", "one", "two",
        "file", "files", "based", "project", "see", "like", "make",
        "get", "set", "run", "build", "add", "create", "update",
    }

    words = re.findall(r'\b[a-z][a-z\-]{2,}\b', text)
    words = [w for w in words if w not in stop_words and len(w) > 2]

    counter = Counter(words)
    return counter.most_common(top_n)


def prepare_text_for_embedding(repo_data: dict) -> str:
    """Chuẩn bị text đầu vào cho embedding model."""
    parts = []

    if repo_data.get("description"):
        parts.append(repo_data["description"])

    if repo_data.get("topics"):
        parts.append("Topics: " + ", ".join(repo_data["topics"]))

    if repo_data.get("language"):
        parts.append(f"Language: {repo_data['language']}")

    if repo_data.get("readme_content"):
        # Lấy 1000 ký tự đầu của README đã clean
        readme = clean_text(repo_data["readme_content"])[:1000]
        parts.append(readme)

    return " ".join(parts)
