/**
 * GitHub Tech Trends AI — Dashboard JavaScript
 * Theme toggle, i18n, pagination, autocomplete, category cards, chatbot.
 */

// ============ CONFIG ============
const API_BASE = '/api';
const REFRESH_INTERVAL = 60000;
const TRENDS_PER_PAGE = 12;
const REPOS_PER_PAGE = 15;

// Language colors (GitHub style)
const LANG_COLORS = {
    'Python': '#3572A5', 'JavaScript': '#f1e05a', 'TypeScript': '#3178c6',
    'Rust': '#dea584', 'Go': '#00ADD8', 'Java': '#b07219',
    'C++': '#f34b7d', 'C#': '#178600', 'Swift': '#F05138',
    'Kotlin': '#A97BFF', 'Dart': '#00B4AB', 'Ruby': '#701516',
    'PHP': '#4F5D95', 'C': '#555555', 'Shell': '#89e051',
    'Lua': '#000080', 'Zig': '#ec915c', 'Elixir': '#6e4a7e',
    'Haskell': '#5e5086', 'Scala': '#c22d40',
};

// Category icons
const CATEGORY_ICONS = {
    'AI/ML': '🧠', 'Web Frontend': '🎨', 'Web Backend': '⚙️',
    'Mobile': '📱', 'DevOps': '☁️', 'Database': '🗄️',
    'Languages': '💻', 'Tools': '🔧', 'Security': '🔒',
    'Blockchain': '⛓️', 'Data Engineering': '📊', 'Game Dev': '🎮',
    'IoT': '📡', 'Other': '📦',
};

// ============ i18n ============
const i18nDict = {
    vi: {
        subtitle: 'Phân tích xu hướng công nghệ thời gian thực',
        search_placeholder: 'Tìm kiếm công nghệ...',
        collect: 'Thu thập',
        trends: 'Xu hướng',
        rising: 'Đang tăng',
        emerging: 'Mới nổi',
        categories: 'Danh mục',
        explore_categories: 'Khám phá theo danh mục',
        all: 'Tất cả',
        sort_by: 'Sắp xếp:',
        trend_score: 'Điểm xu hướng',
        growth_rate: 'Tốc độ tăng',
        repo_count: 'Số repo',
        trending_tech: 'Xu hướng công nghệ nổi bật',
        loading: 'Đang tải dữ liệu...',
        analytics_charts: 'Biểu đồ phân tích',
        top_tech_score: 'Top Công nghệ theo Trend Score',
        category_distribution: 'Phân bố theo danh mục',
        predictions: 'Dự đoán xu hướng',
        analyzing_predictions: 'Đang phân tích dự đoán...',
        collected_repos: 'Repositories đã thu thập',
        language: 'Ngôn ngữ',
        ask_me: 'Hỏi tôi về xu hướng công nghệ',
        chatbot_welcome: 'Xin chào! Tôi là trợ lý AI. Hãy hỏi tôi về xu hướng công nghệ trên GitHub!',
        chat_placeholder: 'Nhập câu hỏi...',
        suggest_trending: 'Xu hướng nào đang hot nhất?',
        suggest_compare: 'So sánh React vs Vue',
        suggest_find: 'Tìm repo về AI/ML',
        created_by: 'Được tạo bởi AI',
        footer_info: 'Dữ liệu từ GitHub • Phân tích bằng AI • Cập nhật tự động',
        no_trends_data: 'Chưa có dữ liệu xu hướng',
        no_trends_hint: 'Nhấn "Thu thập" để bắt đầu crawl dữ liệu từ GitHub',
        no_predictions: 'Chưa có dự đoán',
        no_predictions_hint: 'Dự đoán sẽ xuất hiện sau khi phân tích dữ liệu',
        no_repos: 'Chưa có repositories',
        current: 'Hiện tại',
        predicted: 'Dự đoán',
        change: 'Thay đổi',
        confidence: 'Độ tin cậy',
        first_detected: 'Lần đầu phát hiện',
        collecting: 'Đang thu thập...',
        collect_success: '✅ Đã bắt đầu thu thập dữ liệu từ GitHub!',
        collect_error: '❌ Lỗi khi thu thập!',
        not_found: 'Không tìm thấy thông tin.',
        prev: '← Trước',
        next: 'Sau →',
    },
    en: {
        subtitle: 'Real-time technology trend analysis',
        search_placeholder: 'Search technologies...',
        collect: 'Collect',
        trends: 'Trends',
        rising: 'Rising',
        emerging: 'Emerging',
        categories: 'Categories',
        explore_categories: 'Explore by Category',
        all: 'All',
        sort_by: 'Sort:',
        trend_score: 'Trend Score',
        growth_rate: 'Growth Rate',
        repo_count: 'Repo Count',
        trending_tech: 'Trending Technologies',
        loading: 'Loading data...',
        analytics_charts: 'Analytics Charts',
        top_tech_score: 'Top Technologies by Trend Score',
        category_distribution: 'Distribution by Category',
        predictions: 'Trend Predictions',
        analyzing_predictions: 'Analyzing predictions...',
        collected_repos: 'Collected Repositories',
        language: 'Language',
        ask_me: 'Ask me about tech trends',
        chatbot_welcome: 'Hi! I\'m your AI assistant. Ask me about technology trends on GitHub!',
        chat_placeholder: 'Type your question...',
        suggest_trending: 'What\'s trending right now?',
        suggest_compare: 'Compare React vs Vue',
        suggest_find: 'Find AI/ML repos',
        created_by: 'Created by AI',
        footer_info: 'Data from GitHub • AI Analysis • Auto-updated',
        no_trends_data: 'No trend data available',
        no_trends_hint: 'Click "Collect" to start crawling data from GitHub',
        no_predictions: 'No predictions yet',
        no_predictions_hint: 'Predictions will appear after data analysis',
        no_repos: 'No repositories yet',
        current: 'Current',
        predicted: 'Predicted',
        change: 'Change',
        confidence: 'Confidence',
        first_detected: 'First detected',
        collecting: 'Collecting...',
        collect_success: '✅ Started collecting data from GitHub!',
        collect_error: '❌ Error during collection!',
        not_found: 'Information not found.',
        prev: '← Prev',
        next: 'Next →',
    },
};

