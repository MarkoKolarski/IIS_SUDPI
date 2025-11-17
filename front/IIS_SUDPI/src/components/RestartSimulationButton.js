import React from 'react';

const RestartSimulationButton = ({ rutaId, onRestart, loading = false }) => {
  return (
    <button 
      onClick={onRestart}
      disabled={loading}
      className="restart-button"
      style={{
        padding: '10px 15px',
        backgroundColor: '#ff9800',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: loading ? 'not-allowed' : 'pointer',
        fontSize: '14px',
        fontWeight: 'bold',
        marginTop: '10px'
      }}
    >
      {loading ? '🔄 Pokrećem...' : '🔄 Pokreni simulaciju ispočetka'}
    </button>
  );
};

export default RestartSimulationButton;