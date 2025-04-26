from flask import Flask, request, render_template
import mlflow.pyfunc
import pandas as pd

# Configuration
NUM_CLUSTERS = 10
mlflow.set_tracking_uri("http://127.0.0.1:5000")  # Link to MLflow backend

# Flask app
app = Flask(__name__, template_folder='.')

# Load models from MLflow registry
models = {}
for cluster_id in range(1, NUM_CLUSTERS + 1):
    model_name = f"TaxiDemandCluster_{cluster_id}"
    model_uri = f"models:/{model_name}/Production"
    try:
        models[cluster_id] = mlflow.pyfunc.load_model(model_uri)
        print(f"Loaded model '{model_name}' from registry.")
    except Exception as e:
        print(f"Failed to load model {model_name}: {e}")

@app.route("/", methods=["GET", "POST"])
def predict():
    result = None
    if request.method == "POST":
        try:
            hour = int(request.form["hour"])
            day_type = request.form["day_type"]

            day_type_map = {
                "Weekday": 0,
                "Saturday": 1,
                "Sunday": 2,
                "Public Holiday": 3
            }
            special_day = day_type_map.get(day_type, 0)
            is_weekend = 1 if special_day in [1, 2] else 0
            weekend_hour_interaction = hour * is_weekend

            input_data = pd.DataFrame([{
                "day": 15,  # Fixed placeholder or make it user-defined later
                "hour": hour,
                "special_day": special_day,
                "weekend_hour_interaction": weekend_hour_interaction
            }])

            result = {
                f"Cluster {cid}": round(model.predict(input_data)[0], 2)
                for cid, model in models.items()
            }

        except Exception as e:
            result = {"Error": str(e)}

    return render_template("web_template.html", result=result)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
