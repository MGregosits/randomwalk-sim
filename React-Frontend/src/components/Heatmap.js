import React from 'react';
import './Plots.css';

function Heatmap({ heatmap }) {
  return (
    <div className="heatmap-container">
      <h3>Heatmap of the random walk</h3>
      <img src={`data:image/png;base64,${heatmap}`} alt="Heatmap" className="heatmap-image" />
    </div>
  );
}

export default Heatmap;