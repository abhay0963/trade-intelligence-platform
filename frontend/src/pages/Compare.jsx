import { useEffect, useState } from 'react'
import axios from 'axios'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend, BarChart, Bar } from 'recharts'

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
  if (!val && val !== 0) return 'N/A'
  if (type === 'trillion') return `$${(val/1e12).toFixed(2)}T`
  if (type === 'billion')  return `$${(val/1e9).toFixed(1)}B`
  if (type === 'percent')  return `${Number(val).toFixed(1)}%`
  if (type === 'dollar')   return `$${Number(val).toLocaleString()}`
  return val
}

export default function Compare() {
  const [countryA, setCountryA] = useState('IND')
  const [countryB, setCountryB] = useState('CHN')
  const [profileA, setProfileA] = useState(null)
  const [profileB, setProfileB] = useState(null)
  const [loading, setLoading]   = useState(false)

  function loadProfiles() {
    setLoading(true)
    Promise.all([
      axios.get(`${API}/api/countries/${countryA}/profile`),
      axios.get(`${API}/api/countries/${countryB}/profile`)
    ]).then(([a, b]) => {
      setProfileA(a.data)
      setProfileB(b.data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }

  useEffect(() => { loadProfiles() }, [])

  // Build combined GDP chart data
  const gdpChart = []
  if (profileA && profileB) {
    const yearsA = {}
    profileA.gdp_trend.forEach(r => yearsA[r.year] = r.value)
    profileB.gdp_trend.forEach(r => {
      gdpChart.push({
        year:  r.year,
        [COUNTRIES.find(c=>c.code===countryA)?.name]: (yearsA[r.year] || 0) / 1e12,
        [COUNTRIES.find(c=>c.code===countryB)?.name]: r.value / 1e12,
      })
    })
  }

  const nameA = COUNTRIES.find(c=>c.code===countryA)?.name
  const nameB = COUNTRIES.find(c=>c.code===countryB)?.name

  // Key indicators to compare
  const INDICATORS = [
    { key: 'GDP (current US$)',    label: 'GDP',           type: 'trillion' },
    { key: 'GDP Per Capita (US$)', label: 'GDP Per Capita',type: 'dollar'   },
    { key: 'Total Exports (US$)',  label: 'Exports',       type: 'billion'  },
    { key: 'Total Imports (US$)',  label: 'Imports',       type: 'billion'  },
    { key: 'Trade Balance (US$)',  label: 'Trade Balance', type: 'billion'  },
    { key: 'Inflation Rate (%)',   label: 'Inflation',     type: 'percent'  },
    { key: 'Unemployment Rate (%)',label: 'Unemployment',  type: 'percent'  },
    { key: 'Trade as % of GDP',    label: 'Trade/GDP',     type: 'percent'  },
  ]

  return (
    <div>
      <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '4px' }}>Compare Countries</h1>
      <p style={{ color: '#64748b', marginBottom: '28px', fontSize: '14px' }}>
        Side by side economic comparison of any two countries
      </p>

      {/* Country selectors */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '28px', alignItems: 'center' }}>
        <select
          value={countryA}
          onChange={e => setCountryA(e.target.value)}
          style={{ background: '#1e293b', color: '#38bdf8', border: '1px solid #38bdf8', borderRadius: '8px', padding: '10px 16px', fontSize: '15px', cursor: 'pointer' }}
        >
          {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>

        <span style={{ color: '#475569', fontSize: '18px', fontWeight: 700 }}>vs</span>

        <select
          value={countryB}
          onChange={e => setCountryB(e.target.value)}
          style={{ background: '#1e293b', color: '#f87171', border: '1px solid #f87171', borderRadius: '8px', padding: '10px 16px', fontSize: '15px', cursor: 'pointer' }}
        >
          {COUNTRIES.map(c => <option key={c.code} value={c.code}>{c.name}</option>)}
        </select>

        <button
          onClick={loadProfiles}
          style={{ background: '#0ea5e9', color: '#fff', border: 'none', borderRadius: '8px', padding: '10px 24px', fontSize: '15px', cursor: 'pointer', fontWeight: 600 }}
        >
          Compare
        </button>
      </div>

      {loading && <p style={{ color: '#94a3b8' }}>Loading...</p>}

      {profileA && profileB && !loading && (
        <>
          {/* Indicator comparison table */}
          <div style={{ background: '#1e293b', borderRadius: '12px', border: '1px solid #334155', marginBottom: '24px', overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', background: '#0f172a', padding: '14px 20px' }}>
              <span style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase' }}>Indicator</span>
              <span style={{ color: '#38bdf8', fontSize: '13px', fontWeight: 600, textAlign: 'center' }}>{nameA}</span>
              <span style={{ color: '#f87171', fontSize: '13px', fontWeight: 600, textAlign: 'center' }}>{nameB}</span>
            </div>
            {INDICATORS.map((ind, i) => {
              const valA = profileA.indicators[ind.key]?.value
              const valB = profileB.indicators[ind.key]?.value
              return (
                <div key={ind.key} style={{
                  display: 'grid', gridTemplateColumns: '1fr 1fr 1fr',
                  padding: '12px 20px',
                  background: i % 2 === 0 ? 'transparent' : '#0f172a22',
                  borderTop: '1px solid #1e293b'
                }}>
                  <span style={{ color: '#64748b', fontSize: '13px' }}>{ind.label}</span>
                  <span style={{ color: '#38bdf8', fontWeight: 600, textAlign: 'center', fontSize: '14px' }}>{fmt(valA, ind.type)}</span>
                  <span style={{ color: '#f87171', fontWeight: 600, textAlign: 'center', fontSize: '14px' }}>{fmt(valB, ind.type)}</span>
                </div>
              )
            })}
          </div>

          {/* GDP trend comparison chart */}
          <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155', marginBottom: '24px' }}>
            <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', marginBottom: '20px' }}>
              GDP Trend Comparison (Trillion USD)
            </p>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={gdpChart}>
                <XAxis dataKey="year" stroke="#475569" fontSize={11} />
                <YAxis stroke="#475569" fontSize={11} tickFormatter={v => `$${v.toFixed(1)}T`} />
                <Tooltip formatter={v => [`$${Number(v).toFixed(2)}T`]} contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
                <Legend />
                <Line type="monotone" dataKey={nameA} stroke="#38bdf8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey={nameB} stroke="#f87171" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Top exports/imports side by side */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
            {[{profile: profileA, name: nameA, color: '#38bdf8'}, {profile: profileB, name: nameB, color: '#f87171'}].map(({profile, name, color}) => (
              <div key={name} style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: `1px solid ${color}22` }}>
                <p style={{ color, fontSize: '13px', fontWeight: 600, marginBottom: '16px' }}>{name}</p>
                <p style={{ color: '#34d399', fontSize: '11px', textTransform: 'uppercase', marginBottom: '10px' }}>Top Exports</p>
                {profile.top_exports.map((p, i) => (
                  <div key={i} style={{ display: 'flex', gap: '8px', padding: '6px 0', borderBottom: '1px solid #0f172a' }}>
                    <span style={{ color, fontWeight: 700, fontSize: '12px', minWidth: '18px' }}>#{i+1}</span>
                    <span style={{ color: '#e2e8f0', fontSize: '13px' }}>{p}</span>
                  </div>
                ))}
                <p style={{ color: '#f87171', fontSize: '11px', textTransform: 'uppercase', margin: '16px 0 10px' }}>Top Imports</p>
                {profile.top_imports.map((p, i) => (
                  <div key={i} style={{ display: 'flex', gap: '8px', padding: '6px 0', borderBottom: '1px solid #0f172a' }}>
                    <span style={{ color: '#f87171', fontWeight: 700, fontSize: '12px', minWidth: '18px' }}>#{i+1}</span>
                    <span style={{ color: '#e2e8f0', fontSize: '13px' }}>{p}</span>
                  </div>
                ))}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}