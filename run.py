import json
from tinygrid import RandomForestForecaster, LassoForecaster


if __name__ == "__main__":
  # Forecasting
  rnn = RandomForestForecaster()
  rnn.fit()
  rnn.predict()
  # Turn all of the ndarray to list
  yy = {key: list(val) for (key, val) in rnn.y_preds.items()}
  with open("cache/final_forecast.json", "w") as f:
    json.dump(yy, f, indent=6) 
  
