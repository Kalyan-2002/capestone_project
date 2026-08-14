
import os
import joblib
import pandas as pd


MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "artifacts",
    "best_titanic_classification_pipeline.joblib"
)


if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(
        f"Model file was not found:\n{MODEL_PATH}\n"
        "Run 02_modeling.ipynb and save the model first."
    )


model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")
print("Model path:", MODEL_PATH)


raw_passenger = pd.DataFrame([
    {
        "pclass": 3,
        "sex": "male",
        "age": 25,
        "sibsp": 0,
        "parch": 0,
        "fare": 7.25,
        "embarked": "S",
        "class": "Third",
        "who": "man",
        "adult_male": True,
        "alive": "no",
        "alone": True
    }
])

prediction = model.predict(raw_passenger)

probability = model.predict_proba(
    raw_passenger
)[:, 1]


print("\n========================================")
print("TITANIC SURVIVAL PREDICTION")
print("========================================")

print("Predicted class:", int(prediction[0]))

if prediction[0] == 1:
    print("Prediction: SURVIVED")
else:
    print("Prediction: DID NOT SURVIVE")

print(
    "Survival probability:",
    round(float(probability[0]), 4)
)