// ============ STATE ============
let currentLang = localStorage.getItem('lang') || 'vi';
let currentTheme = localStorage.getItem('theme') || 'dark';
let currentCategory = 'all';
let currentSort = 'growth_rate';
let allTrends = [];
let allRepos = [];
let trendPage = 1;
let repoPage = 1;
let charts = {};

// ============ INIT ============
document.addEventListener('DOMContentLoaded', () => {
    try {
        applyTheme(currentTheme);
    } catch (e) {
        console.error("Error applying theme:", e);
    }
    
    try {
        applyLanguage(currentLang);
    } catch (e) {
        console.error("Error applying language:", e);
    }
    
    try {
        setupEventListeners();
    } catch (e) {
        console.error("Error setting up event listeners:", e);
    }
    
    loadAllData().catch(e => console.error("Error loading data:", e));
    setInterval(() => loadAllData().catch(e => console.error(e)), REFRESH_INTERVAL);
});

// ============ THEME ============
function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    const themeIcon = document.getElementById('themeIcon');
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
    }

    // Update Chart.js colors (Safeguard in case Chart is not loaded)
    if (typeof Chart !== 'undefined' && Chart.defaults) {
        const isDark = theme === 'dark';
        Chart.defaults.color = isDark ? '#94a3b8' : '#475569';
        Chart.defaults.borderColor = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)';
        if (!Chart.defaults.font) Chart.defaults.font = {};
        Chart.defaults.font.family = "'Inter', sans-serif";
    }
}

function toggleTheme() {
    applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
    // Redraw charts
    if (allTrends && allTrends.length) renderTrendScoreChart(allTrends.slice(0, 12));
}

// ============ i18n ============
function t(key) {
    return (i18nDict[currentLang] && i18nDict[currentLang][key]) || key;
}

function applyLanguage(lang) {
    currentLang = lang;
    localStorage.setItem('lang', lang);

    // Update label
    document.getElementById('langLabel').textContent = lang === 'vi' ? '🇻🇳 VI' : '🇺🇸 EN';

    // Update HTML lang
    document.documentElement.lang = lang;

    // Update all data-i18n elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18nDict[lang] && i18nDict[lang][key]) {
            el.textContent = i18nDict[lang][key];
        }
    });

    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (i18nDict[lang] && i18nDict[lang][key]) {
            el.placeholder = i18nDict[lang][key];
        }
    });
}

