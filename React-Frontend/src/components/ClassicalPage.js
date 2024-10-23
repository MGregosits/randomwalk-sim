import React, { useState } from 'react';
import axios from 'axios';
import Network from './Network';
import MultipleSimulationsView from './MultipleSimulationsView';
import '../index.css';

function ClassicalPage() {
    const [n, setN] = useState('');
    const [targetX, setTargetX] = useState('');
    const [targetY, setTargetY] = useState('');
    const [gridX, setGridX] = useState('');
    const [gridY, setGridY] = useState('');
    const [data, setData] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // Add a state for loading indicator

    const sendData = async () => {
        setIsLoading(true); // Set loading indicator to true
        try {
            const response = await axios.post('http://localhost:5000/process', {
                n: parseInt(n),
                target_x: parseInt(targetX),
                target_y: parseInt(targetY),
                grid_x: parseInt(gridX),
                grid_y: parseInt(gridY),
            }, {
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            setData(response.data);
        } catch (error) {
            console.error(error);
        } finally {
            setIsLoading(false); // Set loading indicator to false after request completes
        }
    };

    return (
        <div>
            <p>Enter the size of the grid (x, y):</p>
            <input type="number" value={gridX} onChange={e => setGridX(e.target.value)} />
            <input type="number" value={gridY} onChange={e => setGridY(e.target.value)} />
            <p>Choose the number of the steps!</p>
            <input type="number" value={n} onChange={e => setN(e.target.value)} />
            <p>Enter the desired state (x, y):</p>
            <input type="number" value={targetX} onChange={e => setTargetX(e.target.value)} />
            <input type="number" value={targetY} onChange={e => setTargetY(e.target.value)} />
            <button onClick={sendData}>Send Data</button>
            <div id="canvas-container">
                <div id="canvas" />
            </div>
            <p id="hitting_time">{data && `Hitting time: ${data.hitting_time}`}</p>
            <p id="mixing_time">{data && `Mixing time: ${data.mixing_time}`}</p>
            {isLoading ? ( // Conditionally render loading indicator while data is being fetched
                <p>Loading data...</p>
            ) : (
                data && <Network data={data} />
            )}
            <div>
                {gridX && gridY && targetX && targetY && (
                    <MultipleSimulationsView
                        gridX={gridX}
                        gridY={gridY}
                        targetX={targetX}
                        targetY={targetY}
                    />
                )}
            </div>
        </div>

    );
}

export default ClassicalPage;