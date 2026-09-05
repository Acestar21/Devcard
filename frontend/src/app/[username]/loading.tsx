export default function Loading() {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      textAlign: 'center',
      padding: '2rem',
      fontFamily: 'system-ui, -apple-system, sans-serif',
      backgroundColor: '#f8fafc',
      color: '#64748b'
    }}>
      <div style={{
        width: '40px',
        height: '40px',
        border: '4px solid #e2e8f0',
        borderTop: '4px solid #3b82f6',
        borderRadius: '50%',
        animation: 'spin 1s linear infinite',
        marginBottom: '1.5rem'
      }} />
      <p style={{ fontSize: '1.125rem', fontWeight: '500', color: '#1e293b' }}>
        Loading profile...
      </p>
      <p style={{ fontSize: '0.875rem', maxWidth: '300px', marginTop: '0.5rem', lineHeight: '1.5' }}>
        First load may take up to a minute if the backend has been idle (free hosting).
      </p>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
