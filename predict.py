import pandas as pd
import pickle
import datetime

# Get the current date, month, and year
today = datetime.datetime.now()
year = today.year
month = today.month
day = today.day
hour = today.hour

with open('model_temperature.pkl', 'rb') as file:
    temperature_model = pickle.load(file)

with open('model_humid.pkl', 'rb') as file:
    humid_model = pickle.load(file)

# Assuming you have the new data point
new_data = pd.DataFrame({'hour': [hour], 'day': [day], 'month': [month]})
next_temp = temperature_model.predict(new_data)
print('Predicted next humid:', next_temp[0])

next_temp = humid_model.predict(new_data)
print('Predicted next humid:', next_temp[0])