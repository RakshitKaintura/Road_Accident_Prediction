import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, roc_auc_score

df = pd.read_csv("data/processed/train.csv")

X = df.drop("severe", axis=1)
y = df["severe"]

scale_pos_weight = (y == 0).sum() / (y == 1).sum()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

base_model = XGBClassifier(
    objective="binary:logistic",
    scale_pos_weight=scale_pos_weight,
    max_depth=6,
    n_estimators=500,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric="auc",
    random_state=42
)

base_model.fit(X_train, y_train)

# 🔥 Probability calibration
model = CalibratedClassifierCV(base_model, method="isotonic", cv=3)
model.fit(X_train, y_train)

proba = model.predict_proba(X_test)[:, 1]

print(classification_report(y_test, (proba > 0.42).astype(int)))
print("ROC-AUC:", roc_auc_score(y_test, proba))

joblib.dump(model, "backend/model/xgb_model.pkl")
print("Spatial + calibrated severe-risk model saved")
