from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import pickle
import os

app = Flask(__name__)

with open('trained_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Read the values from the file
with open('values.txt', 'r') as Vfile:
    lines = Vfile.readlines()

# Extract the values
max_valueA = float(lines[0].split(':')[1].strip())
min_valueA = float(lines[1].split(':')[1].strip())
max_valueN = float(lines[2].split(':')[1].strip())
min_valueN = float(lines[3].split(':')[1].strip())
    
@app.route('/')
def home():
    print(model.feature_names_in_)
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    city = request.form.get('City')
    property_type = request.form.get('type')
    hasParking = request.form.get('hasParking')
    room_number = request.form.get('room_number')
    Area = request.form.get('Area')
    #min-max scaling
    room_number= float(room_number)
    room_number= ((room_number- min_valueN)/(max_valueN-min_valueN))
    Area = float(Area)
    Area=((Area-min_valueA)/(max_valueA-min_valueA))
    
     
    string_features = ['אילת','אריאל','באר שבע','בית שאן','בת ים','גבעת שמואל','דימונה','הוד השרון','הרצליה','זכרון יעקב','חולון','חיפה','יהוד מונוסון','ירושלים','כפר סבא','מודיעין מכבים רעות','נהריה','נוף הגליל','נס ציונה','נתניה','פתח תקווה','צפת','קרית ביאליק','ראשון לציון','רחובות','רמת גן','רעננה','שוהם','תל אביב','בית פרטי','דו משפחתי','דופלקס','דירה','דירת גג','דירת גן','פנטהאוז',"קוטג'"]

    # Create a DataFrame with the input data
    input_data = pd.DataFrame({
    'אילת': [0]
})
    for feature in string_features[1:]:
        input_data[feature] = 0
    input_data[city] = 1
    input_data[property_type] = 1
    input_data['number'] = float(room_number)  # Convert room_number to float
    input_data['Area'] = float(Area)  # Convert area to float
    input_data['hasParking'] = hasParking
    

    predicted_price = model.predict(input_data)[0]
    text_output = f"Predicted Property Value: {predicted_price:.2f}"

    return render_template('index.html', prediction_text =text_output)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    
    app.run(host='0.0.0.0', port=port, debug=True)