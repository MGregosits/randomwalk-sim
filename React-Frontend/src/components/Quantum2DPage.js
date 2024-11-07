import React, {useState} from "react";
import axios from "axios";
import BarPlot from "./BarPlot";
import Heatmap from "./Heatmap";
import HeatmapGif from "./HeatmapGif";

function Quantum2DPage() {
    const [number_qubits, setNumberQubits] = useState('');
    const [iterator, setIterator] = useState('');
    const [sample_number, setSampleNumber] = useState('');
    const [barPlot, setBarPlot] = useState('');
    const [heatMap, setHeatMap] = useState('');
    const [heatMapGif, setHeatMapGif] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const runQuantumSimulation = async () => {
        setIsLoading(true);
        try {
            const response = await axios.post('http://localhost:5000/quantum_2d', {
                number_qubits: parseInt(number_qubits),
                iterator: parseInt(iterator),
                sample_number: parseInt(sample_number)
            });
            setBarPlot(response.data.bar_plot_q_2d);
            setHeatMap(response.data.heatmap_q_2d);
            setHeatMapGif(response.data.heatmap_q_2d_gif);
        } catch (error) {
            console.error('Error running 2D quantum simulation.', error);
        } finally {
            setIsLoading(false);
        }
    };

    return(
        <div>
          <h2>Quantum 2D Simulation</h2>
          <p>Enter the n parameter (n x n grid):</p>
          <input type="number" value={number_qubits} onChange={e => setNumberQubits(e.target.value)} />
          <p>Enter the iterator value (iterator):</p>
          <input type="number" value={iterator} onChange={e => setIterator(e.target.value)} />
          <p>Enter the sample number (sample_number):</p>
          <input type="number" value={sample_number} onChange={e => setSampleNumber(e.target.value)} />
          <button onClick={runQuantumSimulation}>Run Simulations</button>
          {isLoading ? (
            <p>Loading Bar Plot...</p>
          ) : barPlot ? (
            <BarPlot key={barPlot} barPlot={barPlot} />
          ) : null}
          {isLoading ? (
            <p>Loading Heatmap...</p>
          ) : heatMap ? (
            <Heatmap key={heatMap} heatmap={heatMap} />
          ) : null}
          {isLoading ? (
            <p>Loading Heatmap GIF...</p>
          ) : heatMapGif ? (
            <HeatmapGif key={heatMapGif} heatmapgif={heatMapGif} />
          ) : null}
        </div>
        );}

export default Quantum2DPage;