import React from 'react';
import './Footer.css';

const Footer = () => {
  return (
    <footer style={footerStyle}>
      &copy; {new Date().getFullYear()} Máté Gregosits. All rights reserved.
    </footer>
  );
};

// Define styles for the footer
const footerStyle = {
  textAlign: 'center',
  padding: '10px',
  position: 'fixed',
  bottom: '0',
  width: '100%'
};

// Export the Footer component
export default Footer;
