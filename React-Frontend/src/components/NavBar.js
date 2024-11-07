import React from 'react';
import './NavBar.css';

function NavBar() {
    return <nav className="nav">
        <h1 className="site-title">Random Walk Simulation</h1>
        <ul>
            <CustomLink href="/classical_1d">Classical 1D Simulation</CustomLink>
            <CustomLink href="/">Classical Simulation</CustomLink>
            <CustomLink href="/quantum">Quantum Simulation</CustomLink>
            <CustomLink href="/quantum_2d">Quantum 2D Simulation</CustomLink>
        </ul>
    </nav>
}

function CustomLink({ href, children, ...props }) {
    const path = window.location.pathname;
        return (
        <li className={path === href ? "active" : ""}>
            <a href={href} {...props}>
                {children}
            </a>
        </li>
    )
}

export default NavBar;