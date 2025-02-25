from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import joblib
import torch

app = Flask(__name__)
CORS(app)

# Load pre-trained models
arima_model_path = 'D:/week10 data/arima_model.pkl'
var_model_path = 'D:/week10 data/var_model.pkl'
lstm_model_path = 'D:/week10 data/lstm_model.pth'

arima_model = joblib.load(arima_model_path)
var_model = joblib.load(var_model_path)

# Define the LSTM model class (same as before)
class LSTMModel(torch.nn.Module):
    def __init__(self, input_size, hidden_size, num_layers, output_size):
        super(LSTMModel, self).__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.lstm = torch.nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = torch.nn.Linear(hidden_size, output_size)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_size)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

# Initialize and load the LSTM model
input_size = 1
hidden_size = 50
num_layers = 1
output_size = 1
device = torch.device('cpu')

lstm_model = LSTMModel(input_size, hidden_size, num_layers, output_size).to(device)
lstm_model.load_state_dict(torch.load(lstm_model_path))

# Load data
data_path = 'D:/week10 data/merged_data.csv'
data = pd.read_csv(data_path, parse_dates=['Date'])

@app.route('/')
def index():
    return "Welcome to the Brent Oil Price Dashboard API. Access specific endpoints for data and predictions."

@app.route('/api/data', methods=['GET'])
def get_data():
    result = data.to_dict(orient='records')
    return jsonify(result)

@app.route('/api/predictions', methods=['GET'])
def get_predictions():
    model_type = request.args.get('model')

    if model_type == 'arima':
        predictions = arima_model.forecast(steps=30).tolist()
    elif model_type == 'var':
        predictions = var_model.forecast(var_model.y, steps=30).tolist()
    elif model_type == 'lstm':
        lstm_input = torch.FloatTensor(data['Price'].values).view(-1, input_size, 1).to(device)
        with torch.no_grad():
            predictions = lstm_model(lstm_input).cpu().numpy().tolist()
    else:
        return jsonify({'error': 'Invalid model type'})

    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)
