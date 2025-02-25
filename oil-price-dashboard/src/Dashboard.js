import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from 'recharts';

const Dashboard = () => {
  const [data, setData] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [model, setModel] = useState('arima');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/api/data')
      .then(response => setData(response.data))
      .catch(error => console.error(error));
  }, []);

  const fetchPredictions = () => {
    axios.get(`http://127.0.0.1:5000/api/predictions?model=${model}`)
      .then(response => setPredictions(response.data))
      .catch(error => console.error(error));
  };

  return (
    <div>
      <h1>Brent Oil Price Dashboard</h1>

      <div>
        <label>Select Model: </label>
        <select onChange={e => setModel(e.target.value)} value={model}>
          <option value="arima">ARIMA</option>
          <option value="var">VAR</option>
          <option value="lstm">LSTM</option>
        </select>
        <button onClick={fetchPredictions}>Fetch Predictions</button>
      </div>

      {Array.isArray(data) && (
        <LineChart width={600} height={300} data={data}>
          <Line type="monotone" dataKey="Price" stroke="#8884d8" />
          <CartesianGrid stroke="#ccc" />
          <XAxis dataKey="Date" />
          <YAxis />
          <Tooltip />
          <Legend />
        </LineChart>
      )}

      {Array.isArray(predictions) && (
        <LineChart width={600} height={300} data={predictions}>
          <Line type="monotone" dataKey="0" stroke="#82ca9d" />
          <CartesianGrid stroke="#ccc" />
          <XAxis />
          <YAxis />
          <Tooltip />
          <Legend />
        </LineChart>
      )}
    </div>
  );
};

export default Dashboard;
