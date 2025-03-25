import pandas as pd
import random

# Enhanced Credit Score Calculation
def calculate_credit_score(aadhaar_number, land_data):
    try:
        land_info = land_data[land_data['aadhaar_number'] == int(aadhaar_number)]
        if not land_info.empty:
            land_size = land_info.iloc[0]['land_size']
            crop_type = land_info.iloc[0]['crop_type']
            
            # Example scoring logic
            base_score = 500
            score = base_score + (land_size * 10) + (len(crop_type) * 5)
            risk = "Low" if score > 700 else "Moderate" if score > 500 else "High"
            return score, risk
        return None, None
    except ValueError:
        return None, None

# Map Risk Levels to Numeric Values
def get_risk_level(risk):
    levels = {"Low": 100, "Moderate": 50, "High": 20}
    return levels.get(risk, 0)
