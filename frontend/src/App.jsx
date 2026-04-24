const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export default function App() {
  return (
    <main style={{fontFamily: 'system-ui, sans-serif', padding: '2rem'}}>
      <h1>React + Django</h1>
      <p>Your frontend is configured to call the backend at:</p>
      <code>{apiUrl}</code>
      <p>To use the Django health endpoint, visit:</p>
      <a href={`${apiUrl}/api/health/`} target="_blank" rel="noreferrer">
        {apiUrl}/api/health/
      </a>
    </main>
  )
}
