"""
Enhanced main.py with ML Prediction Endpoints
Adds ML-based crop prediction while keeping existing rule-based system
"""

# Add these imports to your existing main.py
from ml_integration import get_ml_prediction, compare_with_rules, ml_service
from datetime import datetime

# ========== NEW ML ENDPOINTS (Add to your existing main.py) ==========

@app.get("/ml-predict/{location}", tags=["ML Predictions"])
async def ml_crop_prediction(location: str):
    """
    Get ML-based crop prediction for a location
    
    Uses trained machine learning model on historical crop success data
    to predict the best crop based on current conditions.
    
    Returns:
        - Primary ML recommendation
        - Confidence score
        - Top 3 crop predictions with probabilities
        - Input features used for prediction
    """
    try:
        logger.info(f"ML prediction request for location: {location}")
        
        # Get current data
        from services.weather import get_weather
        from services.soil import get_soil
        
        weather_data = get_weather(location)
        soil_data = get_soil(location)
        current_month = datetime.now().month
        
        # Get ML prediction
        ml_prediction = get_ml_prediction(location, weather_data, soil_data, current_month)
        
        # Add timestamp
        ml_prediction["timestamp"] = datetime.now().isoformat()
        
        logger.info(f"ML prediction: {ml_prediction['primary_recommendation']} "
                   f"({ml_prediction['confidence']:.2f}%)")
        
        return ml_prediction
    
    except ValueError as e:
        logger.error(f"Location error: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    
    except Exception as e:
        logger.error(f"ML prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/hybrid-predict/{location}", tags=["ML Predictions"])
async def hybrid_crop_prediction(location: str):
    """
    Hybrid prediction combining rule-based and ML approaches
    
    Provides both traditional rule-based recommendations and ML predictions,
    along with a comparison to show agreement/disagreement between methods.
    
    Returns:
        - Rule-based recommendation
        - ML recommendation
        - Comparison analysis
        - Both prediction details
    """
    try:
        logger.info(f"Hybrid prediction request for location: {location}")
        
        # Get data
        from services.weather import get_weather
        from services.soil import get_soil
        from services.mandi import get_price
        from engine import analyze_farm
        
        # Get rule-based prediction
        farm_analysis = analyze_farm(location)
        rule_based_crop = farm_analysis['recommended_crop']
        
        # Get ML prediction
        weather_data = get_weather(location)
        soil_data = get_soil(location)
        current_month = datetime.now().month
        
        ml_prediction = get_ml_prediction(location, weather_data, soil_data, current_month)
        
        # Compare predictions
        comparison = compare_with_rules(rule_based_crop, ml_prediction)
        
        # Get price data for both crops
        rule_price = get_price(rule_based_crop)
        ml_price = get_price(ml_prediction['primary_recommendation'])
        
        response = {
            "location": location,
            "timestamp": datetime.now().isoformat(),
            
            "rule_based": {
                "crop": rule_based_crop,
                "confidence": farm_analysis['confidence'],
                "reason": farm_analysis['reason'],
                "risk_level": farm_analysis['risk_level'],
                "price": rule_price.get('current_price', rule_price['price'])
            },
            
            "machine_learning": {
                "crop": ml_prediction['primary_recommendation'],
                "confidence": ml_prediction['confidence'],
                "top_3": ml_prediction['all_recommendations'],
                "price": ml_price.get('current_price', ml_price['price'])
            },
            
            "comparison": comparison,
            
            "recommendation": {
                "final_crop": rule_based_crop if comparison['agreement'] else 
                             (rule_based_crop if farm_analysis['confidence'] > ml_prediction['confidence'] 
                              else ml_prediction['primary_recommendation']),
                "method": "rule-based" if comparison['agreement'] or 
                         farm_analysis['confidence'] > ml_prediction['confidence'] else "ml",
                "confidence": comparison['strength'],
                "note": comparison['verdict']
            }
        }
        
        logger.info(f"Hybrid prediction complete: Rule={rule_based_crop}, ML={ml_prediction['primary_recommendation']}")
        
        return response
    
    except Exception as e:
        logger.error(f"Hybrid prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ml-train", tags=["ML Management"])
async def retrain_ml_model():
    """
    Retrain the ML model with latest data
    
    This endpoint allows you to retrain the machine learning model
    when new historical data is available.
    
    Note: This operation may take several minutes
    """
    try:
        logger.info("Starting ML model retraining...")
        
        # Retrain model
        accuracy = ml_service.model.train()
        
        # Save updated model
        ml_service.model.save_model(ml_service.model_path)
        
        logger.info(f"Model retrained successfully. Accuracy: {accuracy * 100:.2f}%")
        
        return {
            "status": "success",
            "message": "Model retrained successfully",
            "accuracy": round(accuracy * 100, 2),
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Model retraining error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ml-model-info", tags=["ML Management"])
async def get_ml_model_info():
    """
    Get information about the current ML model
    
    Returns model statistics, feature importance, and training details
    """
    try:
        if not ml_service.model.trained:
            return {
                "status": "not_trained",
                "message": "Model has not been trained yet"
            }
        
        # Get feature importance
        import pandas as pd
        feature_importance = pd.DataFrame({
            'feature': ml_service.model.feature_names,
            'importance': ml_service.model.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        top_features = feature_importance.head(5).to_dict('records')
        
        return {
            "status": "trained",
            "model_type": "RandomForest",
            "n_estimators": ml_service.model.model.n_estimators,
            "features_count": len(ml_service.model.feature_names),
            "crops": list(ml_service.model.label_encoder.classes_),
            "top_5_features": top_features,
            "trained": ml_service.model.trained
        }
    
    except Exception as e:
        logger.error(f"Model info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENHANCED ADVICE ENDPOINT ==========
# Replace or add alongside your existing /advice endpoint

@app.get("/advice-ml", tags=["Chatbot"])
async def get_advice_with_ml(
    message: str = Query(..., description="User's question about farming"),
    location: str = Query(..., description="Location/city name"),
    use_ml: bool = Query(True, description="Use ML prediction (true) or rule-based (false)")
):
    """
    Enhanced advice endpoint with ML option
    
    Provides crop advice using either:
    - ML-based prediction (use_ml=true)
    - Traditional rule-based system (use_ml=false)
    - Hybrid approach (default)
    """
    try:
        logger.info(f"Enhanced advice request: location={location}, use_ml={use_ml}")
        
        # Import required modules
        from chatbot import chatbot
        from engine import analyze_farm
        from services.weather import get_weather
        from services.soil import get_soil
        
        # Get base analysis
        farm_analysis = analyze_farm(location)
        
        if use_ml:
            # Get ML prediction
            weather_data = get_weather(location)
            soil_data = get_soil(location)
            ml_prediction = get_ml_prediction(location, weather_data, soil_data)
            
            # Override rule-based recommendation with ML
            farm_analysis['recommended_crop'] = ml_prediction['primary_recommendation']
            farm_analysis['confidence'] = ml_prediction['confidence']
            farm_analysis['ml_enabled'] = True
            farm_analysis['ml_top_3'] = ml_prediction['all_recommendations']
        else:
            farm_analysis['ml_enabled'] = False
        
        # Build enhanced context for chatbot
        context = f"{message}\n\nML Prediction: {'Enabled' if use_ml else 'Disabled'}"
        
        # Get AI response
        response = chatbot.chatbot_response(context, location)
        
        # Add ML metadata
        response['prediction_method'] = 'machine_learning' if use_ml else 'rule_based'
        response['timestamp'] = datetime.now().isoformat()
        
        return response
    
    except Exception as e:
        logger.error(f"Enhanced advice error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== INSTRUCTIONS TO INTEGRATE ==========
"""
TO INTEGRATE INTO YOUR EXISTING main.py:

1. Add imports at the top:
   from ml_integration import get_ml_prediction, compare_with_rules, ml_service
   from datetime import datetime

2. Add these new endpoints to your app (copy all functions above)

3. Your existing endpoints (/advice, /analyze, etc.) remain unchanged

4. Test the new ML endpoints:
   - GET /ml-predict/Pune
   - GET /hybrid-predict/Mumbai
   - GET /advice-ml?message=What to plant&location=Delhi&use_ml=true

5. The ML model will train automatically on first use if no saved model exists
"""
