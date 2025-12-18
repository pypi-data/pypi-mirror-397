import { useEffect, useState } from 'react';

import './App.css';

interface HealthCheckResponse {
  status: string;
  hostname: string;
  version: string;
}

function App() {
  const [healthData, setHealthData] = useState<HealthCheckResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealthCheck = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch('/health');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: HealthCheckResponse = await response.json();
        setHealthData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch health check');
      } finally {
        setLoading(false);
      }
    };

    fetchHealthCheck();
  }, []);

  return (
    <div className="app">
      <h1>Health Check</h1>
      {loading && <p>Loading...</p>}
      {error && <p className="error">Error: {error}</p>}
      {healthData && (
        <div className="health-data">
          <div className="health-item">
            <strong>Status:</strong> <span>{healthData.status}</span>
          </div>
          <div className="health-item">
            <strong>Hostname:</strong> <span>{healthData.hostname}</span>
          </div>
          <div className="health-item">
            <strong>Version:</strong> <span>{healthData.version}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
