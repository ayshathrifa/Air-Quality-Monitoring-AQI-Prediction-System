// ── Tab Switching ────────────────────────────────────────────────────────────
function switchTab(tab) {
    document.getElementById('tab-live').style.display = tab === 'live' ? 'block' : 'none';
    document.getElementById('tab-manual').style.display = tab === 'manual' ? 'block' : 'none';
    document.querySelectorAll('.tab-btn').forEach((btn, i) => {
        btn.classList.toggle('active', (i === 0 && tab === 'live') || (i === 1 && tab === 'manual'));
    });
    resetAQIDisplay();
    document.getElementById('prediction-result').innerHTML = '';
}

let currentLat = null;
let currentLon = null;
let trendChart = null;
let modelChart = null;
let forecastChart = null;
let seasonalChart = null;

const AQI_COLORS = { 1:'#00e400', 2:'#ffff00', 3:'#ff7e00', 4:'#ff0000', 5:'#8f3f97' };
const DAYS = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];

if ('Notification' in window) Notification.requestPermission();

window.addEventListener('DOMContentLoaded', () => {
    const savedLat = localStorage.getItem('currentLat');
    const savedLon = localStorage.getItem('currentLon');
    if (savedLat && savedLon) {
        currentLat = parseFloat(savedLat);
        currentLon = parseFloat(savedLon);
        document.getElementById('lat').value = savedLat;
        document.getElementById('lon').value = savedLon;
        refreshData();
    } else {
        resetAQIDisplay();
    }
    loadStats();
    loadModelComparison();
    loadForecast24h();
    loadSeasonalTrends();
    loadHeatmap();
});

async function refreshData() {
    if (currentLat === null || currentLon === null) {
        document.getElementById('aqi-label').textContent = 'Enter location coordinates';
        return;
    }
    try {
        const res = await fetch(`/api/current?lat=${currentLat}&lon=${currentLon}`);
        const data = await res.json();
        updateAQIDisplay(data);
        updatePollutants(data);
        updateHealthRecommendation(data.health_recommendation);
        updatePollutionSource(data.pollution_source);
        loadStats();
        loadTrendChart();
        showAlertBanner(data.predicted_aqi, data.aqi_info.label);
        checkAQIAlert(data.predicted_aqi, data.aqi_info.label);
    } catch (e) {
        console.error('Error fetching data:', e);
    }
}

function updateAQIDisplay(data) {
    const aqi = data.predicted_aqi || data.aqi;
    document.getElementById('aqi-display').style.backgroundColor = AQI_COLORS[aqi];
    document.getElementById('aqi-value').textContent = aqi;
    document.getElementById('aqi-label').textContent = data.aqi_info.label;
    document.getElementById('aqi-description').textContent = data.aqi_info.description;
    document.getElementById('confidence').textContent = (data.confidence || 0).toFixed(1);
}

function resetAQIDisplay() {
    document.getElementById('aqi-display').style.backgroundColor = '#cccccc';
    document.getElementById('aqi-value').textContent = '--';
    document.getElementById('aqi-label').textContent = 'Enter location or pollutant values above';
    document.getElementById('aqi-description').textContent = '';
    document.getElementById('confidence').textContent = '--';
}

function updatePollutants(data) {
    const maxVals = { pm2_5: 36, pm10: 162, co: 1000, no2: 80, o3: 200, so2: 60 };
    ['pm2_5','pm10','co','no2','o3','so2'].forEach(k => {
        document.getElementById(k).textContent = data[k].toFixed(2);
    });
    updateThresholdBar('pm25-bar', data.pm2_5, maxVals.pm2_5);
    updateThresholdBar('pm10-bar', data.pm10, maxVals.pm10);
    updateThresholdBar('co-bar', data.co, maxVals.co);
    updateThresholdBar('no2-bar', data.no2, maxVals.no2);
    updateThresholdBar('o3-bar', data.o3, maxVals.o3);
    updateThresholdBar('so2-bar', data.so2, maxVals.so2);
}

function updateThresholdBar(id, value, max) {
    document.getElementById(id).style.width = Math.min((value / max) * 100, 100) + '%';
}

