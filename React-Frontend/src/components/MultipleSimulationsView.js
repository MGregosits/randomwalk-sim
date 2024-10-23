import React, {useState} from "react";
import axios from "axios";
import BarPlot from "./BarPlot";
import Heatmap from "./Heatmap";

function MultipleSimulationsView({gridX, gridY, targetX, targetY}){
    const [n, setN] = useState('');
    const [nSims, setNSims] = useState('');
    const [barPlot, setBarPlot] = useState('');
    const [heatmap, setHeatmap] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const runMultipleSimulations = async () => {
        setIsLoading(true);
        try {
          const response = await axios.post('http://localhost:5000/multiple_runs', {
            n: parseInt(n),
            n_sims: parseInt(nSims),
            target_x: parseInt(targetX),
            target_y: parseInt(targetY),
            grid_x: parseInt(gridX),
            grid_y: parseInt(gridY)
          });
          setBarPlot(response.data.bar_plot);
          setHeatmap(response.data.heat_map);
        } catch (error) {
          console.error('Error running multiple simulations:', error);
        } finally {
          setIsLoading(false);
        }
    };
    
    return(
    <div>
      <h2>Multiple Simulations and Visualization</h2>
      <p>Enter the number of steps (n):</p>
      <input type="number" value={n} onChange={e => setN(e.target.value)} />
      <p>Enter the number of number of simulations (n_sims):</p>
      <input type="number" value={nSims} onChange={e => setNSims(e.target.value)} />
      <button onClick={runMultipleSimulations}>Run Simulations</button>
      {isLoading ? (
        <p>Loading Bar Plot...</p>
      ) : barPlot ? (
        <BarPlot key={barPlot} barPlot={barPlot} />
      ) : null}
      {isLoading ? (
        <p>Loading Heatmap...</p>
      ) : heatmap ? (
        <Heatmap key={heatmap} heatmap={heatmap} />
      ) : null}
    </div>
    );
}

export default MultipleSimulationsView;