const express = require('express');
const bodyParser = require('body-parser');
const mongoose = require('mongoose');
const cors = require('cors');
const reportRoutes = require('./routes/report');

const app = express();
app.use(bodyParser.json());
app.use(cors());

mongoose.connect('mongodb://mongo:27017/ipsee', { useNewUrlParser: true, useUnifiedTopology: true })
  .then(() => console.log('MongoDB connected'))
  .catch(err => console.error(err));

app.use('/api/report', reportRoutes);

// Remove the app.listen() from here
module.exports = app; // Export the app for use in server.js
