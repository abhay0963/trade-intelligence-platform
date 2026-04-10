import { useEffect, useState } from 'react'
import axios from 'axios'

const API = 'http://127.0.0.1:8000'
const COLORS = ['#38bdf8','#a78bfa','#34d399','#fb923c','#f472b6','#facc15','#818cf8','#4ade80','#f87171']
const GOLD_COLORS = ['#facc15','#94a3b8','#fb923c']

function PriceCard({ item, color }) {
  return (
    <div style={{ background: '#1e293b', borderRadius: '12px', padding: '24px', border: `1px solid ${color}22` }}>
      <p style={{ color: '#475569', fontSize: '12px', marginBottom: '6px' }}>{item.symbol}</p>
      <p style={{ fontSize: '15px', fontWeight: 600, marginBottom: '12px', color: '#e2e8f0' }}>{item.commodity_name}</p>
      <p style={{ fontSize: '32px', fontWeight: 700, color }}>${Number(item.price).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
      <p style={{ color: '#475569', fontSize: '11px', marginTop: '8px' }}>{item.unit} · {item.price_date}</p>
    </div>
  )
}

export default function Commodities() {
  const [commodities, setCommodities] = useState([])
  const [metals, setMetals]           = useState([])

  useEffect(() => {
    axios.get(`${API}/api/commodities`)
      .then(r => {
        setCommodities(r.data.commodities || [])
        setMetals(r.data.precious_metals || [])
      })
  }, [])

  return (
    <div>
      <h1 style={{ fontSize: '26px', fontWeight: 700, marginBottom: '4px' }}>Commodities & Precious Metals</h1>
      <p style={{ color: '#64748b', marginBottom: '28px', fontSize: '14px' }}>Live prices from Alpha Vantage and ExchangeRate API</p>

      {metals.length > 0 && (
        <>
          <p style={{ color: '#facc15', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
            Precious Metals
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
            {metals.map((m, i) => <PriceCard key={m.symbol} item={m} color={GOLD_COLORS[i]} />)}
          </div>
        </>
      )}

      {metals.length === 0 && (
        <div style={{ background: '#1e293b', borderRadius: '12px', padding: '20px', border: '1px solid #334155', marginBottom: '24px' }}>
          <p style={{ color: '#475569', fontSize: '14px' }}>
            Gold & Silver prices refresh daily. Alpha Vantage free tier (25 requests/day) was used by other data today. Check back tomorrow.
          </p>
        </div>
      )}

      <p style={{ color: '#94a3b8', fontSize: '12px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '16px' }}>
        Commodities
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
        {commodities.map((c, i) => <PriceCard key={c.symbol} item={c} color={COLORS[i % COLORS.length]} />)}
      </div>

      {commodities.length === 0 && (
        <p style={{ color: '#475569', fontSize: '14px' }}>Commodity prices refresh daily. Check back tomorrow.</p>
      )}
    </div>
  )
}
