import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { Background, Controls, MarkerType, applyNodeChanges, applyEdgeChanges } from 'reactflow';
import 'reactflow/dist/style.css';
import { getBlastRadius } from '../api/client';

const CustomNode = ({ data }) => {
  const getIcon = () => {
    switch(data.nodeType) {
      case 'event': return '🌪️';
      case 'supplier': return '🏭';
      case 'component': return '🔩';
      case 'product': return '📱';
      case 'inventory': return '📦';
      case 'financial': return '💰';
      default: return '📍';
    }
  };

  const getLabel = () => {
    if (data.title) return data.title;
    if (data.name) return data.name;
    if (data.nodeType === 'inventory') return `${data.runway} Days Runway`;
    if (data.nodeType === 'financial') return `$${data.revenue_at_risk?.toLocaleString()}`;
    return data.label || 'Node';
  };
  
  const getColor = () => {
    if (data.nodeType === 'event') return '#ef4444';
    if (data.nodeType === 'supplier') return '#f59e0b';
    if (data.nodeType === 'financial') return '#ef4444';
    return '#3b82f6';
  };

  return (
    <div style={{
      padding: '12px 16px',
      background: 'var(--bg-card)',
      border: `2px solid ${getColor()}`,
      borderRadius: '8px',
      color: '#fff',
      fontSize: '12px',
      minWidth: '150px',
      textAlign: 'center',
      boxShadow: '0 4px 6px rgba(0,0,0,0.3)'
    }}>
      <div style={{ fontSize: '20px', marginBottom: '8px' }}>{getIcon()}</div>
      <div style={{ fontWeight: 'bold', fontSize: '13px', textTransform: 'uppercase', color: 'var(--text-secondary)' }}>
        {data.nodeType}
      </div>
      <div style={{ marginTop: '4px' }}>{getLabel()}</div>
    </div>
  );
};

const nodeTypes = { customNode: CustomNode };

export default function BlastRadius({ assessmentId }) {
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);

  useEffect(() => {
    const fetchGraph = async () => {
      try {
        const res = await getBlastRadius(assessmentId);
        
        // Add markerEnd to edges for arrows
        const formattedEdges = res.data.edges.map(e => ({
           ...e,
           markerEnd: { type: MarkerType.ArrowClosed, color: e.style?.stroke || '#888' },
           style: { ...e.style, strokeWidth: 2 }
        }));
        
        setNodes(res.data.nodes);
        setEdges(formattedEdges);
      } catch (e) {
        console.error("Failed to load blast radius", e);
      }
    };
    fetchGraph();
  }, [assessmentId]);

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);

  const onNodeClick = (_, node) => {
    setSelectedNode(node);
  };

  return (
    <div className="card mt-24">
      <h3>Risk Blast Radius</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
        Visualize how this disruption propagates through the supply chain dependency tree.
      </p>

      <div style={{ display: 'flex', gap: '24px', height: '600px' }}>
        <div style={{ flex: 1, background: '#0a0a0a', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border)' }}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-left"
          >
            <Background color="#333" gap={16} />
            <Controls />
          </ReactFlow>
        </div>

        {selectedNode && (
          <div style={{ width: '300px', background: 'var(--bg-card-hover)', borderRadius: '8px', padding: '16px', border: '1px solid var(--border)' }}>
            <h4 style={{ textTransform: 'capitalize', color: 'var(--accent-blue)', borderBottom: '1px solid var(--border)', paddingBottom: '8px', marginBottom: '12px' }}>
              {selectedNode.data.nodeType} Details
            </h4>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              {Object.entries(selectedNode.data).map(([key, val]) => {
                if (key === 'nodeType' || key === 'label') return null;
                return (
                  <div key={key}>
                    <strong style={{ color: 'var(--text-secondary)', textTransform: 'capitalize' }}>{key.replace('_', ' ')}:</strong>
                    <div style={{ marginTop: '4px' }}>
                      {typeof val === 'number' ? (key.includes('revenue') ? `$${val.toLocaleString()}` : val) : String(val)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
