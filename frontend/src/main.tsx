import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom/client'
import './index.css'

interface Underlying {
  id: number
  name: string
  reference_level: number | null
  spot: number | null
  spot_date: string | null
  spot_source: string | null
}

interface Product {
  id: number
  name: string
  isin: string
  issuer: string
  currency: string
  asset_class: string
  market_value: number | null
  valuation_date: string | null
  worst_performance_pct: number | null
  worst_underlying: string | null
  distance_to_strike_pts: number | null
  distance_to_autocall_pts: number | null
  status: string
  missing_fields: string[]
  awaiting_termsheet: boolean
  underlyings: Underlying[]
}

interface DashboardData {
  as_of_date: string
  products: Product[]
  aggregates: {
    total_market_value: number
    product_count: number
  }
}

function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchDashboard()
  }, [])

  const fetchDashboard = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/dashboard')
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard')
      }
      const json = await response.json()
      setData(json)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
      setData(null)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div style={{ padding: '20px' }}>Loading dashboard...</div>
  if (error) return <div style={{ padding: '20px', color: 'red' }}>Error: {error}</div>
  if (!data) return <div style={{ padding: '20px' }}>No data</div>

  return (
    <div style={{ padding: '20px', fontFamily: 'sans-serif' }}>
      <h1>Portfolio Dashboard</h1>
      <p>As of: {data.as_of_date}</p>
      
      <div style={{ marginBottom: '30px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '4px' }}>
        <h2 style={{ margin: '0 0 10px 0' }}>Aggregates</h2>
        <p><strong>Total Market Value:</strong> ${data.aggregates.total_market_value.toLocaleString()}</p>
        <p><strong>Product Count:</strong> {data.aggregates.product_count}</p>
      </div>

      <h2>Structured Products</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
        <thead>
          <tr style={{ backgroundColor: '#f0f0f0', borderBottom: '1px solid #ccc' }}>
            <th style={{ padding: '8px', textAlign: 'left' }}>Name</th>
            <th style={{ padding: '8px', textAlign: 'left' }}>ISIN</th>
            <th style={{ padding: '8px', textAlign: 'right' }}>Market Value</th>
            <th style={{ padding: '8px', textAlign: 'right' }}>Worst Perf %</th>
            <th style={{ padding: '8px', textAlign: 'right' }}>To Strike</th>
            <th style={{ padding: '8px', textAlign: 'right' }}>To Autocall</th>
            <th style={{ padding: '8px', textAlign: 'center' }}>Status</th>
          </tr>
        </thead>
        <tbody>
          {data.products.map((prod) => (
            <tr key={prod.id} style={{ borderBottom: '1px solid #eee' }}>
              <td style={{ padding: '8px' }}>
                <div>{prod.name}</div>
                <div style={{ fontSize: '11px', color: '#666' }}>
                  {prod.worst_underlying || '—'}
                </div>
              </td>
              <td style={{ padding: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
                {prod.isin || '—'}
              </td>
              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace' }}>
                {prod.market_value ? `$${prod.market_value.toLocaleString(undefined, { maximumFractionDigits: 0 })}` : '—'}
              </td>
              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace' }}>
                {prod.worst_performance_pct !== null ? `${prod.worst_performance_pct.toFixed(1)}%` : '—'}
              </td>
              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace', color: prod.distance_to_strike_pts !== null && prod.distance_to_strike_pts < 0 ? 'red' : 'inherit' }}>
                {prod.distance_to_strike_pts !== null ? prod.distance_to_strike_pts.toFixed(1) + ' pts' : '—'}
              </td>
              <td style={{ padding: '8px', textAlign: 'right', fontFamily: 'monospace' }}>
                {prod.distance_to_autocall_pts !== null ? prod.distance_to_autocall_pts.toFixed(1) + ' pts' : '—'}
              </td>
              <td style={{ padding: '8px', textAlign: 'center' }}>
                <span style={{
                  padding: '3px 8px',
                  borderRadius: '3px',
                  fontSize: '11px',
                  fontWeight: 'bold',
                  backgroundColor:
                    prod.status === 'red' ? '#ffcccc' :
                    prod.status === 'orange' ? '#ffe0b2' :
                    prod.status === 'green' ? '#c8e6c9' :
                    prod.status === 'neutral' ? '#e0e0e0' :
                    '#f5f5f5',
                  color:
                    prod.status === 'red' ? '#c62828' :
                    prod.status === 'orange' ? '#e65100' :
                    prod.status === 'green' ? '#2e7d32' :
                    '#666',
                }}>
                  {prod.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {data.products.length === 0 && (
        <div style={{ padding: '20px', color: '#666', textAlign: 'center' }}>
          No products yet. Create one to get started.
        </div>
      )}

      <button onClick={fetchDashboard} style={{ marginTop: '20px', padding: '10px 20px' }}>
        Refresh
      </button>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <Dashboard />
  </React.StrictMode>,
)
