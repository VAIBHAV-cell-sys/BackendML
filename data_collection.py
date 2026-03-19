"""
Historical Data Collection Guide
How to collect and format real crop failure/success data for training
"""

import pandas as pd
import json
from datetime import datetime, timedelta
import random

class HistoricalDataCollector:
    """
    Utility to collect and format historical crop data
    """
    
    def __init__(self):
        self.data_template = {
            'crop': '',
            'temperature': 0.0,
            'humidity': 0.0,
            'rainfall': 0.0,
            'wind_speed': 0.0,
            'pressure': 0.0,
            'cloud_cover': 0.0,
            'soil_pH': 0.0,
            'nitrogen': 0,  # 0=Low, 1=Medium, 2=High
            'phosphorus': 0,
            'potassium': 0,
            'organic_matter': 0.0,
            'season': 0,  # 0=Kharif, 1=Rabi, 2=Zaid
            'month': 0,
            'success': 0  # 0=Failure, 1=Success
        }
    
    def create_data_template_csv(self, filename='data_collection_template.csv'):
        """
        Create a CSV template for manual data entry
        """
        # Create sample rows
        sample_data = [
            {
                'date': '2023-06-15',
                'location': 'Pune',
                'crop': 'Rice',
                'temperature': 28.5,
                'humidity': 75.0,
                'rainfall': 8.5,
                'wind_speed': 5.5,
                'pressure': 1012.0,
                'cloud_cover': 60.0,
                'soil_pH': 6.5,
                'nitrogen': 'High',
                'phosphorus': 'High',
                'potassium': 'Medium',
                'organic_matter': 2.3,
                'season': 'Kharif',
                'month': 6,
                'yield_quintals_per_acre': 25.0,
                'success': 'Yes',
                'notes': 'Good monsoon, timely sowing'
            },
            {
                'date': '2023-07-10',
                'location': 'Jaipur',
                'crop': 'Bajra',
                'temperature': 32.0,
                'humidity': 40.0,
                'rainfall': 0.5,
                'wind_speed': 8.0,
                'pressure': 1010.0,
                'cloud_cover': 20.0,
                'soil_pH': 8.1,
                'nitrogen': 'Low',
                'phosphorus': 'Medium',
                'potassium': 'Medium',
                'organic_matter': 0.8,
                'season': 'Kharif',
                'month': 7,
                'yield_quintals_per_acre': 18.0,
                'success': 'Yes',
                'notes': 'Drought-resistant crop performed well'
            }
        ]
        
        df = pd.DataFrame(sample_data)
        df.to_csv(filename, index=False)
        
        print(f"✅ Template created: {filename}")
        print(f"📋 Columns: {list(df.columns)}")
        print(f"\n📝 Instructions:")
        print("   1. Fill in historical crop data row by row")
        print("   2. Use actual weather data from weather APIs or records")
        print("   3. Mark 'success' as 'Yes' if crop yielded well, 'No' if failed")
        print("   4. Include at least 500-1000 records for good model accuracy")
        print("   5. Balance the data - include both successes and failures")
        
        return df
    
    def format_collected_data(self, input_csv, output_csv='formatted_historical_data.csv'):
        """
        Convert collected data to ML model format
        
        Args:
            input_csv (str): Path to collected data CSV
            output_csv (str): Path to save formatted data
        """
        print(f"📂 Reading data from {input_csv}...")
        df = pd.read_csv(input_csv)
        
        print(f"📊 Loaded {len(df)} records")
        
        # Convert nutrient levels to numeric
        nutrient_map = {'Low': 0, 'Medium': 1, 'High': 2}
        df['nitrogen'] = df['nitrogen'].map(nutrient_map)
        df['phosphorus'] = df['phosphorus'].map(nutrient_map)
        df['potassium'] = df['potassium'].map(nutrient_map)
        
        # Convert season to numeric
        season_map = {'Kharif': 0, 'Rabi': 1, 'Zaid': 2}
        df['season'] = df['season'].map(season_map)
        
        # Convert success to binary
        df['success'] = df['success'].map({'Yes': 1, 'No': 0})
        
        # Select required columns
        required_columns = [
            'crop', 'temperature', 'humidity', 'rainfall', 'wind_speed',
            'pressure', 'cloud_cover', 'soil_pH', 'nitrogen', 'phosphorus',
            'potassium', 'organic_matter', 'season', 'month', 'success'
        ]
        
        formatted_df = df[required_columns].copy()
        
        # Save formatted data
        formatted_df.to_csv(output_csv, index=False)
        
        print(f"✅ Formatted data saved to {output_csv}")
        print(f"📈 Statistics:")
        print(f"   Total records: {len(formatted_df)}")
        print(f"   Successful crops: {formatted_df['success'].sum()} ({formatted_df['success'].mean()*100:.1f}%)")
        print(f"   Failed crops: {(1-formatted_df['success']).sum()} ({(1-formatted_df['success'].mean())*100:.1f}%)")
        print(f"   Unique crops: {formatted_df['crop'].nunique()}")
        print(f"   Crops: {list(formatted_df['crop'].unique())}")
        
        return formatted_df
    
    def fetch_historical_weather(self, location, start_date, end_date):
        """
        Placeholder for historical weather data fetching
        
        In production, use:
        - OpenWeather History API (paid)
        - Visual Crossing Weather API
        - Meteostat Python library
        - Government weather records
        """
        print("⚠️  Historical weather fetching not implemented")
        print("🔗 Recommended APIs:")
        print("   - Visual Crossing: https://www.visualcrossing.com/")
        print("   - Meteostat: https://meteostat.net/")
        print("   - OpenWeather History: https://openweathermap.org/history")
        
        # Example code structure:
        """
        import requests
        
        # Example: Visual Crossing API
        api_key = "YOUR_API_KEY"
        url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{start_date}/{end_date}"
        
        params = {
            'unitGroup': 'metric',
            'key': api_key,
            'include': 'days'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Extract daily weather data
        for day in data['days']:
            weather_record = {
                'date': day['datetime'],
                'temperature': day['temp'],
                'humidity': day['humidity'],
                'rainfall': day.get('precip', 0),
                'wind_speed': day['windspeed'],
                'pressure': day['pressure']
            }
        """
    
    def generate_report(self, data_csv):
        """
        Generate data quality report
        """
        df = pd.read_csv(data_csv)
        
        print("\n" + "="*70)
        print("  DATA QUALITY REPORT")
        print("="*70)
        
        print(f"\n📊 Dataset Overview:")
        print(f"   Total Records: {len(df)}")
        print(f"   Date Range: {df['month'].min()} to {df['month'].max()}")
        print(f"   Locations: {df['location'].nunique() if 'location' in df.columns else 'N/A'}")
        
        print(f"\n🌾 Crop Distribution:")
        crop_counts = df['crop'].value_counts()
        for crop, count in crop_counts.head(10).items():
            print(f"   {crop}: {count} records ({count/len(df)*100:.1f}%)")
        
        print(f"\n✓ Success Rate:")
        success_rate = df['success'].mean() * 100
        print(f"   Success: {df['success'].sum()} ({success_rate:.1f}%)")
        print(f"   Failure: {(1-df['success']).sum()} ({100-success_rate:.1f}%)")
        
        print(f"\n🔍 Data Quality Checks:")
        missing = df.isnull().sum()
        if missing.any():
            print("   ⚠️  Missing values found:")
            for col, count in missing[missing > 0].items():
                print(f"      {col}: {count} missing")
        else:
            print("   ✅ No missing values")
        
        print(f"\n📈 Feature Statistics:")
        print(f"   Temperature: {df['temperature'].min():.1f}°C to {df['temperature'].max():.1f}°C")
        print(f"   Rainfall: {df['rainfall'].min():.1f}mm to {df['rainfall'].max():.1f}mm")
        print(f"   Soil pH: {df['soil_pH'].min():.1f} to {df['soil_pH'].max():.1f}")
        
        print("\n" + "="*70)


