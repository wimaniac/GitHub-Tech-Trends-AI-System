/**
 * GitHub Tech Trends AI — Dashboard JavaScript
 * Quản lý giao diện, fetch API, charts và tương tác.
 */

// ============ CONFIG ============
const API_BASE = '/api';
const REFRESH_INTERVAL = 60000; // 60s

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

// Chart.js global config
Chart.defaults.color = '#94a3b8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.05)';
Chart.defaults.font.family = "'Inter', sans-serif";

// ============ STATE ============
let currentCategory = 'all';
let currentSort = 'trend_score';
let allTrends = [];
let charts = {};

// ============ INIT ============
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    setupEventListeners();
    setInterval(loadAllData, REFRESH_INTERVAL);
});

function setupEventListeners() {
    // Search
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', debounce(handleSearch, 300));

    // Collect button
    document.getElementById('btnCollect').addEventListener('click', triggerCollect);

    // Sort select
    document.getElementById('sortSelect').addEventListener('change', (e) => {
        currentSort = e.target.value;
        loadTrends();
    });

    // Category filter "all" button
    document.querySelector('.filter-btn[data-category="all"]').addEventListener('click', () => {
        currentCategory = 'all';
        updateFilterButtons();
        renderTrends(allTrends);
    });

    // Modal close
    document.getElementById('modalClose').addEventListener('click', closeModal);
    document.getElementById('detailModal').addEventListener('click', (e) => {
        if (e.target === e.currentTarget) closeModal();
    });

    // Keyboard
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
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
    const params = new URLSearchParams({ limit: '50', sort_by: currentSort });
    if (currentCategory !== 'all') params.set('category', currentCategory);

    const data = await apiFetch(`/trends?${params}`);
    if (!data) {
        showEmptyState('trendsGrid', '📊', 'Chưa có dữ liệu xu hướng', 'Nhấn "Thu thập" để bắt đầu crawl dữ liệu từ GitHub');
        return;
    }

    allTrends = data.trends || [];
    renderTrends(allTrends);
    renderTrendScoreChart(allTrends.slice(0, 12));
}

async function loadCategories() {
    const data = await apiFetch('/categories');
    if (!data || !data.categories) return;

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
        showEmptyState('predictionsGrid', '🔮', 'Chưa có dự đoán', 'Dự đoán sẽ xuất hiện sau khi phân tích dữ liệu');
        return;
    }
    renderPredictions(data.predictions);
}

async function loadRepos() {
    const data = await apiFetch('/repos?limit=30');
    if (!data || !data.repos || data.repos.length === 0) {
        document.getElementById('repoTableBody').innerHTML =
            '<tr><td colspan="5" class="empty-state"><div class="empty-state-icon">📁</div><p>Chưa có repositories</p></td></tr>';
        return;
    }
    renderRepoTable(data.repos);
}

