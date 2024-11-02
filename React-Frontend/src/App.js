import React from 'react';
import NavBar from './components/NavBar';
import './index.css';
import ClassicalPage from './components/ClassicalPage';
import QuantumPage from './components/QuantumPage';
import Quantum2DPage from './components/Quantum2DPage';
import Classical1D from './components/Classical1D';

function App() {
    let component;
    switch(window.location.pathname) {
        case '/classical_1d':
            component = <Classical1D />;
            break;
        case '/':
            component = <ClassicalPage />;
            break;
        case '/quantum':
            component = <QuantumPage />;
            break;
        case '/quantum_2d':
            component = <Quantum2DPage />;
    }

    return (
        <div>
            <NavBar />
            { component }
        </div>

    );
}

export default App;