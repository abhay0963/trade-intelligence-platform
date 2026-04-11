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

function formatInsight(text) {
  return text.split('\n').map((line, i) => {
    const trimmed = line.trim()
    if (!trimmed) return <div key={i} style={{ height: '10px' }} />
    if (trimmed.match(/^#{1,3}\s/) || trimmed.match(/^\d+\.\s+[A-Z]/)) {
      return <p key={i} style={{ fontSize: '18px', fontWeight: 700, color: '#38bdf8', margin: '24px 0 8px', borderBottom: '1px solid #1e3a5f', paddingBottom: '6px' }}>
        {trimmed.replace(/^#{1,3}\s+/, '').replace(/\*\*/g, '')}
      </p>
    }
    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      return <p key={i} style={{ fontSize: '15px', fontWeight: 600, color: '#f1f5f9', margin: '14px 0 4px' }}>
        {trimmed.replace(/\*\*/g, '')}
      </p>
    }
    if (trimmed.match(/^\*\*.+\*\*/)) {
      const parts = trimmed.split(/\*\*/)
      return <p key={i} style={{ fontSize: '14px', color: '#cbd5e1', margin: '6px 0' }}>
        {parts.map((part, j) => j % 2 === 1
          ? <strong key={j} style={{ color: '#f1f5f9' }}>{part}</strong>
          : part
        )}
      </p>
    }
    if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.startsWith('* ')) {
      return <p key={i} style={{ fontSize: '14px', color: '#94a3b8', margin: '5px 0', paddingLeft: '20px', display: 'flex', gap: '8px' }}>
        <span style={{ color: '#0ea5e9', flexShrink: 0 }}>→</span>
        <span>{trimmed.slice(2)}</span>
      </p>
    }
    return <p key={i} style={{ fontSize: '14px', color: '#cbd5e1', margin: '5px 0', lineHeight: '1.7' }}>{trimmed}</p>
  })
}

export default function AIInsights() {
  const [selected, setSelected] = useState('IND')
  const [insight, setInsight]   = useState('')
  const [loading, setLoading]   = useState(false)
  const [profile, setProfile]   = useState(null)

  function analyze() {
    setLoading(true)
    setInsight('')
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
      .then(r => { setInsight(r.data.insight); setLoading(false) })
      .catch(() => { setInsight('Failed to get insights. Make sure the API is running.'); setLoading(false) })
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid #334155' }}>
            <span style={{ background: '#0ea5e9', borderRadius: '6px', padding: '4px 12px', fontSize: '12px', fontWeight: 600, color: '#fff' }}>AI Analysis</span>
            <span style={{ color: '#64748b', fontSize: '13px' }}>{countryName}</span>
            <span style={{ color: '#334155', fontSize: '12px', marginLeft: 'auto' }}>Powered by Groq · Llama 3.3 70B</span>
          </div>
          <div>{formatInsight(insight)}</div>
        </div>
      )}
    </div>
  )
}
