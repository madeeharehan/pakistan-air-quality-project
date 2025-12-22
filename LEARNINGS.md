Week 1: Lessons Learned & Project Progress
1. Project Overview & Methodology
   Goal: Establish a reliable data pipeline to fetch and categorize $PM_{2.5}$ air quality data for five major cities in Pakistan (Lahore, Karachi, Islamabad, Peshawar, Faisalabad).
   Approach: * Used the OpenAQ Python SDK (v3) to programmatically access historical sensor data.
               Developed a modular script structure (Download → Analyze → Visualize) to ensure code maintainability.
               Applied the US EPA AQI standards to convert raw concentration values into human-readable health categories.
   2. Technical Challenges & Solutions
      Challenge
      SDK Version Mismatch: Tried using location_id in measurements.list(), which is deprecated in v3.	
      Solution
      Switched to querying by sensors_id. Learned that in the new API, locations are containers for specific hardware sensors.
      Challenge
      API Parameter Errors: Encountered unexpected keyword argument 'date_from'.
      Solution
      Discovered the parameter was renamed to datetime_from in the latest library update.
      Challenge
      Data Volume Limits: API requests were capped at 1,000 records, but 90 days of hourly data require ~2,160 records per city.
      Solution
      Implemented pagination logic using a while loop to fetch all pages of data until the full history was retrieved.
