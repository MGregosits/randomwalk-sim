import React from 'react';
import './Plots.css';

function BarPlot({ barPlot }) {
  return (
    <div className="bar-plot-container">
      <h3>Bar Plot of the occurrences of the positions</h3>
      <img src={`data:image/png;base64,${barPlot}`} alt="Bar Plot" className="bar-plot-image" />
    </div>
  );
}

export default BarPlot;
