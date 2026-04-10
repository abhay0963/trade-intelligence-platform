import { useState } from 'react'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'

const COUNTRIES = [
  {code:'USA',name:'United States'},{code:'CHN',name:'China'},{code:'DEU',name:'Germany'},
  {code:'JPN',name:'Japan'},{code:'GBR',name:'United Kingdom'},{code:'FRA',name:'France'},
  {code:'IND',name:'India'},{code:'ITA',name:'Italy'},{code:'KOR',name:'South Korea'},
  {code:'CAN',name:'Canada'},{code:'RUS',name:'Russia'},{code:'MEX',name:'Mexico'},
  {code:'AUS',name:'Australia'},{code:'ESP',name:'Spain'},{code:'IDN',name:'Indonesia'},
  {code:'NLD',name:'Netherlands'},{code:'SAU',name:'Saudi Arabia'},{code:'TUR',name:'Turkey'},
  {code:'CHE',name:'Switzerland'},{code:'POL',name:'Poland'},{code:'BEL',name:'Belgium'},
  {code:'SWE',name:'Sweden'},{code:'BRA',name:'Brazil'},{code:'ARG',name:'Argentina'},
  {code:'ZAF',name:'South Africa'}
]

export default function AIInsights() {
  const [selected, setSelected] = useState('IND')
  const [insight, setInsight]   = useState('')
  const [loading, setLoading]   = useState(false)
  const [profile, setProfile]   = useState(null)

  function analyze() {
    setLoading(true)
    setInsight('')

    // First fetch the country profile so Groq has real data
    axios.get(`${API}/api/countries/${selected}/profile`)
      .then(r => {
        setProfile(r.data)
        const countryName = COUNTRIES.find(c => c.code === selected)?.name
        return axios.post(`${API}/api/ai/insights`, {
          country:      countryName,
          country_code: selected,
          indicators:   r.data.indicators,
          top_exports:  r.data.top_exports,
          top_imports:  r.data.top_imports
        })
      })
      .then(r => {
        setInsight(r.data.insight)
        setLoading(false)
      })
      .catch(() => {
        setInsight('Failed to get insights. Make sure the API is running.')
        setLoading(false)
      })
  }

  const countryName = COUNTRIES.find(c => c.code === selected)?.name

  return (
    <div>
      <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '4px' }}>AI Trade Intelligence</h1>
      <p style={{ color: '#64748b', marginBottom: '28px', fontSize: '14px' }}>
        Powered by Groq (Llama 3.3 70B) — analyzes real trade data and generates business intelligence
      </p>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '28px', alignItems: 'center' }}>
        <select
          value={selected}
          onChange={e => setSelected(e.target.value)}
          style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', borderRadius: '8px', padding: '10px 16px', fontSize: '15px', cursor: 'pointer' }}
        >
          {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>

        <button
          onClick={analyze}
          disabled={loading}
          style={{ background: loading ? '#334155' : '#0ea5e9', color: '#fff', border: 'none', borderRadius: '8px', padding: '10px 28px', fontSize: '15px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: 600 }}
        >
          {loading ? 'Analyzing...' : `Analyze ${countryName}`}
        </button>
      </div>

      {!insight && !loading && (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '48px', border: '1px solid #334155', textAlign: 'center' }}>
          <p style={{ color: '#475569', fontSize: '15px', marginBottom: '8px' }}>Select a country and click Analyze</p>
          <p style={{ color: '#334155', fontSize: '13px' }}>Groq will analyze GDP, exports, imports, inflation, unemployment and generate business opportunities</p>
        </div>
      )}

      {insight && (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '32px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #334155' }}>
            <span style={{ background: '#0ea5e9', borderRadius: '6px', padding: '4px 10px', fontSize: '12px', fontWeight: 600 }}>AI Analysis</span>
            <span style={{ color: '#64748b', fontSize: '13px' }}>{countryName}</span>
          </div>
          <div style={{ lineHeight: '1.8', fontSize: '15px', color: '#e2e8f0', whiteSpace: 'pre-wrap' }}>
            {insight}
          </div>
        </div>
      )}
    </div>
  )
}