function updateHealthRecommendation(rec) {
    const div = document.getElementById('health-rec');
    if (!rec) {
        div.innerHTML = '<p style="color:#999;font-style:italic;">Enter location to see personalized health recommendations</p>';
        return;
    }
    div.innerHTML = `
        <div class="health-rec-header" style="background:${rec.color}; color:${rec.color === '#ffff00' ? '#333' : 'white'}; padding:12px 16px; border-radius:8px; margin-bottom:12px;">
            <span style="font-size:2em;">${rec.icon}</span>
            <span style="font-size:1.3em; font-weight:bold; margin-left:10px;">${rec.level}</span>
        </div>
        <div class="health-rec-grid">
            <div class="rec-item"><strong>General:</strong> ${rec.general}</div>
            <div class="rec-item"><strong>Sensitive Groups:</strong> ${rec.sensitive}</div>
            <div class="rec-item"><strong>Outdoor Activity:</strong> ${rec.outdoor}</div>
            <div class="rec-item"><strong>Mask Advice:</strong> ${rec.mask}</div>
        </div>`;
}

function updatePollutionSource(source) {
    const div = document.getElementById('pollution-source');
    if (!source) {
        div.innerHTML = '<p style="color:#999;font-style:italic;">Enter location coordinates to analyze pollution sources</p>';
        return;
    }
    div.innerHTML = `
        <div class="source-name">${source.source}</div>
        <div class="source-confidence">Confidence: ${source.confidence}%</div>`;
}

function updateLocation() {
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    if (!lat || !lon) { alert('Please enter both latitude and longitude'); return; }
    currentLat = parseFloat(lat);
    currentLon = parseFloat(lon);
    localStorage.setItem('currentLat', lat);
    localStorage.setItem('currentLon', lon);
    document.getElementById('aqi-label').textContent = 'Loading...';
    refreshData();
}

async function predictCustom() {
    const keys = ['pm2_5','pm10','co','no2','o3','so2'];
    const data = {};
    for (const k of keys) {
        const v = document.getElementById('pred_' + k).value;
        if (!v) { alert('Please fill all fields'); return; }
        data[k] = v;
    }
    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await res.json();
        const aqi = result.predicted_aqi;
        const rec = result.health_recommendation;
        // Show result in shared aqi-display
        updateAQIDisplay({ predicted_aqi: aqi, aqi: aqi, aqi_info: result.aqi_info, confidence: result.confidence });
        // Also show health tip in prediction-result
        const resultDiv = document.getElementById('prediction-result');
        resultDiv.innerHTML = rec ? `<div class="rec-item" style="margin-top:8px;">${rec.outdoor} &nbsp;|&nbsp; ${rec.mask}</div>` : '';
        checkAQIAlert(aqi, result.aqi_info.label);
    } catch (e) { console.error(e); }
}

async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const s = await res.json();
        document.getElementById('total-records').textContent = s.total_records || 0;
        document.getElementById('avg-pm2_5').textContent = (s.avg_pm2_5 || 0).toFixed(1);
        document.getElementById('avg-pm10').textContent = (s.avg_pm10 || 0).toFixed(1);
        document.getElementById('avg-aqi').textContent = (s.avg_aqi || 0).toFixed(1);
    } catch (e) { console.error(e); }
}

// ── Model Comparison ──────────────────────────────────────────────────────────