function toggleLanguage() {
    applyLanguage(currentLang === 'vi' ? 'en' : 'vi');
    // Re-render dynamic content
    if (allTrends.length) renderTrends(getPagedTrends());
    if (allRepos.length) renderRepoTable(getPagedRepos());
}

// ============ EVENT LISTENERS ============
function setupEventListeners() {
    // Helper
    const bind = (id, event, handler) => {
        const el = document.getElementById(id);
        if (el) el.addEventListener(event, handler);
    };

    // Search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(handleSearch, 300));
        searchInput.addEventListener('focus', () => {
            if (searchInput.value.trim().length >= 2) fetchSuggestions(searchInput.value.trim());
        });
    }
    
    document.addEventListener('click', (e) => {
        const sugg = document.getElementById('searchSuggestions');
        if (sugg && !e.target.closest('.search-box')) {
            sugg.classList.remove('active');
        }
    });

    // Collect button
    bind('btnCollect', 'click', triggerCollect);

    // Sort select
    bind('sortSelect', 'change', (e) => {
        currentSort = e.target.value;
        trendPage = 1;
        loadTrends();
    });

    // Category filter "all" button
    const btnAllCategory = document.querySelector('.filter-btn[data-category="all"]');
    if (btnAllCategory) {
        btnAllCategory.addEventListener('click', () => {
            currentCategory = 'all';
            trendPage = 1;
            updateFilterButtons();
            renderTrends(getPagedTrends());
            renderTrendsPagination();
        });
    }

    // Theme & Language
    bind('btnTheme', 'click', toggleTheme);
    bind('btnLang', 'click', toggleLanguage);

    // Modal close
    bind('modalClose', 'click', closeModal);
    bind('detailModal', 'click', (e) => {
        if (e.target === e.currentTarget) closeModal();
    });

    // Keyboard
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeModal();
            closeChatbot();
        }
    });

    // Chatbot
    bind('chatbotFab', 'click', openChatbot);
    bind('chatbotClose', 'click', closeChatbot);
    bind('chatSend', 'click', sendChatMessage);
    
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    // Chat suggestion buttons
    document.querySelectorAll('.chat-suggestion-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const input = document.getElementById('chatInput');
            if (input) input.value = btn.textContent;
            sendChatMessage();
        });
    });
}

// ============ DATA LOADING ============
async function loadAllData() {
    await Promise.all([
        loadStats(),
        loadTrends(),
        loadCategories(),
        loadPredictions(),
        loadRepos(),
    ]);
}

async function apiFetch(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, options);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (err) {
        console.error(`API Error [${endpoint}]:`, err);
        return null;
    }
}

async function loadStats() {
    const data = await apiFetch('/stats');
    if (!data) return;

    animateCounter('statRepos', data.total_repos || 0);
    animateCounter('statTrends', data.total_trends || 0);
    animateCounter('statRising', data.rising_count || 0);
    animateCounter('statEmerging', data.emerging_count || 0);
    animateCounter('statCategories', data.categories || 0);
}

async function loadTrends() {
    const params = new URLSearchParams({ limit: '100', sort_by: currentSort });
    if (currentCategory !== 'all') params.set('category', currentCategory);

    const data = await apiFetch(`/trends?${params}`);
    if (!data) {
        showEmptyState('trendsGrid', '📊', t('no_trends_data'), t('no_trends_hint'));
        return;
    }

    allTrends = data.trends || [];
    renderTrends(getPagedTrends());
    renderTrendsPagination();
    renderTrendScoreChart(allTrends.slice(0, 12));
}

async function loadCategories() {
    const data = await apiFetch('/categories');
    if (!data || !data.categories) return;

    // Render category cards
    renderCategoryCards(data.categories);

    // Render filter pills
    const container = document.getElementById('categoryFilters');
    container.innerHTML = data.categories.map(c =>
        `<button class="filter-btn${currentCategory === c.category ? ' active' : ''}" 
                 data-category="${c.category}" onclick="filterByCategory('${c.category}')">
            ${c.category} (${c.count})
        </button>`
    ).join('');

    renderCategoryChart(data.categories);
}

