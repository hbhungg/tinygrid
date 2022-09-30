// Vega lite graph example
const jsonData = {
  "data": {
    "width": "container",
    "height": "container",
    "sequence": {
      "start": 0,
      "stop": 12.7,
      "step": 0.1,
      "as": "x"
    }
  },
  "transform": [
    {
      "calculate": "sin(datum.x)",
      "as": "sin(x)"
    }
  ],
  "mark": "line",
  "encoding": {
    "x": {
      "field": "x",
      "type": "quantitative"
    },
    "y": {
      "field": "sin(x)",
      "type": "quantitative"
    }
  }
};
// Call embed function on html element by id: vis1
vegaEmbed('#vis1', jsonData);