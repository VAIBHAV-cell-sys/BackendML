"""
ML-Based Crop Prediction System
Uses historical crop success/failure data to predict optimal crops
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class CropPredictionModel:
    """
    Machine Learning model for crop prediction based on environmental factors
    """
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.trained = False
        
    def prepare_features(self, data):
        """
        Prepare features from raw data
        
        Args:
            data (dict): Dictionary containing weather, soil, and other parameters
        
        Returns:
            numpy array: Feature vector
        """
        features = []
        
        # Weather features
        features.append(data.get('temperature', 25.0))
        features.append(data.get('humidity', 60.0))
        features.append(data.get('rainfall', 0.0))
        features.append(data.get('wind_speed', 5.0))
        features.append(data.get('pressure', 1013.0))
        features.append(data.get('cloud_cover', 50.0))
        
        # Soil features
        features.append(data.get('soil_pH', 7.0))
        features.append(data.get('soil_nitrogen', 1.0))  # 0=Low, 1=Medium, 2=High
        features.append(data.get('soil_phosphorus', 1.0))
        features.append(data.get('soil_potassium', 1.0))
        features.append(data.get('soil_organic_matter', 1.5))
        
        # Additional features
        features.append(data.get('season', 0))  # 0=Kharif, 1=Rabi, 2=Zaid
        features.append(data.get('month', 6))  # 1-12
        
        return np.array(features).reshape(1, -1)
    
    def create_sample_dataset(self, filename='crop_historical_data.csv'):
        """
        Create a sample historical dataset for training
        This would be replaced with actual historical data
        """
        np.random.seed(42)
        
        # Define crop types
        crops = ['Wheat', 'Rice', 'Bajra', 'Maize', 'Cotton', 
                'Sugarcane', 'Groundnut', 'Soybean', 'Jowar', 'Pulses']
        
        # Generate synthetic historical data
        n_samples = 5000
        data = []
        
        for _ in range(n_samples):
            # Random crop
            crop = np.random.choice(crops)
            
            # Generate features based on crop preferences
            if crop == 'Rice':
                temp = np.random.normal(28, 3)
                humidity = np.random.normal(75, 10)
                rainfall = np.random.normal(8, 3)
                soil_pH = np.random.normal(6.5, 0.5)
                success = 1 if (rainfall > 5 and humidity > 65) else 0
                
            elif crop == 'Wheat':
                temp = np.random.normal(22, 4)
                humidity = np.random.normal(55, 10)
                rainfall = np.random.normal(2, 1.5)
                soil_pH = np.random.normal(6.8, 0.4)
                success = 1 if (temp < 25 and rainfall < 3) else 0
                
            elif crop == 'Bajra':
                temp = np.random.normal(30, 4)
                humidity = np.random.normal(45, 10)
                rainfall = np.random.normal(1, 1)
                soil_pH = np.random.normal(7.5, 0.6)
                success = 1 if (rainfall < 2 and temp > 25) else 0
                
            elif crop == 'Cotton':
                temp = np.random.normal(28, 3)
                humidity = np.random.normal(60, 10)
                rainfall = np.random.normal(3, 2)
                soil_pH = np.random.normal(7.2, 0.5)
                success = 1 if (temp > 25 and rainfall < 5) else 0
                
            elif crop == 'Maize':
                temp = np.random.normal(26, 3)
                humidity = np.random.normal(65, 10)
                rainfall = np.random.normal(4, 2)
                soil_pH = np.random.normal(6.5, 0.5)
                success = 1 if (rainfall > 2 and temp > 23) else 0
                
            else:  # Other crops
                temp = np.random.normal(26, 5)
                humidity = np.random.normal(60, 15)
                rainfall = np.random.normal(3, 2.5)
                soil_pH = np.random.normal(7.0, 0.8)
                success = np.random.choice([0, 1], p=[0.3, 0.7])
            
            # Additional features
            wind_speed = np.random.uniform(2, 15)
            pressure = np.random.normal(1013, 5)
            cloud_cover = np.random.uniform(0, 100)
            
            # Soil nutrients (0=Low, 1=Medium, 2=High)
            nitrogen = np.random.choice([0, 1, 2])
            phosphorus = np.random.choice([0, 1, 2])
            potassium = np.random.choice([0, 1, 2])
            organic_matter = np.random.uniform(0.5, 3.0)
            
            # Season and month
            season = np.random.choice([0, 1, 2])  # Kharif, Rabi, Zaid
            month = np.random.randint(1, 13)
            
            data.append({
                'crop': crop,
                'temperature': round(temp, 1),
                'humidity': round(humidity, 1),
                'rainfall': round(max(0, rainfall), 2),
                'wind_speed': round(wind_speed, 1),
                'pressure': round(pressure, 1),
                'cloud_cover': round(cloud_cover, 1),
                'soil_pH': round(soil_pH, 2),
                'nitrogen': nitrogen,
                'phosphorus': phosphorus,
                'potassium': potassium,
                'organic_matter': round(organic_matter, 2),
                'season': season,
                'month': month,
                'success': success
            })
        
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"✅ Sample dataset created: {filename}")
        print(f"📊 Total samples: {len(df)}")
        print(f"🌾 Crops: {df['crop'].unique()}")
        print(f"✓ Success rate: {df['success'].mean() * 100:.1f}%")
        
        return df
    
    def train(self, data_file='crop_historical_data.csv'):
        """
        Train the crop prediction model
        
        Args:
            data_file (str): Path to historical data CSV
        """
        print("🔄 Loading training data...")
        
        # Load data
        try:
            df = pd.read_csv(data_file)
        except FileNotFoundError:
            print("⚠️  No historical data found. Creating sample dataset...")
            df = self.create_sample_dataset(data_file)
        
        print(f"📊 Loaded {len(df)} historical records")
        
        # Filter only successful crops for recommendation
        successful_df = df[df['success'] == 1].copy()
        print(f"✓ Successful crops: {len(successful_df)} records")
        
        # Prepare features
        feature_columns = [
            'temperature', 'humidity', 'rainfall', 'wind_speed', 
            'pressure', 'cloud_cover', 'soil_pH', 'nitrogen', 
            'phosphorus', 'potassium', 'organic_matter', 'season', 'month'
        ]
        
        X = successful_df[feature_columns].values
        y = successful_df['crop'].values
        
        self.feature_names = feature_columns
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        print("🧠 Training Random Forest model...")
        
        # Train Random Forest
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Model trained successfully!")
        print(f"🎯 Accuracy: {accuracy * 100:.2f}%")
        
        # Cross-validation score
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5)
        print(f"📊 Cross-validation score: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📈 Top 5 Important Features:")
        for idx, row in feature_importance.head(5).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Classification report
        print("\n📋 Classification Report:")
        print(classification_report(
            y_test, y_pred,
            target_names=self.label_encoder.classes_,
            zero_division=0
        ))
        
        self.trained = True
        
        return accuracy
    
    def predict(self, current_data):
        """
        Predict best crop based on current conditions
        
        Args:
            current_data (dict): Current weather and soil conditions
        
        Returns:
            dict: Prediction results with top recommendations
        """
        if not self.trained:
            raise Exception("Model not trained. Call train() first.")
        
        # Prepare features
        features = self.prepare_features(current_data)
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Get probabilities for all crops
        probabilities = self.model.predict_proba(features_scaled)[0]
        
        # Get top 3 predictions
        top_indices = np.argsort(probabilities)[::-1][:3]
        
        predictions = []
        for idx in top_indices:
            crop = self.label_encoder.classes_[idx]
            confidence = probabilities[idx] * 100
            
            predictions.append({
                'crop': crop,
                'confidence': round(confidence, 2),
                'probability': round(probabilities[idx], 4)
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'primary_recommendation': predictions[0]['crop'],
            'confidence': predictions[0]['confidence'],
            'all_recommendations': predictions,
            'input_features': current_data
        }
    
    def save_model(self, model_path='models/crop_prediction_model.pkl'):
        """
        Save trained model to disk
        """
        import os
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_names,
            'trained': self.trained
        }
        
        joblib.dump(model_data, model_path)
        print(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path='models/crop_prediction_model.pkl'):
        """
        Load trained model from disk
        """
        model_data = joblib.load(model_path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.label_encoder = model_data['label_encoder']
        self.feature_names = model_data['feature_names']
        self.trained = model_data['trained']
        
        print(f"✅ Model loaded from {model_path}")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("  CROP PREDICTION ML MODEL - TRAINING & TESTING")
    print("=" * 70)
    
    # Initialize model
    model = CropPredictionModel()
    
    # Train model
    print("\n📚 Step 1: Training Model on Historical Data")
    print("-" * 70)
    model.train()
    
    # Save model
    print("\n💾 Step 2: Saving Model")
    print("-" * 70)
    model.save_model()
    
    # Test prediction with sample data
    print("\n🔮 Step 3: Testing Predictions")
    print("-" * 70)
    
    # Test case 1: Conditions favorable for Rice
    test_data_1 = {
        'temperature': 28.5,
        'humidity': 75,
        'rainfall': 8.2,
        'wind_speed': 5.5,
        'pressure': 1012,
        'cloud_cover': 60,
        'soil_pH': 6.5,
        'soil_nitrogen': 2,  # High
        'soil_phosphorus': 2,  # High
        'soil_potassium': 1,  # Medium
        'soil_organic_matter': 2.3,
        'season': 0,  # Kharif
        'month': 7  # July
    }
    
    prediction_1 = model.predict(test_data_1)
    print("\n📍 Test Case 1: High rainfall, warm temperature")
    print(f"🌾 Recommended Crop: {prediction_1['primary_recommendation']}")
    print(f"🎯 Confidence: {prediction_1['confidence']:.2f}%")
    print(f"📊 Top 3 Recommendations:")
    for rec in prediction_1['all_recommendations']:
        print(f"   - {rec['crop']}: {rec['confidence']:.2f}%")
    
    # Test case 2: Conditions favorable for Bajra
    test_data_2 = {
        'temperature': 32,
        'humidity': 40,
        'rainfall': 0.5,
        'wind_speed': 8,
        'pressure': 1010,
        'cloud_cover': 20,
        'soil_pH': 8.1,
        'soil_nitrogen': 0,  # Low
        'soil_phosphorus': 1,  # Medium
        'soil_potassium': 1,  # Medium
        'soil_organic_matter': 0.8,
        'season': 0,  # Kharif
        'month': 6  # June
    }
    
    prediction_2 = model.predict(test_data_2)
    print("\n📍 Test Case 2: Low rainfall, hot temperature, arid soil")
    print(f"🌾 Recommended Crop: {prediction_2['primary_recommendation']}")
    print(f"🎯 Confidence: {prediction_2['confidence']:.2f}%")
    print(f"📊 Top 3 Recommendations:")
    for rec in prediction_2['all_recommendations']:
        print(f"   - {rec['crop']}: {rec['confidence']:.2f}%")
    
    # Test case 3: Conditions favorable for Wheat
    test_data_3 = {
        'temperature': 20,
        'humidity': 50,
        'rainfall': 1.5,
        'wind_speed': 4,
        'pressure': 1015,
        'cloud_cover': 30,
        'soil_pH': 7.0,
        'soil_nitrogen': 2,  # High
        'soil_phosphorus': 1,  # Medium
        'soil_potassium': 2,  # High
        'soil_organic_matter': 2.0,
        'season': 1,  # Rabi
        'month': 11  # November
    }
    
    prediction_3 = model.predict(test_data_3)
    print("\n📍 Test Case 3: Cool temperature, low rainfall, Rabi season")
    print(f"🌾 Recommended Crop: {prediction_3['primary_recommendation']}")
    print(f"🎯 Confidence: {prediction_3['confidence']:.2f}%")
    print(f"📊 Top 3 Recommendations:")
    for rec in prediction_3['all_recommendations']:
        print(f"   - {rec['crop']}: {rec['confidence']:.2f}%")
    
    print("\n" + "=" * 70)
    print("✅ Training and testing completed successfully!")
    print("=" * 70)