async function loadPredictions() {
    const data = await apiFetch('/predictions?top_n=12');
    if (!data || !data.predictions || data.predictions.length === 0) {
        showEmptyState('predictionsGrid', '🔮', t('no_predictions'), t('no_predictions_hint'));
        return;
    }
    renderPredictions(data.predictions);
}

async function loadRepos() {
    const data = await apiFetch('/repos?limit=200');
    if (!data || !data.repos || data.repos.length === 0) {
        document.getElementById('repoTableBody').innerHTML =
            `<tr><td colspan="5" class="empty-state"><div class="empty-state-icon">📁</div><p>${t('no_repos')}</p></td></tr>`;
        return;
    }
    allRepos = data.repos;
    renderRepoTable(getPagedRepos());
    renderReposPagination();
}

// ============ PAGINATION ============
function getPagedTrends() {
    const filtered = currentCategory === 'all'
        ? allTrends
        : allTrends.filter(t => t.category === currentCategory);
    const start = (trendPage - 1) * TRENDS_PER_PAGE;
    return filtered.slice(start, start + TRENDS_PER_PAGE);
}

function getTotalTrendPages() {
    const filtered = currentCategory === 'all'
        ? allTrends
        : allTrends.filter(t => t.category === currentCategory);
    return Math.ceil(filtered.length / TRENDS_PER_PAGE) || 1;
}

function renderTrendsPagination() {
    const total = getTotalTrendPages();
    renderPagination('trendsPagination', trendPage, total, (page) => {
        trendPage = page;
        renderTrends(getPagedTrends());
        renderTrendsPagination();
        document.getElementById('trendsGrid').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
}

function getPagedRepos() {
    const start = (repoPage - 1) * REPOS_PER_PAGE;
    return allRepos.slice(start, start + REPOS_PER_PAGE);
}

function getTotalRepoPages() {
    return Math.ceil(allRepos.length / REPOS_PER_PAGE) || 1;
}

function renderReposPagination() {
    const total = getTotalRepoPages();
    renderPagination('reposPagination', repoPage, total, (page) => {
        repoPage = page;
        renderRepoTable(getPagedRepos());
        renderReposPagination();
        document.getElementById('repoTable').scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
}

function renderPagination(containerId, currentPage, totalPages, onPageChange) {
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 1) {
        if (container) container.innerHTML = '';
        return;
    }

    let html = '';

    // Previous
    html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} 
             onclick="window._pagination_${containerId}(${currentPage - 1})">${t('prev')}</button>`;

    // Page numbers
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) startPage = Math.max(1, endPage - maxVisible + 1);

    if (startPage > 1) {
        html += `<button class="page-btn" onclick="window._pagination_${containerId}(1)">1</button>`;
        if (startPage > 2) html += `<span class="page-info">...</span>`;
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `<button class="page-btn${i === currentPage ? ' active' : ''}" 
                 onclick="window._pagination_${containerId}(${i})">${i}</button>`;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) html += `<span class="page-info">...</span>`;
        html += `<button class="page-btn" onclick="window._pagination_${containerId}(${totalPages})">${totalPages}</button>`;
    }

    // Next
    html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} 
             onclick="window._pagination_${containerId}(${currentPage + 1})">${t('next')}</button>`;

    container.innerHTML = html;

    // Register callback
    window[`_pagination_${containerId}`] = onPageChange;
}

// ============ RENDERING ============
function renderCategoryCards(categories) {
    const container = document.getElementById('categoryCards');
    if (!container) return;

    // Add "All" card
    let html = `
        <div class="category-card${currentCategory === 'all' ? ' active' : ''}" 
             onclick="filterByCategory('all')">
            <div class="category-card-icon">🌐</div>
            <div class="category-card-name">${t('all')}</div>
        </div>`;

    html += categories.map(c => `
        <div class="category-card${currentCategory === c.category ? ' active' : ''}" 
             onclick="filterByCategory('${c.category}')">
            <div class="category-card-icon">${CATEGORY_ICONS[c.category] || '📦'}</div>
            <div class="category-card-name">${c.category}</div>
            <div class="category-card-count">${c.count} ${t('trends').toLowerCase()}</div>
        </div>
    `).join('');

    container.innerHTML = html;
}

function renderTrends(trends) {
    const grid = document.getElementById('trendsGrid');

    if (!trends || trends.length === 0) {
        showEmptyState('trendsGrid', '📊', t('no_trends_data'), t('no_trends_hint'));
        return;
    }

    grid.innerHTML = trends.map((tr, i) => `
        <div class="trend-card" onclick="showTrendDetail('${tr.technology_name}')" style="animation-delay: ${i * 0.05}s">
            <div class="trend-card-header">
                <span class="trend-name">${escapeHtml(tr.technology_name)}</span>
                <span class="trend-status status-${tr.status}">${tr.status}</span>
            </div>
            <div class="trend-category">${escapeHtml(tr.category)}</div>
            <div class="trend-description">${escapeHtml(tr.description || '')}</div>
            <div class="trend-metrics">
                <div class="metric">
                    <span class="metric-value">${formatNumber(tr.trend_score)}</span>
                    <span class="metric-label">Score</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${formatNumber(tr.repo_count)}</span>
                    <span class="metric-label">Repos</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${formatNumber(tr.avg_stars)}</span>
                    <span class="metric-label">Avg ⭐</span>
                </div>
            </div>
        </div>
    `).join('');

    // Staggered animation
    grid.querySelectorAll('.trend-card').forEach((card, i) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, i * 60);
    });
}

