const mongoose = require('mongoose');

const ReportSchema = new mongoose.Schema({
  url: {
    type: String,
    required: true,
    validate: {
      validator: (v) => /^https?:\/\/[^\s/$.?#].[^\s]*$/.test(v),
      message: props => `${props.value} is not a valid URL!`
    },
    index: true
  },
  violations: {
    type: [String],
    required: true,
    validate: {
      validator: (v) => v.length > 0,
      message: 'There must be at least one violation'
    }
  },
  date: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Report', ReportSchema);
