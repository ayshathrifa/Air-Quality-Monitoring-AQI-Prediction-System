let currentLat = null;
let currentLon = null;
let trendChart = null;

const AQI_COLORS = {
    1: '#00e400',
    2: '#ffff00',
    3: '#ff7e00',
    4: '#ff0000',
    5: '#8f3f97'
};

// Advanced Feature 3: Request notification permission
if ('Notification' in window) {
    Notification.requestPermission();
}

// Load data on page load
window.addEventListener('DOMContentLoaded', () => {
    // Load saved coordinates from localStorage
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
    updateHealthAdvice(null);
    updatePollutionSource(null);
});

async function refreshData() {
    if (currentLat === null || currentLon === null) {
        document.getElementById('aqi-label').textContent = 'Enter location coordinates';
        return;
    }
    
    try {
        console.log(`Fetching data for: ${currentLat}, ${currentLon}`);
        const response = await fetch(`/api/current?lat=${currentLat}&lon=${currentLon}`);
        const data = await response.json();
        
        console.log('Received data:', data);
        
        updateAQIDisplay(data);
        updatePollutants(data);
        updateHealthAdvice(data.health_advice);
        updatePollutionSource(data.pollution_source);
        loadStats();
        loadTrendChart();
        loadForecast();
        
        // Show alert banner if AQI is unhealthy
        showAlertBanner(data.predicted_aqi, data.aqi_info.label);
        
        // Advanced Feature 3: AQI Notification
        checkAQIAlert(data.predicted_aqi, data.aqi_info.label);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function updateAQIDisplay(data) {
    const aqiValue = data.predicted_aqi || data.aqi;
    const aqiInfo = data.aqi_info;
    const confidence = data.confidence || 0;
    
    const aqiDisplay = document.getElementById('aqi-display');
    aqiDisplay.style.backgroundColor = AQI_COLORS[aqiValue];
    
    document.getElementById('aqi-value').textContent = aqiValue;
    document.getElementById('aqi-label').textContent = aqiInfo.label;
    document.getElementById('aqi-description').textContent = aqiInfo.description;
    document.getElementById('confidence').textContent = confidence.toFixed(1);
}

function resetAQIDisplay() {
    const aqiDisplay = document.getElementById('aqi-display');
    aqiDisplay.style.backgroundColor = '#cccccc';
    
    document.getElementById('aqi-value').textContent = '--';
    document.getElementById('aqi-label').textContent = 'Enter location to check air quality';
    document.getElementById('aqi-description').textContent = '';
    document.getElementById('confidence').textContent = '--';
}

function updatePollutants(data) {
    const thresholds = {
        pm2_5: 12, pm10: 54, co: 500, no2: 40, o3: 100, so2: 20
    };
    
    document.getElementById('pm2_5').textContent = data.pm2_5.toFixed(2);
    document.getElementById('pm10').textContent = data.pm10.toFixed(2);
    document.getElementById('co').textContent = data.co.toFixed(2);
    document.getElementById('no2').textContent = data.no2.toFixed(2);
    document.getElementById('o3').textContent = data.o3.toFixed(2);
    document.getElementById('so2').textContent = data.so2.toFixed(2);
    
    // Update threshold bars
    updateThresholdBar('pm25-bar', data.pm2_5, thresholds.pm2_5 * 3);
    updateThresholdBar('pm10-bar', data.pm10, thresholds.pm10 * 3);
    updateThresholdBar('co-bar', data.co, thresholds.co * 2);
    updateThresholdBar('no2-bar', data.no2, thresholds.no2 * 2);
    updateThresholdBar('o3-bar', data.o3, thresholds.o3 * 2);
    updateThresholdBar('so2-bar', data.so2, thresholds.so2 * 3);
}

function updateThresholdBar(id, value, max) {
    const percentage = Math.min((value / max) * 100, 100);
    document.getElementById(id).style.width = percentage + '%';
}

function updateLocation() {
    const lat = document.getElementById('lat').value;
    const lon = document.getElementById('lon').value;
    
    if (lat && lon) {
        currentLat = parseFloat(lat);
        currentLon = parseFloat(lon);
        
        // Save to localStorage
        localStorage.setItem('currentLat', lat);
        localStorage.setItem('currentLon', lon);
        
        console.log(`Location updated to: ${currentLat}, ${currentLon}`);
        
        // Show loading message
        document.getElementById('aqi-label').textContent = 'Loading...';
        
        // Fetch new data
        refreshData();
    } else {
        alert('Please enter both latitude and longitude');
    }
}

async function predictCustom() {
    const data = {
        pm2_5: document.getElementById('pred_pm2_5').value,
        pm10: document.getElementById('pred_pm10').value,
        co: document.getElementById('pred_co').value,
        no2: document.getElementById('pred_no2').value,
        o3: document.getElementById('pred_o3').value,
        so2: document.getElementById('pred_so2').value
    };
    
    // Validate inputs
    for (let key in data) {
        if (!data[key]) {
            alert('Please fill all fields');
            return;
        }
    }
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        displayPredictionResult(result);
    } catch (error) {
        console.error('Error predicting:', error);
    }
}

function displayPredictionResult(result) {
    const resultDiv = document.getElementById('prediction-result');
    const aqiValue = result.predicted_aqi;
    const aqiInfo = result.aqi_info;
    const confidence = result.confidence;
    
    resultDiv.style.backgroundColor = AQI_COLORS[aqiValue];
    resultDiv.style.color = 'white';
    resultDiv.innerHTML = `
        <div style="font-size: 2em; font-weight: bold;">${aqiValue}</div>
        <div style="font-size: 1.3em; margin-top: 10px;">${aqiInfo.label}</div>
        <div style="margin-top: 10px;">${aqiInfo.description}</div>
        <div style="margin-top: 10px;">Confidence: ${confidence.toFixed(1)}%</div>
    `;
    
    // Trigger notification for unhealthy AQI
    checkAQIAlert(aqiValue, aqiInfo.label);
}

async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        
        document.getElementById('total-records').textContent = stats.total_records || 0;
        document.getElementById('avg-pm2_5').textContent = (stats.avg_pm2_5 || 0).toFixed(2);
        document.getElementById('avg-pm10').textContent = (stats.avg_pm10 || 0).toFixed(2);
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Advanced Feature 1: Update Health Advice
function updateHealthAdvice(advice) {
    const adviceDiv = document.getElementById('health-advice');
    if (advice && advice.length > 0) {
        adviceDiv.innerHTML = advice.map(item => `<p>• ${item}</p>`).join('');
    } else {
        adviceDiv.innerHTML = '<p style="color: #999; font-style: italic;">Enter location coordinates to see health recommendations</p>';
    }
}

// Advanced Feature 4: Update Pollution Source
function updatePollutionSource(source) {
    const sourceDiv = document.getElementById('pollution-source');
    if (source) {
        sourceDiv.innerHTML = `
            <div class="source-name">${source.source}</div>
            <div class="source-confidence">Confidence: ${source.confidence}%</div>
        `;
    } else {
        sourceDiv.innerHTML = '<p style="color: #999; font-style: italic;">Enter location coordinates to analyze pollution sources</p>';
    }
}

// Advanced Feature 3: AQI Alert Notification
function checkAQIAlert(aqi, label) {
    console.log('checkAQIAlert called:', aqi, label);
    
    if (aqi >= 4) {
        if (!('Notification' in window)) {
            console.log('Browser does not support notifications');
            alert(`⚠️ AQI ALERT: Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`);
            return;
        }
        
        if (Notification.permission === 'granted') {
            console.log('Showing notification...');
            new Notification('⚠️ AQI Alert', {
                body: `Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`
            });
        } else if (Notification.permission === 'default') {
            console.log('Requesting notification permission...');
            Notification.requestPermission().then(permission => {
                if (permission === 'granted') {
                    new Notification('⚠️ AQI Alert', {
                        body: `Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`
                    });
                } else {
                    alert(`⚠️ AQI ALERT: Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`);
                }
            });
        } else {
            console.log('Notification permission denied, showing alert');
            alert(`⚠️ AQI ALERT: Air Quality is ${label}! AQI: ${aqi}\nAvoid outdoor activities.`);
        }
    }
}

// Test notification function
function testNotification() {
    console.log('Test notification button clicked');
    
    if (!('Notification' in window)) {
        alert('❌ This browser does not support notifications');
        console.error('Notifications not supported');
        return;
    }
    
    console.log('Notification permission:', Notification.permission);
    
    if (Notification.permission === 'granted') {
        console.log('Sending test notification...');
        new Notification('🔔 Test Notification', {
            body: 'Notifications are working! You will see alerts when AQI becomes unhealthy.',
        });
        alert('✅ Notification sent! Check top-right corner of your screen.');
    } else if (Notification.permission !== 'denied') {
        console.log('Requesting notification permission...');
        Notification.requestPermission().then(permission => {
            console.log('Permission result:', permission);
            if (permission === 'granted') {
                new Notification('🔔 Test Notification', {
                    body: 'Notifications enabled! You will see alerts when AQI becomes unhealthy.',
                });
                alert('✅ Notification sent! Check top-right corner of your screen.');
            } else {
                alert('❌ Notification permission denied');
            }
        });
    } else {
        alert('❌ Notifications are blocked. Please enable them in browser settings:\n\n1. Click the lock icon in address bar\n2. Find "Notifications"\n3. Change to "Allow"\n4. Refresh page');
        console.error('Notifications blocked by user');
    }
}

// Advanced Feature 2: Pollution Trend Chart
async function loadTrendChart() {
    try {
        const response = await fetch('/api/trend');
        const data = await response.json();
        
        if (data.pm2_5.length === 0) return;
        
        const ctx = document.getElementById('trendChart').getContext('2d');
        
        if (trendChart) {
            trendChart.destroy();
        }
        
        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.timestamps.map((t, i) => `Record ${i + 1}`),
                datasets: [
                    {
                        label: 'PM2.5',
                        data: data.pm2_5,
                        borderColor: '#ff6384',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'PM10',
                        data: data.pm10,
                        borderColor: '#36a2eb',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Pollutant Levels Over Time'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'µg/m³'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading trend chart:', error);
    }
}

// Alert Banner
function showAlertBanner(aqi, label) {
    const banner = document.getElementById('alert-banner');
    const message = document.getElementById('alert-message');
    
    if (aqi >= 3) {
        let alertText = '';
        if (aqi === 3) {
            alertText = `⚠️ Air Quality Alert: ${label} - Sensitive groups should limit outdoor activities`;
        } else if (aqi === 4) {
            alertText = `🚨 Health Warning: ${label} - Avoid outdoor exercise and close windows`;
        } else {
            alertText = `🔴 SEVERE ALERT: ${label} - Stay indoors! Health emergency conditions`;
        }
        message.textContent = alertText;
        banner.style.display = 'flex';
    } else {
        banner.style.display = 'none';
    }
}

function closeAlert() {
    document.getElementById('alert-banner').style.display = 'none';
}

// AQI Forecast
async function loadForecast() {
    try {
        const response = await fetch('/api/forecast');
        const forecast = await response.json();
        
        const panel = document.getElementById('forecast-panel');
        
        if (forecast.length > 0) {
            panel.innerHTML = forecast.map(item => `
                <div class="forecast-item">
                    <div class="forecast-hour">+${item.hour}h</div>
                    <div class="forecast-aqi">${item.aqi}</div>
                </div>
            `).join('');
        } else {
            panel.innerHTML = '<p style="color: #999; font-style: italic;">Enter location to see AQI forecast</p>';
        }
    } catch (error) {
        console.error('Error loading forecast:', error);
    }
}

// Download Data
function downloadData() {
    window.location.href = '/api/download';
}