function renderPredictions(predictions) {
    const grid = document.getElementById('predictionsGrid');

    grid.innerHTML = predictions.map(p => {
        const change = p.predicted_score - p.current_score;
        const changePercent = p.current_score > 0 ? ((change / p.current_score) * 100).toFixed(1) : 0;
        const barWidth = Math.min((p.confidence || 0) * 100, 100);

        return `
        <div class="prediction-card">
            <div class="prediction-header">
                <span class="prediction-name">${escapeHtml(p.technology_name)}</span>
                <span class="prediction-momentum">${p.momentum || ''}</span>
            </div>
            <div class="prediction-scores">
                <div class="prediction-score">
                    <span class="prediction-score-label">${t('current')}</span>
                    <span class="prediction-score-value score-current">${formatNumber(p.current_score)}</span>
                </div>
                <div class="prediction-score">
                    <span class="prediction-score-label">${t('predicted')}</span>
                    <span class="prediction-score-value score-predicted">${formatNumber(p.predicted_score)}</span>
                </div>
                <div class="prediction-score">
                    <span class="prediction-score-label">${t('change')}</span>
                    <span class="prediction-score-value" style="color: ${change >= 0 ? 'var(--accent-green)' : 'var(--accent-red)'}">
                        ${change >= 0 ? '+' : ''}${changePercent}%
                    </span>
                </div>
            </div>
            <div class="prediction-bar">
                <div class="prediction-bar-fill" style="width: ${barWidth}%"></div>
            </div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 4px;">
                ${t('confidence')}: ${(p.confidence * 100).toFixed(0)}% • ${p.method || ''}
            </div>
        </div>
    `}).join('');
}

