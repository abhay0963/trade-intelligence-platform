import { useEffect, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'

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

function fmt(val, type) {
  if (!val) return 'N/A'
  if (type === 'trillion') return `$${(val/1e12).toFixed(2)}T`
  if (type === 'billion')  return `$${(val/1e9).toFixed(1)}B`
  if (type === 'percent')  return `${Number(val).toFixed(1)}%`
  if (type === 'dollar')   return `$${Number(val).toLocaleString()}`
  return val
}

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{ background: '#0f172a', borderRadius: '10px', padding: '18px', border: '1px solid #1e293b' }}>
      <p style={{ color: '#475569', fontSize: '11px', textTransform: 'uppercase', marginBottom: '6px' }}>{label}</p>
      <p style={{ fontSize: '22px', fontWeight: 700, color: color || '#e2e8f0' }}>{value}</p>
      {sub && <p style={{ color: '#475569', fontSize: '11px', marginTop: '4px' }}>{sub}</p>}
    </div>
  )
}

export default function Countries() {
  const [selected, setSelected] = useState('IND')
  const [profile, setProfile]   = useState(null)
  const [loading, setLoading]   = useState(false)

  useEffect(() => {
    setLoading(true)
    setProfile(null)
    axios.get(`${API}/api/countries/${selected}/profile`)
      .then(r => { setProfile(r.data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [selected])

  const ind = profile?.indicators || {}

  // Merge GDP and trade trends for combined chart
  const tradeChart = (profile?.gdp_trend || []).map((g, i) => ({
    year:    g.year,
    GDP:     g.value / 1e12,
    Exports: (profile?.exports_trend[i]?.value || 0) / 1e12,
    Imports: (profile?.imports_trend[i]?.value || 0) / 1e12,
  }))

  return (
    <div>
      <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '20px' }}>Country Profile</h1>

      {/* Country selector */}
      <select
        value={selected}
        onChange={e => setSelected(e.target.value)}
        style={{ background: '#1e293b', color: '#e2e8f0', border: '1px solid #334155', borderRadius: '8px', padding: '10px 16px', fontSize: '15px', marginBottom: '28px', cursor: 'pointer', width: '260px' }}
      >
        {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
      </select>

      {loading && <p style={{ color: '#94a3b8' }}>Loading country data...</p>}

      {profile && !loading && (
        <>
          {/* Key indicators */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '24px' }}>
            <StatCard label="GDP" value={fmt(ind['GDP (current US$)']?.value, 'trillion')} color="#38bdf8" sub={`Year: ${ind['GDP (current US$)']?.year}`} />
            <StatCard label="GDP Per Capita" value={fmt(ind['GDP Per Capita (US$)']?.value, 'dollar')} color="#a78bfa" />
            <StatCard label="Total Exports" value={fmt(ind['Total Exports (US$)']?.value, 'billion')} color="#34d399" />
            <StatCard label="Total Imports" value={fmt(ind['Total Imports (US$)']?.value, 'billion')} color="#fb923c" />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '28px' }}>
            <StatCard label="Trade Balance" value={fmt(ind['Trade Balance (US$)']?.value, 'billion')} color={ind['Trade Balance (US$)']?.value > 0 ? '#34d399' : '#f87171'} />
            <StatCard label="Inflation Rate" value={fmt(ind['Inflation Rate (%)']?.value, 'percent')} color="#facc15" />
            <StatCard label="Unemployment" value={fmt(ind['Unemployment Rate (%)']?.value, 'percent')} color="#fb923c" />
            <StatCard label="Trade % of GDP" value={fmt(ind['Trade as % of GDP']?.value, 'percent')} color="#38bdf8" />
          </div>

          {/* Trade trend chart */}
          <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155', marginBottom: '24px' }}>
            <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', marginBottom: '20px' }}>
              GDP vs Exports vs Imports (Trillion USD) — 2015 to 2023
            </p>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={tradeChart}>
                <XAxis dataKey="year" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} tickFormatter={v => `$${v.toFixed(1)}T`} />
                <Tooltip formatter={v => [`$${Number(v).toFixed(2)}T`]} contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                <Legend />
                <Line type="monotone" dataKey="GDP"     stroke="#38bdf8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Exports" stroke="#34d399" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="Imports" stroke="#f87171" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Top exports and imports */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
              <p style={{ color: '#34d399', fontSize: '12px', textTransform: 'uppercase', marginBottom: '16px' }}>
                Top 5 Exports
              </p>
              {(profile.top_exports || []).map((p, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 0', borderBottom: '1px solid #0f172a' }}>
                  <span style={{ color: '#34d399', fontWeight: 700, fontSize: '13px', minWidth: '20px' }}>#{i+1}</span>
                  <span style={{ color: '#e2e8f0', fontSize: '14px' }}>{p}</span>
                </div>
              ))}
            </div>

            <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
              <p style={{ color: '#f87171', fontSize: '12px', textTransform: 'uppercase', marginBottom: '16px' }}>
                Top 5 Imports
              </p>
              {(profile.top_imports || []).map((p, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 0', borderBottom: '1px solid #0f172a' }}>
                  <span style={{ color: '#f87171', fontWeight: 700, fontSize: '13px', minWidth: '20px' }}>#{i+1}</span>
                  <span style={{ color: '#e2e8f0', fontSize: '14px' }}>{p}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
