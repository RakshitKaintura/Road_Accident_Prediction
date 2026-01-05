import joblib

MODEL_PATH = "model/xgb_severe_model.pkl"
model = joblib.load(MODEL_PATH)

def predict_proba(features_df):
    return model.predict_proba(features_df)[:, 1]