# ==========================================================================
# INTEGRATION WITH REAL DATA SOURCES
# ==========================================================================

def integrate_government_data():
    """
    Example: Integrate with government agricultural databases
    """
    print("🏛️  Government Data Sources (India):")
    print("   - AGMARKNET: Market prices and arrivals")
    print("     https://agmarknet.gov.in/")
    print("   - India Meteorological Department: Weather data")
    print("     https://mausam.imd.gov.in/")
    print("   - Soil Health Card Portal: Soil data")
    print("     https://soilhealth.dac.gov.in/")
    print("   - NFSM: Crop statistics")
    print("     https://nfsm.gov.in/")


def integrate_satellite_data():
    """
    Example: Integrate with satellite/remote sensing data
    """
    print("🛰️  Satellite Data Sources:")
    print("   - NASA POWER: Solar, meteorological data")
    print("     https://power.larc.nasa.gov/")
    print("   - Copernicus: Land monitoring, agriculture")
    print("     https://www.copernicus.eu/")
    print("   - Google Earth Engine: Satellite imagery analysis")
    print("     https://earthengine.google.com/")


# ==========================================================================
# EXAMPLE USAGE
# ==========================================================================

if __name__ == "__main__":
    collector = HistoricalDataCollector()
    
    print("="*70)
    print("  HISTORICAL DATA COLLECTION SYSTEM")
    print("="*70)
    
    # Step 1: Create template
    print("\n📋 Step 1: Creating Data Collection Template")
    print("-"*70)
    collector.create_data_template_csv()
    
    # Step 2: Show data sources
    print("\n\n📡 Step 2: Available Data Sources")
    print("-"*70)
    integrate_government_data()
    print()
    integrate_satellite_data()
    
    # Step 3: Generate report on existing data
    print("\n\n📊 Step 3: Example Report Generation")
    print("-"*70)
    print("(Run after collecting actual data)")
    
    print("\n" + "="*70)
    print("✅ Setup complete!")
    print("\nNext Steps:")
    print("1. Fill data_collection_template.csv with historical records")
    print("2. Use format_collected_data() to prepare for ML training")
    print("3. Train model with: python ml_crop_prediction.py")
    print("="*70)