function renderRepoTable(repos) {
    const tbody = document.getElementById('repoTableBody');

    tbody.innerHTML = repos.map(r => `
        <tr>
            <td>
                <a href="${escapeHtml(r.url)}" target="_blank" class="repo-link" title="${escapeHtml(r.description)}">
                    ${escapeHtml(r.full_name)}
                </a>
                ${r.description ? `<div style="font-size: 11px; color: var(--text-muted); margin-top: 2px; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(r.description)}</div>` : ''}
            </td>
            <td>
                ${r.language ? `<span class="lang-badge"><span class="lang-dot" style="background: ${LANG_COLORS[r.language] || '#888'}"></span> ${escapeHtml(r.language)}</span>` : '-'}
            </td>
            <td style="font-weight: 600; color: var(--accent-orange);">${formatNumber(r.stars)}</td>
            <td>${formatNumber(r.forks)}</td>
            <td>
                ${(r.topics || []).slice(0, 3).map(tp => `<span class="topic-tag">${escapeHtml(tp)}</span>`).join('')}
                ${(r.topics || []).length > 3 ? `<span class="topic-tag">+${r.topics.length - 3}</span>` : ''}
            </td>
        </tr>
    `).join('');
}

// ============ CHARTS ============
function renderTrendScoreChart(trends) {
    const ctx = document.getElementById('trendScoreChart');
    if (!ctx) return;

    if (charts.trendScore) charts.trendScore.destroy();

    const isDark = currentTheme === 'dark';
    const labels = trends.map(t => t.technology_name);
    const scores = trends.map(t => t.trend_score);
    const colors = trends.map((t, i) => {
        const hue = (i * 30 + 260) % 360;
        return `hsla(${hue}, 70%, ${isDark ? 60 : 50}%, 0.8)`;
    });

    charts.trendScore = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Trend Score',
                data: scores,
                backgroundColor: colors,
                borderColor: colors.map(c => c.replace('0.8', '1')),
                borderWidth: 1,
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: isDark ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255,255,255,0.95)',
                    titleColor: isDark ? '#f1f5f9' : '#0f172a',
                    bodyColor: isDark ? '#94a3b8' : '#475569',
                    titleFont: { weight: '600' },
                    padding: 12,
                    borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.05)' },
                    ticks: { font: { size: 11 } },
                },
                x: {
                    grid: { display: false },
                    ticks: { font: { size: 10 }, maxRotation: 45 },
                }
            },
            animation: { duration: 1000, easing: 'easeOutQuart' },
        }
    });
}

function renderCategoryChart(categories) {
    const ctx = document.getElementById('categoryChart');
    if (!ctx || !categories.length) return;

    if (charts.category) charts.category.destroy();

    const isDark = currentTheme === 'dark';
    const catColors = [
        '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b',
        '#ef4444', '#ec4899', '#3b82f6', '#a855f7',
        '#14b8a6', '#f97316', '#84cc16', '#e879f9', '#fb923c',
    ];

    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories.map(c => c.category),
            datasets: [{
                data: categories.map(c => c.count),
                backgroundColor: catColors.slice(0, categories.length),
                borderColor: isDark ? 'rgba(10, 14, 23, 0.8)' : 'rgba(255, 255, 255, 0.9)',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        padding: 12,
                        usePointStyle: true,
                        pointStyle: 'circle',
                        font: { size: 11 },
                    }
                },
                tooltip: {
                    backgroundColor: isDark ? 'rgba(17, 24, 39, 0.95)' : 'rgba(255,255,255,0.95)',
                    titleColor: isDark ? '#f1f5f9' : '#0f172a',
                    bodyColor: isDark ? '#94a3b8' : '#475569',
                    padding: 12,
                    borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                }
            },
            animation: { animateRotate: true, duration: 1200 },
        }
    });
}

// ============ SEARCH AUTOCOMPLETE ============
async function fetchSuggestions(query) {
    if (query.length < 2) {
        document.getElementById('searchSuggestions').classList.remove('active');
        return;
    }

    const data = await apiFetch(`/search/suggestions?q=${encodeURIComponent(query)}`);
    if (!data || !data.suggestions || data.suggestions.length === 0) {
        document.getElementById('searchSuggestions').classList.remove('active');
        return;
    }

    const container = document.getElementById('searchSuggestions');
    container.innerHTML = data.suggestions.map(s => {
        if (s.type === 'trend') {
            return `<div class="suggestion-item" onclick="selectSuggestion('${escapeHtml(s.name)}', 'trend')">
                <span class="suggestion-type trend">Trend</span>
                <span class="suggestion-name">${escapeHtml(s.name)}</span>
                <span class="suggestion-meta">${s.category} • ${s.score}</span>
            </div>`;
        } else {
            return `<div class="suggestion-item" onclick="selectSuggestion('${escapeHtml(s.name)}', 'repo')">
                <span class="suggestion-type repo">Repo</span>
                <span class="suggestion-name">${escapeHtml(s.name)}</span>
                <span class="suggestion-meta">${s.language || ''} ⭐${formatNumber(s.stars)}</span>
            </div>`;
        }
    }).join('');

    container.classList.add('active');
}

function selectSuggestion(name, type) {
    document.getElementById('searchSuggestions').classList.remove('active');
    document.getElementById('searchInput').value = name;

    if (type === 'trend') {
        showTrendDetail(name);
    } else {
        // Filter by this name
        const filtered = allTrends.filter(t =>
            t.technology_name.toLowerCase().includes(name.toLowerCase()) ||
            (t.description || '').toLowerCase().includes(name.toLowerCase())
        );
        renderTrends(filtered.length ? filtered : getPagedTrends());
    }
}

// ============ INTERACTIONS ============
function filterByCategory(category) {
    currentCategory = category;
    trendPage = 1;
    updateFilterButtons();
    updateCategoryCards();

    if (category === 'all') {
        renderTrends(getPagedTrends());
    } else {
        loadTrends();
    }
    renderTrendsPagination();
}

function updateFilterButtons() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === currentCategory);
    });
}

function updateCategoryCards() {
    document.querySelectorAll('.category-card').forEach(card => {
        const name = card.querySelector('.category-card-name')?.textContent?.trim();
        const isAll = name === t('all');
        card.classList.toggle('active',
            (currentCategory === 'all' && isAll) ||
            name === currentCategory
        );
    });
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        document.getElementById('searchSuggestions').classList.remove('active');
        trendPage = 1;
        renderTrends(getPagedTrends());
        renderTrendsPagination();
        return;
    }

    // Fetch suggestions
    fetchSuggestions(query);

    // Client-side filter
    const filtered = allTrends.filter(tr =>
        tr.technology_name.toLowerCase().includes(query) ||
        (tr.category || '').toLowerCase().includes(query) ||
        (tr.description || '').toLowerCase().includes(query)
    );
    renderTrends(filtered);

    // Clear pagination during search
    document.getElementById('trendsPagination').innerHTML = '';
}

async function showTrendDetail(techName) {
    const modal = document.getElementById('detailModal');
    const body = document.getElementById('modalBody');

    modal.classList.add('active');
    body.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

    const data = await apiFetch(`/trends/detail/${encodeURIComponent(techName)}`);
    if (!data || !data.trend) {
        body.innerHTML = `<p style="color: var(--text-muted);">${t('not_found')}</p>`;
        return;
    }

    const tr = data.trend;
    body.innerHTML = `
        <h2 class="modal-title">${escapeHtml(tr.technology_name)}</h2>
        <div class="modal-category">${escapeHtml(tr.category)} • ${tr.status}</div>
        <div class="modal-metrics">
            <div class="modal-metric">
                <div class="modal-metric-label">Trend Score</div>
                <div class="modal-metric-value" style="color: var(--accent-cyan);">${tr.trend_score}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Growth Rate</div>
                <div class="modal-metric-value" style="color: ${tr.growth_rate > 0 ? 'var(--accent-green)' : 'var(--accent-red)'};">${tr.growth_rate}%</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Repositories</div>
                <div class="modal-metric-value">${tr.repo_count}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Avg Stars</div>
                <div class="modal-metric-value" style="color: var(--accent-orange);">${tr.avg_stars} ⭐</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Mentions</div>
                <div class="modal-metric-value">${tr.mention_count}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">${t('first_detected')}</div>
                <div class="modal-metric-value" style="font-size: 14px;">${formatDate(tr.first_seen)}</div>
            </div>
        </div>
        <p style="color: var(--text-secondary); font-size: 13px;">${escapeHtml(tr.description || '')}</p>
        ${data.timeline && data.timeline.length > 0 ? `
            <div style="margin-top: 20px;">
                <h3 style="font-size: 14px; color: var(--text-secondary); margin-bottom: 12px;">Timeline</h3>
                <canvas id="modalTimelineChart" height="200"></canvas>
            </div>
        ` : ''}
    `;

    // Render timeline chart
    if (data.timeline && data.timeline.length > 0) {
        setTimeout(() => renderTimelineChart(data.timeline), 100);
    }
}

function renderTimelineChart(timeline) {
    const ctx = document.getElementById('modalTimelineChart');
    if (!ctx) return;

    const isDark = currentTheme === 'dark';

    new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeline.map(t => formatDate(t.date)),
            datasets: [{
                label: 'Score',
                data: timeline.map(t => t.score),
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointBackgroundColor: '#8b5cf6',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: isDark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false }, ticks: { font: { size: 10 } } },
            }
        }
    });
}

function closeModal() {
    document.getElementById('detailModal').classList.remove('active');
}

async function triggerCollect() {
    const btn = document.getElementById('btnCollect');
    const searchInput = document.getElementById('searchInput');
    const query = searchInput ? searchInput.value.trim() : '';

    btn.classList.add('loading');
    btn.innerHTML = `<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> ${t('collecting')}`;

    const url = query ? `/collect?query=${encodeURIComponent(query)}` : '/collect';
    const data = await apiFetch(url, { method: 'POST' });

    showToast(data ? t('collect_success') : t('collect_error'), data ? 'success' : 'error');

    setTimeout(() => {
        btn.classList.remove('loading');
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg> <span data-i18n="collect">${t('collect')}</span>`;
    }, 3000);

    setTimeout(loadAllData, 10000);
}

