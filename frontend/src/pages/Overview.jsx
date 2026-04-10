import { useEffect, useState } from 'react'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const API = 'http://127.0.0.1:8000'

function StatCard({ label, value, color = '#38bdf8' }) {
  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
      <p style={{ color: '#64748b', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '8px' }}>{label}</p>
      <p style={{ fontSize: '28px', fontWeight: 700, color }}>{value}</p>
    </div>
  )
}

export default function Overview() {
  const [top10, setTop10]           = useState([])
  const [commodities, setCommodities] = useState([])
  const [metals, setMetals]         = useState([])
  const [forex, setForex]           = useState([])
  const [loading, setLoading]       = useState(true)

  useEffect(() => {
    Promise.all([
      axios.get(`${API}/api/gdp/top10`),
      axios.get(`${API}/api/commodities`),
      axios.get(`${API}/api/forex`)
    ]).then(([g, c, f]) => {
      setTop10(g.data.rankings || [])
      setCommodities(c.data.commodities || [])
      setMetals(c.data.precious_metals || [])
      setForex(f.data.rates || [])
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  if (loading) return <p style={{ color: '#94a3b8', padding: '40px' }}>Loading live data...</p>

  const totalGDP = top10.reduce((s, c) => s + c.gdp_usd, 0)

  return (
    <div>
      <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '4px' }}>Global Trade Overview</h1>
      <p style={{ color: '#64748b', marginBottom: '28px', fontSize: '14px' }}>
        Live economic data — World Bank, Alpha Vantage, ExchangeRate API
      </p>

      {/* Summary cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px', marginBottom: '28px' }}>
        <StatCard label="Countries Tracked" value="25" color="#38bdf8" />
        <StatCard label="Commodities" value={commodities.length + metals.length} color="#a78bfa" />
        <StatCard label="Currencies" value={forex.length} color="#34d399" />
        <StatCard label="Combined GDP (Top 10)" value={`$${(totalGDP/1e12).toFixed(0)}T`} color="#fb923c" />
      </div>

      {/* Top 10 GDP bar chart */}
      <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155', marginBottom: '24px' }}>
        <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '20px' }}>
          Top 10 Economies by GDP (2023)
        </p>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={top10} layout="vertical" margin={{ left: 20 }}>
            <XAxis type="number" stroke="#475569" tickFormatter={v => `$${(v/1e12).toFixed(1)}T`} fontSize={11} />
            <YAxis type="category" dataKey="country" stroke="#475569" fontSize={12} width={120} />
            <Tooltip formatter={v => [`$${(v/1e12).toFixed(2)}T`, 'GDP']} contentStyle={{ background: '#0f172a', border: '1px solid #334155' }} />
            <Bar dataKey="gdp_usd" radius={[0, 4, 4, 0]}>
              {top10.map((_, i) => <Cell key={i} fill={i === 0 ? '#38bdf8' : i === 1 ? '#60a5fa' : '#3b82f6'} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Commodities + metals */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '24px' }}>

        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
          <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
            Commodity Prices
          </p>
          {commodities.map(c => (
            <div key={c.symbol} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #0f172a' }}>
              <span style={{ color: '#94a3b8', fontSize: '14px' }}>{c.commodity_name}</span>
              <span style={{ color: '#f8fafc', fontWeight: 600, fontSize: '14px' }}>${Number(c.price).toFixed(2)}</span>
            </div>
          ))}
        </div>

        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
          <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
            Precious Metals & Forex
          </p>
          {metals.map(m => (
            <div key={m.symbol} style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #0f172a' }}>
              <span style={{ color: '#facc15', fontSize: '14px' }}>{m.commodity_name}</span>
              <span style={{ color: '#f8fafc', fontWeight: 600, fontSize: '14px' }}>${Number(m.price).toLocaleString()}</span>
            </div>
          ))}
          {metals.length === 0 && (
            <p style={{ color: '#475569', fontSize: '13px' }}>Refreshes daily — check back tomorrow</p>
          )}
          <div style={{ marginTop: '12px' }}>
            {forex.slice(0, 6).map(f => (
              <div key={f.currency_code} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid #0f172a' }}>
                <span style={{ color: '#94a3b8', fontSize: '14px' }}>{f.currency_code}/USD</span>
                <span style={{ color: '#f8fafc', fontSize: '14px' }}>{f.rate_vs_usd}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Forex grid */}
      <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: '1px solid #334155' }}>
        <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
          Live Exchange Rates vs USD
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px' }}>
          {forex.map(f => (
            <div key={f.currency_code} style={{ background: '#0f172a', borderRadius: '8px', padding: '12px', textAlign: 'center' }}>
              <p style={{ color: '#38bdf8', fontWeight: 700, fontSize: '14px' }}>{f.currency_code}</p>
              <p style={{ color: '#e2e8f0', fontSize: '13px', marginTop: '4px' }}>{f.rate_vs_usd}</p>
              <p style={{ color: '#475569', fontSize: '11px' }}>{f.currency_name}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