async function loadModelComparison() {
    try {
        const res = await fetch('/api/model-comparison');
        const data = await res.json();
        const names = Object.keys(data);
        const accuracies = names.map(n => data[n].accuracy);
        const cvAccuracies = names.map(n => data[n].cv_accuracy);

        // Table
        const tableDiv = document.getElementById('model-comparison-table');
        tableDiv.innerHTML = `
            <table class="comparison-table">
                <thead><tr><th>Model</th><th>Test Accuracy (%)</th><th>CV Accuracy (%)</th></tr></thead>
                <tbody>${names.map((n, i) => `
                    <tr class="${i === accuracies.indexOf(Math.max(...accuracies)) ? 'best-model' : ''}">
                        <td>${n}</td><td>${accuracies[i]}</td><td>${cvAccuracies[i]}</td>
                    </tr>`).join('')}
                </tbody>
            </table>`;

        // Chart
        const ctx = document.getElementById('modelChart').getContext('2d');
        if (modelChart) modelChart.destroy();
        modelChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: names,
                datasets: [
                    { label: 'Test Accuracy (%)', data: accuracies, backgroundColor: 'rgba(102,126,234,0.8)' },
                    { label: 'CV Accuracy (%)', data: cvAccuracies, backgroundColor: 'rgba(118,75,162,0.6)' }
                ]
            },
            options: {
                responsive: true,
                scales: { y: { min: 50, max: 100, title: { display: true, text: 'Accuracy (%)' } } },
                plugins: { legend: { position: 'top' } }
            }
        });
    } catch (e) { console.error('Model comparison error:', e); }
}

// ── 24-Hour Forecast ──────────────────────────────────────────────────────────

async function loadForecast24h() {
    try {
        const res = await fetch('/api/forecast24h');
        const data = await res.json();
        if (!data.length) return;

        const ctx = document.getElementById('forecastChart').getContext('2d');
        if (forecastChart) forecastChart.destroy();

        const aqiColors = data.map(d => AQI_COLORS[d.aqi]);
        forecastChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.map(d => `+${d.hour}h`),
                datasets: [
                    {
                        label: 'Predicted PM2.5 (µg/m³)',
                        data: data.map(d => d.pm2_5),
                        backgroundColor: aqiColors,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Predicted AQI',
                        data: data.map(d => d.aqi),
                        type: 'line',
                        borderColor: '#333',
                        backgroundColor: 'transparent',
                        pointBackgroundColor: aqiColors,
                        pointRadius: 5,
                        yAxisID: 'y2'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { title: { display: true, text: 'PM2.5 (µg/m³)' } },
                    y2: { position: 'right', min: 0, max: 6, title: { display: true, text: 'AQI Category' }, grid: { drawOnChartArea: false } }
                },
                plugins: { legend: { position: 'top' } }
            }
        });
    } catch (e) { console.error('Forecast error:', e); }
}

// ── Seasonal Trends ───────────────────────────────────────────────────────────

async function loadSeasonalTrends() {
    try {
        const res = await fetch('/api/seasonal-trends');
        const data = await res.json();
        if (!data.length) return;

        const ctx = document.getElementById('seasonalChart').getContext('2d');
        if (seasonalChart) seasonalChart.destroy();

        seasonalChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.month_name),
                datasets: [
                    {
                        label: 'Avg PM2.5 (µg/m³)',
                        data: data.map(d => d.avg_pm25),
                        borderColor: '#ff6384',
                        backgroundColor: 'rgba(255,99,132,0.15)',
                        tension: 0.4, fill: true, yAxisID: 'y'
                    },
                    {
                        label: 'Avg PM10 (µg/m³)',
                        data: data.map(d => d.avg_pm10),
                        borderColor: '#36a2eb',
                        backgroundColor: 'rgba(54,162,235,0.1)',
                        tension: 0.4, fill: true, yAxisID: 'y'
                    },
                    {
                        label: 'Avg AQI Category',
                        data: data.map(d => d.avg_aqi),
                        borderColor: '#8f3f97',
                        backgroundColor: 'transparent',
                        tension: 0.4, borderDash: [5,5], yAxisID: 'y2'
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    y: { title: { display: true, text: 'µg/m³' } },
                    y2: { position: 'right', min: 0, max: 6, title: { display: true, text: 'AQI Category' }, grid: { drawOnChartArea: false } }
                },
                plugins: { legend: { position: 'top' } }
            }
        });
    } catch (e) { console.error('Seasonal trends error:', e); }
}

// ── Heatmap ───────────────────────────────────────────────────────────────────

