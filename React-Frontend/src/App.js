import React from 'react';
import NavBar from './components/NavBar';
import './index.css';
import ClassicalPage from './components/ClassicalPage';
import QuantumPage from './components/QuantumPage';

function App() {
    let component;
    switch(window.location.pathname) {
        case '/':
            component = <ClassicalPage />;
            break;
        case '/quantum':
            component = <QuantumPage />;
            break;
    }

    return (
        <div>
            <NavBar />
            { component }
        </div>

    );
}

export default App;