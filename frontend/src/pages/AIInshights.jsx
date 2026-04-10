import { useState } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000'

export default function AIInsights() {
  const [country, setCountry]   = useState('India')
  const [insight, setInsight]   = useState('')
  const [loading, setLoading]   = useState(false)

  const COUNTRIES = [
    'United States','China','Germany','Japan','United Kingdom',
    'France','India','Italy','South Korea','Canada','Russia',
    'Mexico','Australia','Spain','Indonesia','Netherlands',
    'Saudi Arabia','Turkey','Switzerland','Poland','Belgium',
    'Sweden','Brazil','Argentina','South Africa'
  ]

  function getInsights() {
    setLoading(true)
    setInsight('')

    axios.post(`${API}/api/ai/insights`, { country })
      .then(r => {
        setInsight(r.data.insight)
        setLoading(false)
      })
      .catch(err => {
        setInsight('Failed to get insights. Make sure the API is running.')
        setLoading(false)
      })
  }

  return (
    <div>
      <h1 style={{ fontSize: '28px', fontWeight: 700, marginBottom: '8px' }}>
        AI Trade Insights
      </h1>
      <p style={{ color: '#64748b', marginBottom: '32px' }}>
        Powered by Groq — analyzes trade data and finds business opportunities
      </p>

      {/* Controls */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '32px', alignItems: 'center' }}>
        <select
          value={country}
          onChange={e => setCountry(e.target.value)}
          style={{
            background: '#1e293b', color: '#e2e8f0',
            border: '1px solid #334155', borderRadius: '8px',
            padding: '10px 16px', fontSize: '15px', cursor: 'pointer'
          }}
        >
          {COUNTRIES.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        <button
          onClick={getInsights}
          disabled={loading}
          style={{
            background: loading ? '#334155' : '#0ea5e9',
            color: '#fff', border: 'none', borderRadius: '8px',
            padding: '10px 24px', fontSize: '15px',
            cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600
          }}
        >
          {loading ? 'Analyzing...' : 'Get AI Insights'}
        </button>
      </div>

      {/* Result */}
      {insight && (
        <div style={{
          background: '#1e293b', borderRadius: '12px',
          padding: '32px', border: '1px solid #334155',
          lineHeight: '1.8', fontSize: '15px', color: '#e2e8f0',
          whiteSpace: 'pre-wrap'
        }}>
          {insight}
        </div>
      )}

      {!insight && !loading && (
        <div style={{
          background: '#1e293b', borderRadius: '12px',
          padding: '48px', border: '1px solid #334155',
          textAlign: 'center', color: '#475569'
        }}>
          Select a country and click "Get AI Insights" to analyze trade opportunities
        </div>
      )}
    </div>
  )
}