// ============ CHATBOT ============
function openChatbot() {
    document.getElementById('chatbotPanel').classList.add('active');
    document.getElementById('chatbotFab').classList.add('hidden');
    document.getElementById('chatInput').focus();
}

function closeChatbot() {
    document.getElementById('chatbotPanel').classList.remove('active');
    document.getElementById('chatbotFab').classList.remove('hidden');
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    input.value = '';
    const messages = document.getElementById('chatMessages');

    // Append user message
    messages.innerHTML += `
        <div class="chat-msg user">
            <div class="chat-msg-avatar">👤</div>
            <div class="chat-msg-content"><p>${escapeHtml(message)}</p></div>
        </div>`;

    // Typing indicator
    const typingId = 'typing-' + Date.now();
    messages.innerHTML += `
        <div class="chat-msg bot" id="${typingId}">
            <div class="chat-msg-avatar">🤖</div>
            <div class="chat-msg-content">
                <div class="chat-typing"><span></span><span></span><span></span></div>
            </div>
        </div>`;
    messages.scrollTop = messages.scrollHeight;

    // Call API
    try {
        const data = await apiFetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });

        // Remove typing indicator
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        if (data) {
            // Parse markdown
            let htmlContent = '';
            try {
                htmlContent = marked.parse(data.response || '');
            } catch {
                htmlContent = `<p>${escapeHtml(data.response || '')}</p>`;
            }

            let suggestionsHtml = '';
            if (data.suggestions && data.suggestions.length > 0) {
                suggestionsHtml = `<div class="chat-suggestions">
                    ${data.suggestions.map(s => `<button class="chat-suggestion-btn" onclick="document.getElementById('chatInput').value='${escapeHtml(s)}';sendChatMessage();">${escapeHtml(s)}</button>`).join('')}
                </div>`;
            }

            messages.innerHTML += `
                <div class="chat-msg bot">
                    <div class="chat-msg-avatar">🤖</div>
                    <div class="chat-msg-content">${htmlContent}${suggestionsHtml}</div>
                </div>`;
        }
    } catch (err) {
        const typingEl = document.getElementById(typingId);
        if (typingEl) typingEl.remove();

        messages.innerHTML += `
            <div class="chat-msg bot">
                <div class="chat-msg-avatar">🤖</div>
                <div class="chat-msg-content"><p>❌ Error: ${escapeHtml(err.message)}</p></div>
            </div>`;
    }

    messages.scrollTop = messages.scrollHeight;
}