// ============ RENDERING ============
function renderTrends(trends) {
    const grid = document.getElementById('trendsGrid');

    if (!trends || trends.length === 0) {
        showEmptyState('trendsGrid', '📊', 'Chưa có dữ liệu xu hướng', 'Nhấn "Thu thập" để bắt đầu crawl dữ liệu từ GitHub');
        return;
    }

    grid.innerHTML = trends.map((t, i) => `
        <div class="trend-card" onclick="showTrendDetail('${t.technology_name}')" style="animation-delay: ${i * 0.05}s">
            <div class="trend-card-header">
                <span class="trend-name">${escapeHtml(t.technology_name)}</span>
                <span class="trend-status status-${t.status}">${t.status}</span>
            </div>
            <div class="trend-category">${escapeHtml(t.category)}</div>
            <div class="trend-description">${escapeHtml(t.description || '')}</div>
            <div class="trend-metrics">
                <div class="metric">
                    <span class="metric-value">${formatNumber(t.trend_score)}</span>
                    <span class="metric-label">Score</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${formatNumber(t.repo_count)}</span>
                    <span class="metric-label">Repos</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${formatNumber(t.avg_stars)}</span>
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
                    <span class="prediction-score-label">Hiện tại</span>
                    <span class="prediction-score-value score-current">${formatNumber(p.current_score)}</span>
                </div>
                <div class="prediction-score">
                    <span class="prediction-score-label">Dự đoán</span>
                    <span class="prediction-score-value score-predicted">${formatNumber(p.predicted_score)}</span>
                </div>
                <div class="prediction-score">
                    <span class="prediction-score-label">Thay đổi</span>
                    <span class="prediction-score-value" style="color: ${change >= 0 ? '#22c55e' : '#ef4444'}">
                        ${change >= 0 ? '+' : ''}${changePercent}%
                    </span>
                </div>
            </div>
            <div class="prediction-bar">
                <div class="prediction-bar-fill" style="width: ${barWidth}%"></div>
            </div>
            <div style="font-size: 10px; color: var(--text-muted); margin-top: 4px;">
                Độ tin cậy: ${(p.confidence * 100).toFixed(0)}% • ${p.method || ''}
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
                ${(r.topics || []).slice(0, 3).map(t => `<span class="topic-tag">${escapeHtml(t)}</span>`).join('')}
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

    const labels = trends.map(t => t.technology_name);
    const scores = trends.map(t => t.trend_score);
    const colors = trends.map((t, i) => {
        const hue = (i * 30 + 260) % 360;
        return `hsla(${hue}, 70%, 60%, 0.8)`;
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
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    titleFont: { weight: '600' },
                    padding: 12,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.03)' },
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

    const catColors = [
        '#8b5cf6', '#06b6d4', '#22c55e', '#f59e0b',
        '#ef4444', '#ec4899', '#3b82f6', '#a855f7',
        '#14b8a6', '#f97316',
    ];

    charts.category = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: categories.map(c => c.category),
            datasets: [{
                data: categories.map(c => c.count),
                backgroundColor: catColors.slice(0, categories.length),
                borderColor: 'rgba(10, 14, 23, 0.8)',
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
                    backgroundColor: 'rgba(17, 24, 39, 0.95)',
                    padding: 12,
                    borderColor: 'rgba(255,255,255,0.1)',
                    borderWidth: 1,
                    cornerRadius: 8,
                }
            },
            animation: { animateRotate: true, duration: 1200 },
        }
    });
}

// ============ INTERACTIONS ============
function filterByCategory(category) {
    currentCategory = category;
    updateFilterButtons();
    loadTrends();
}

function updateFilterButtons() {
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.category === currentCategory);
    });
}

function handleSearch(e) {
    const query = e.target.value.toLowerCase().trim();
    if (!query) {
        renderTrends(allTrends);
        return;
    }
    const filtered = allTrends.filter(t =>
        t.technology_name.toLowerCase().includes(query) ||
        (t.category || '').toLowerCase().includes(query) ||
        (t.description || '').toLowerCase().includes(query)
    );
    renderTrends(filtered);
}

async function showTrendDetail(techName) {
    const modal = document.getElementById('detailModal');
    const body = document.getElementById('modalBody');

    modal.classList.add('active');
    body.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

    const data = await apiFetch(`/trends/detail/${encodeURIComponent(techName)}`);
    if (!data || !data.trend) {
        body.innerHTML = '<p style="color: var(--text-muted);">Không tìm thấy thông tin.</p>';
        return;
    }

    const t = data.trend;
    body.innerHTML = `
        <h2 class="modal-title">${escapeHtml(t.technology_name)}</h2>
        <div class="modal-category">${escapeHtml(t.category)} • ${t.status}</div>
        <div class="modal-metrics">
            <div class="modal-metric">
                <div class="modal-metric-label">Trend Score</div>
                <div class="modal-metric-value" style="color: var(--accent-cyan);">${t.trend_score}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Growth Rate</div>
                <div class="modal-metric-value" style="color: ${t.growth_rate > 0 ? 'var(--accent-green)' : 'var(--accent-red)'};">${t.growth_rate}%</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Repositories</div>
                <div class="modal-metric-value">${t.repo_count}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Avg Stars</div>
                <div class="modal-metric-value" style="color: var(--accent-orange);">${t.avg_stars} ⭐</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Mentions</div>
                <div class="modal-metric-value">${t.mention_count}</div>
            </div>
            <div class="modal-metric">
                <div class="modal-metric-label">Lần đầu phát hiện</div>
                <div class="modal-metric-value" style="font-size: 14px;">${formatDate(t.first_seen)}</div>
            </div>
        </div>
        <p style="color: var(--text-secondary); font-size: 13px;">${escapeHtml(t.description || '')}</p>
        ${data.timeline && data.timeline.length > 0 ? `
            <div style="margin-top: 20px;">
                <h3 style="font-size: 14px; color: var(--text-secondary); margin-bottom: 12px;">Timeline</h3>
                <canvas id="modalTimelineChart" height="200"></canvas>
            </div>
        ` : ''}
    `;

    // Render timeline chart nếu có
    if (data.timeline && data.timeline.length > 0) {
        setTimeout(() => renderTimelineChart(data.timeline), 100);
    }
}

function renderTimelineChart(timeline) {
    const ctx = document.getElementById('modalTimelineChart');
    if (!ctx) return;

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
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.03)' } },
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
    btn.classList.add('loading');
    btn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Đang thu thập...';

    const data = await apiFetch('/collect', { method: 'POST' });

    showToast(data ? '✅ Đã bắt đầu thu thập dữ liệu từ GitHub!' : '❌ Lỗi khi thu thập!',
              data ? 'success' : 'error');

    // Reset button sau 3s
    setTimeout(() => {
        btn.classList.remove('loading');
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v5"/></svg> Thu thập`;
    }, 3000);

    // Reload data sau 10s
    setTimeout(loadAllData, 10000);
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
        return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
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
        toast.style.transform = 'translateY(20px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}