async function loadHeatmap() {
    try {
        const res = await fetch('/api/heatmap');
        const data = await res.json();
        if (!data.length) return;

        // Build 7×24 matrix
        const matrix = Array.from({ length: 7 }, () => new Array(24).fill(0));
        data.forEach(d => { matrix[d.day][d.hour] = d.pm2_5; });

        const allVals = data.map(d => d.pm2_5);
        const minV = Math.min(...allVals);
        const maxV = Math.max(...allVals);

        const hours = Array.from({ length: 24 }, (_, i) => `${i}:00`);

        let html = '<table class="heatmap-table"><thead><tr><th>Day \\ Hour</th>';
        hours.forEach(h => { html += `<th>${h}</th>`; });
        html += '</tr></thead><tbody>';

        matrix.forEach((row, di) => {
            html += `<tr><td class="heatmap-day">${DAYS[di]}</td>`;
            row.forEach(val => {
                const t = (val - minV) / (maxV - minV || 1);
                const r = Math.round(255 * t);
                const g = Math.round(255 * (1 - t));
                html += `<td class="heatmap-cell" style="background:rgb(${r},${g},50);" title="${val} µg/m³"></td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';
        document.getElementById('heatmap-container').innerHTML = html;
    } catch (e) { console.error('Heatmap error:', e); }
}

// ── Trend Chart ───────────────────────────────────────────────────────────────

async function loadTrendChart() {
    try {
        const res = await fetch('/api/trend');
        const data = await res.json();
        if (!data.pm2_5 || !data.pm2_5.length) return;

        const ctx = document.getElementById('trendChart').getContext('2d');
        if (trendChart) trendChart.destroy();

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timestamps.map((_, i) => `Record ${i + 1}`),
                datasets: [
                    { label: 'PM2.5', data: data.pm2_5, borderColor: '#ff6384', backgroundColor: 'rgba(255,99,132,0.1)', tension: 0.4 },
                    { label: 'PM10', data: data.pm10, borderColor: '#36a2eb', backgroundColor: 'rgba(54,162,235,0.1)', tension: 0.4 }
                ]
            },
            options: {
                responsive: true,
                plugins: { legend: { position: 'top' } },
                scales: { y: { beginAtZero: true, title: { display: true, text: 'µg/m³' } } }
            }
        });
    } catch (e) { console.error('Trend chart error:', e); }
}

// ── Alerts & Notifications ────────────────────────────────────────────────────

function showAlertBanner(aqi, label) {
    const banner = document.getElementById('alert-banner');
    const msg = document.getElementById('alert-message');
    if (aqi >= 3) {
        const texts = {
            3: `⚠️ Air Quality Alert: ${label} — Sensitive groups should limit outdoor activities`,
            4: `🚨 Health Warning: ${label} — Avoid outdoor exercise and close windows`,
            5: `🔴 SEVERE ALERT: ${label} — Stay indoors! Health emergency conditions`
        };
        msg.textContent = texts[aqi] || texts[5];
        banner.style.display = 'flex';
    } else {
        banner.style.display = 'none';
    }
}

function closeAlert() { document.getElementById('alert-banner').style.display = 'none'; }

function checkAQIAlert(aqi, label) {
    if (aqi < 4) return;
    const body = `Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`;
    if (!('Notification' in window)) { alert(`⚠️ AQI ALERT: ${body}`); return; }
    if (Notification.permission === 'granted') {
        new Notification('⚠️ AQI Alert', { body });
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(p => {
            if (p === 'granted') new Notification('⚠️ AQI Alert', { body });
            else alert(`⚠️ AQI ALERT: ${body}`);
        });
    } else {
        alert(`⚠️ AQI ALERT: ${body}`);
    }
}

function testNotification() {
    if (!('Notification' in window)) { alert('❌ Browser does not support notifications'); return; }
    if (Notification.permission === 'granted') {
        new Notification('🔔 Test Notification', { body: 'Notifications are working!' });
        alert('✅ Notification sent!');
    } else if (Notification.permission !== 'denied') {
        Notification.requestPermission().then(p => {
            if (p === 'granted') { new Notification('🔔 Test Notification', { body: 'Notifications enabled!' }); alert('✅ Notification sent!'); }
            else alert('❌ Notification permission denied');
        });
    } else {
        alert('❌ Notifications are blocked. Enable them in browser settings.');
    }
}

function downloadData() { window.location.href = '/api/download'; }