// ============ UTILITIES ============
function formatNumber(num) {
    if (num == null) return '0';
    num = parseFloat(num);
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return Math.round(num * 10) / 10;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        const d = new Date(dateStr);
        return d.toLocaleDateString(currentLang === 'vi' ? 'vi-VN' : 'en-US', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch { return dateStr; }
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function debounce(fn, ms) {
    let timer;
    return (...args) => {
        clearTimeout(timer);
        timer = setTimeout(() => fn(...args), ms);
    };
}

function animateCounter(id, target) {
    const el = document.getElementById(id);
    if (!el) return;

    const current = parseInt(el.textContent) || 0;
    if (current === target) return;

    const duration = 800;
    const steps = 30;
    const stepTime = duration / steps;
    const increment = (target - current) / steps;
    let value = current;
    let step = 0;

    const interval = setInterval(() => {
        step++;
        value += increment;
        el.textContent = Math.round(value);
        if (step >= steps) {
            el.textContent = target;
            clearInterval(interval);
        }
    }, stepTime);
}

function showEmptyState(containerId, icon, title, subtitle) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = `
        <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">${icon}</div>
            <p class="empty-state-text">${title}</p>
            <p class="empty-state-sub">${subtitle}</p>
        </div>
    `;
}

function showToast(message, type = 'info') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(-50%) translateY(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
