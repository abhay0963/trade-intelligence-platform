import { useState } from 'react'
import Overview from './pages/Overview.jsx'
import Countries from './pages/Countries.jsx'
import Commodities from './pages/Commodities.jsx'
import AIInsights from './pages/AIInsights.jsx'
import Compare from './pages/Compare.jsx'

const PAGES = ['Overview', 'Countries', 'Compare', 'Commodities', 'AI Insights']

export default function App() {
  const [activePage, setActivePage] = useState('Overview')

  function renderPage() {
    if (activePage === 'Overview')    return <Overview />
    if (activePage === 'Countries')   return <Countries />
    if (activePage === 'Compare')     return <Compare />
    if (activePage === 'Commodities') return <Commodities />
    if (activePage === 'AI Insights') return <AIInsights />
  }

  return (
    <div style={{ minHeight: '100vh' }}>
      <nav style={{ background: '#1e293b', padding: '0 32px', display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid #334155', height: '56px' }}>
        <span style={{ fontSize: '18px', fontWeight: 700, color: '#38bdf8', marginRight: '32px' }}>
          🌍 TradeIQ
        </span>
        {PAGES.map(page => (
          <button
            key={page}
            onClick={() => setActivePage(page)}
            style={{
              background:   activePage === page ? '#0ea5e9' : 'transparent',
              color:        activePage === page ? '#fff' : '#94a3b8',
              border:       'none', borderRadius: '6px',
              padding:      '6px 16px', cursor: 'pointer',
              fontSize:     '14px', fontWeight: activePage === page ? 600 : 400
            }}
          >
            {page}
          </button>
        ))}
      </nav>
      <main style={{ padding: '32px' }}>
        {renderPage()}
      </main>
    </div>
  )
}
