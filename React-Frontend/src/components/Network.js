import React, { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';

cytoscape.use(cola);

const Network = ({ data }) => {
  const cyRef = useRef(null);

  useEffect(() => {
    if (!data) return;

    const scaleFactor = 100;
    const xOffset = Math.min(...data.x) * scaleFactor;
    const yOffset = Math.min(...data.y) * scaleFactor;
    
    const cy = cytoscape({
      container: cyRef.current,
      elements: [],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(visitedColor)',
            label: 'data(label)',
            color: '#333',
            'text-valign': 'center',
            'text-halign': 'center',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#ccc',
            'target-arrow-shape': 'triangle',
            'target-arrow-color': '#ccc',
            'curve-style': 'bezier',
          },
        },
      ],
      layout: {
        name: 'preset',
      },
      userZoomingEnabled: false,
    });

    const nodeVisits = {}; // Track node visits and steps

    // Process each step in the walk
    data.x.forEach((x, index) => {
      const y = data.y[index];
      const id = `${x},${y}`;

      // Record visit and step
      if (!nodeVisits[id]) {
        nodeVisits[id] = { count: 0, steps: [] };
        // create node on the first visit
        cy.add({
          group: 'nodes',
          data: { id, visitedColor: '#5f5', label: id },
          position: { x: x * scaleFactor - xOffset, y: yOffset - y * scaleFactor },
        });
      }
      nodeVisits[id].count += 1;
      nodeVisits[id].steps.push(index);

      if (index <= 0) {
        return;
      }
      const prevX = data.x[index - 1];
      const prevY = data.y[index - 1];
      const sourceId = `${prevX},${prevY}`;
      cy.add({
        group: 'edges',
        data: {
          id: `e${index}`,
          source: sourceId,
          target: id,
        },
      });
    });

    // Iterate the whole grid to ensure all nodes are shown
    for (let y = 0; y < data.grid_y; y++) {
      for (let x = 0; x < data.grid_x; x++) {
        const id = `${x},${y}`;
        // if node is not part of the walk
        if (!nodeVisits[id]) {
          cy.add({
            group: 'nodes',
            data: {id, visitedColor: '#40E0D0', label: id},
            position: {x: x * scaleFactor - xOffset, y: yOffset - y * scaleFactor},
          });
        }
      }
    }
    // Show tooltip on mouseover
    cy.on('mouseover', 'node', (event) => {
      const node = event.target;
      const nodeId = node.id();
      const tooltip = document.getElementById('tooltip');
      // check if the node is part of the walk
      if (nodeVisits[nodeId]) {
        const steps = nodeVisits[nodeId].steps.join(', ');
        tooltip.innerHTML = `Visited on steps ${steps}`;
      } else {
         // If the node is not part of the walk
        tooltip.innerHTML = 'This node was not reached during the walk.';
      }
      tooltip.style.display = 'block';
      tooltip.style.left = `${event.renderedPosition.x}px`;
      tooltip.style.top = `${event.renderedPosition.y + 450}px`;
    });

    // Hiding the tooltip when not hovering
    cy.on('mouseout', 'node', () => {
      const tooltip = document.getElementById('tooltip');
      tooltip.style.display = 'none';
    });

    // Apply layout
    cy.layout({ name: 'preset' }).run();

  }, [data]);

  return (
    <div>
      <div ref={cyRef} style={{ width: '100%', height: '600px' }} />
      <div id="tooltip" style={{ display: 'none', position: 'absolute', backgroundColor: '#342c39', border: '1px solid black', padding: '5px' }} />
    </div>
  );
};

export default Network;
