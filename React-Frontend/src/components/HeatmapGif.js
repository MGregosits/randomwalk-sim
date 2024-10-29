import React from 'react';
import './Plots.css';

function HeatmapGif({ heatmapgif }) {
  return (
    <div className="heatmap-container">
      <h3>GIF of the heatmaps of the random walk (iterates from 1 to 2^n)</h3>
      <img src={`data:image/gif;base64,${heatmapgif}`} alt="Heatmap GIF" className="heatmap-gif" />
    </div>
  );
}

export default HeatmapGif;