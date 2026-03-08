import requests
import time

print("=" * 70)
print("TESTING ALL 4 ADVANCED FEATURES")
print("=" * 70)

base_url = "http://localhost:5000"

# Test 1: Get current data (includes health advice and pollution source)
print("\n1. Testing Health Advisory & Pollution Source...")
response = requests.get(f"{base_url}/api/current?lat=12.9716&lon=77.5946")
data = response.json()

print(f"   AQI: {data['predicted_aqi']}")
print(f"   Health Advice: {data.get('health_advice', 'NOT FOUND')}")
print(f"   Pollution Source: {data.get('pollution_source', 'NOT FOUND')}")

# Test 2: Get statistics
print("\n2. Testing Statistics...")
response = requests.get(f"{base_url}/api/stats")
stats = response.json()
print(f"   Total Records: {stats.get('total_records', 0)}")
print(f"   Avg PM2.5: {stats.get('avg_pm2_5', 0)}")

# Test 3: Get trend data
print("\n3. Testing Trend Analysis...")
response = requests.get(f"{base_url}/api/trend")
trend = response.json()
print(f"   PM2.5 data points: {len(trend.get('pm2_5', []))}")
print(f"   PM10 data points: {len(trend.get('pm10', []))}")

# Collect more data for trend
print("\n4. Collecting data for trend chart...")
for i in range(5):
    requests.get(f"{base_url}/api/current?lat=12.9716&lon=77.5946")
    print(f"   Collected record {i+1}/5")
    time.sleep(1)

# Check trend again
response = requests.get(f"{base_url}/api/trend")
trend = response.json()
print(f"\n   Updated PM2.5 data points: {len(trend.get('pm2_5', []))}")

# Check stats again
response = requests.get(f"{base_url}/api/stats")
stats = response.json()
print(f"\n   Updated Total Records: {stats.get('total_records', 0)}")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print("\nNow refresh your browser to see all features working!")
print("Note: Notifications require browser permission - click 'Allow' when asked")
