# SCREENSHOT GUIDE FOR DOCUMENTATION

## Screenshots to Take for Your Submission

### 1. Main Dashboard View
**What to capture:** Full dashboard showing AQI display
**How to take:**
- Start the application
- Open http://localhost:5000
- Wait for data to load
- Take full-page screenshot
**Filename:** 01_main_dashboard.png

### 2. AQI Display - Good Quality
**What to capture:** AQI showing "Good" (green)
**How to take:**
- Use custom prediction with low values
- PM2.5: 10, PM10: 20, CO: 200, NO2: 10, O3: 30, SO2: 5
- Screenshot the AQI display section
**Filename:** 02_aqi_good.png

### 3. AQI Display - Unhealthy
**What to capture:** AQI showing "Unhealthy" (red)
**How to take:**
- Use custom prediction with high values
- PM2.5: 100, PM10: 150, CO: 1500, NO2: 80, O3: 120, SO2: 40
- Screenshot the AQI display section
**Filename:** 03_aqi_unhealthy.png

### 4. Pollutant Levels Section
**What to capture:** All 6 pollutant readings
**How to take:**
- Scroll to pollutants section
- Capture all 6 boxes (PM2.5, PM10, CO, NO2, O3, SO2)
**Filename:** 04_pollutants.png

### 5. Location Input
**What to capture:** Location change feature
**How to take:**
- Show the latitude/longitude input fields
- Capture before and after changing location
**Filename:** 05_location_input.png

### 6. Custom Prediction Form
**What to capture:** Custom prediction feature
**How to take:**
- Fill in all 6 input fields
- Show the prediction result
**Filename:** 06_custom_prediction.png

### 7. Statistics Section
**What to capture:** Statistics dashboard
**How to take:**
- Scroll to statistics section
- Show total records and averages
**Filename:** 07_statistics.png

### 8. Code - app.py
**What to capture:** Main application code
**How to take:**
- Open app.py in VS Code or text editor
- Show the Flask routes and functions
**Filename:** 08_code_app.png

### 9. Code - model_trainer.py
**What to capture:** ML model training code
**How to take:**
- Open model_trainer.py
- Show the Random Forest implementation
**Filename:** 09_code_model.png

### 10. Terminal - Model Training
**What to capture:** Model training output
**How to take:**
- Run: python model_trainer.py
- Capture the accuracy and classification report
**Filename:** 10_model_training.png

### 11. Terminal - Application Running
**What to capture:** Flask server running
**How to take:**
- Run: python app.py
- Show the server startup messages
**Filename:** 11_app_running.png

### 12. Project Structure
**What to capture:** File and folder organization
**How to take:**
- Open project folder in File Explorer
- Show all files and folders
**Filename:** 12_project_structure.png

### 13. Data File
**What to capture:** CSV data file
**How to take:**
- Open data/air_quality_data.csv in Excel or text editor
- Show the collected data
**Filename:** 13_data_file.png

### 14. Mobile View (Optional)
**What to capture:** Responsive design
**How to take:**
- Open browser developer tools (F12)
- Toggle device toolbar
- Select mobile device
- Take screenshot
**Filename:** 14_mobile_view.png

### 15. API Response (Optional)
**What to capture:** API endpoint response
**How to take:**
- Open http://localhost:5000/api/current in browser
- Show the JSON response
**Filename:** 15_api_response.png

## Tips for Good Screenshots

1. **Resolution:** Use at least 1920x1080 resolution
2. **Clean:** Close unnecessary tabs and windows
3. **Focus:** Highlight important sections
4. **Lighting:** Use light theme for better visibility
5. **Annotations:** Add arrows or text if needed

## Tools for Screenshots

Windows:
- Snipping Tool (Win + Shift + S)
- Print Screen (PrtScn)
- Snip & Sketch

Third-party:
- Greenshot (free)
- ShareX (free)
- Lightshot (free)

## Creating a Screenshot Document

### Option 1: Word Document
1. Create new Word document
2. Insert screenshots with captions
3. Add brief descriptions
4. Save as PDF

### Option 2: PowerPoint
1. Create presentation
2. One screenshot per slide
3. Add titles and descriptions
4. Export as PDF

### Option 3: Markdown Document
```markdown
# Project Screenshots

## 1. Main Dashboard
![Main Dashboard](screenshots/01_main_dashboard.png)
Description: The main dashboard showing real-time AQI...

## 2. AQI Display
![AQI Display](screenshots/02_aqi_good.png)
Description: AQI indicator showing good air quality...
```

## Screenshot Checklist

Before submission, ensure you have:
□ Main dashboard view
□ Different AQI levels (at least 2)
□ Pollutant levels display
□ Custom prediction feature
□ Statistics section
□ Code snippets (2-3 files)
□ Terminal outputs (model training, app running)
□ Project structure
□ Data file view

## Organizing Screenshots

Create a folder structure:
```
AirQualityMonitoring/
├── screenshots/
│   ├── 01_main_dashboard.png
│   ├── 02_aqi_good.png
│   ├── 03_aqi_unhealthy.png
│   ├── ...
│   └── 15_api_response.png
└── documentation/
    └── screenshots.pdf
```

## Creating a Video Demo (Optional)

If you want to create a video demonstration:

1. **Tools:**
   - OBS Studio (free)
   - Windows Game Bar (Win + G)
   - Loom (online)

2. **Script:**
   - Introduction (30 sec)
   - Show dashboard (1 min)
   - Demonstrate features (2 min)
   - Show code (1 min)
   - Conclusion (30 sec)

3. **Duration:** 3-5 minutes

4. **Format:** MP4, 1080p

## Final Documentation Package

Your submission should include:
1. Project folder (all code)
2. Screenshots folder
3. Screenshots document (PDF)
4. README.md
5. PROJECT_SUMMARY.txt
6. Optional: Video demo

Good luck with your documentation!
