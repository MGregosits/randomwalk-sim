import React, {useState} from "react";
import axios from "axios";
import BarPlot from "./BarPlot";
import Heatmap from "./Heatmap";

function Classical1D(){
    const [n, setN] = useState('');
    const [nSims, setNSims] = useState('');
    const [nStates, setNStates] = useState('');
    const [barPlot, setBarPlot] = useState('');
    const [heatmap, setHeatmap] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const runMultipleSimulations = async () => {
        setIsLoading(true);
        try {
          const response = await axios.post('http://localhost:5000/classical_1d', {
            n: parseInt(n),
            n_sims: parseInt(nSims),
            n_states: parseInt(nStates)
          });
          setBarPlot(response.data.bar_plot_1d);
          setHeatmap(response.data.heat_map_1d);
        } catch (error) {
          console.error('Error running multiple simulations:', error);
        } finally {
          setIsLoading(false);
        }
    };
    
    return(
    <div>
      <h2>Multiple Simulations and Visualization</h2>
      <p>Enter the number of states (n_states):</p>
      <input type="number" value={nStates} onChange={e => setNStates(e.target.value)} />
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

export default Classical1D;