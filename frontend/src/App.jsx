import { useEffect, useState } from 'react';
import {
  Activity, ArrowDownRight, ArrowRight, BarChart3, Building2, Check,
  ChevronLeft, ChevronRight, CircleHelp, Database, Download, ExternalLink,
  Filter, Globe2, LayoutDashboard, MapPin, Menu, Phone, RefreshCw,
  Search, ShieldCheck, Tags, X
} from 'lucide-react';
import {
  Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const COLORS = ['#5466ea', '#27bba6', '#f4ac54', '#a68bec', '#ef7682', '#62a7e3', '#77c988'];
const EMPTY = { total: 0, real: 0, sample: 0, with_phone: 0, cities: [], categories: [], sources: [] };
const format = (n) => new Intl.NumberFormat('en-IN').format(n || 0);

async function jsonFetch(path, signal) {
  const res = await fetch(`${API_URL}${path}`, { signal });
  if (!res.ok) throw new Error(`API returned ${res.status}. Check the FastAPI server.`);
  return res.json();
}

function SectionHeading({ title, subtitle, action }) {
  return <div className="section-heading"><div><h2>{title}</h2><p>{subtitle}</p></div>{action}</div>;
}
function MiniLegend({ items }) {
  return <div className="custom-legend">{items.map((item, i) => <div className="legend-row" key={item.name}>
    <i style={{background: COLORS[i % COLORS.length]}} />
    <span title={item.name}>{item.name}</span><strong>{format(item.count)}</strong>
  </div>)}</div>;
}
function Panel({ children, className = '' }) {
  return <div className={`panel ${className}`}>{children}</div>;
}
function StatCard({ icon: Icon, title, value, caption, tint }) {
  return <div className="stat-card">
    <div className={`stat-icon ${tint}`}><Icon size={21} strokeWidth={2}/></div>
    <div className="stat-title">{title}</div>
    <strong>{format(value)}</strong>
    <div className="stat-caption">{caption}</div>
  </div>;
}

export default function App() {
  const [stats, setStats] = useState(EMPTY);
  const [rows, setRows] = useState({ total: 0, items: [], limit: 10, offset: 0 });
  const [loading, setLoading] = useState(true);
  const [rowLoading, setRowLoading] = useState(false);
  const [error, setError] = useState('');
  const [filterCity, setFilterCity] = useState('');
  const [filterOrigin, setFilterOrigin] = useState('');
  const [search, setSearch] = useState('');
  const [debounced, setDebounced] = useState('');
  const [page, setPage] = useState(0);
  const [mobileMenu, setMobileMenu] = useState(false);
  const pageSize = 10;

  const refresh = async () => {
    setLoading(true); setError('');
    try { setStats(await jsonFetch('/api/stats')); }
    catch (e) { setError(e.message + ' Start MySQL and FastAPI, then refresh.'); }
    finally { setLoading(false); }
  };
  useEffect(() => { refresh(); }, []);
  useEffect(() => {
    const timeout = setTimeout(() => setDebounced(search), 250);
    return () => clearTimeout(timeout);
  }, [search]);
  useEffect(() => { setPage(0); }, [filterCity, filterOrigin, debounced]);
  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({ limit: String(pageSize), offset: String(page*pageSize) });
    if (filterCity) params.set('city', filterCity);
    if (filterOrigin) params.set('origin', filterOrigin);
    if (debounced) params.set('search', debounced);
    setRowLoading(true);
    jsonFetch(`/api/listings?${params.toString()}`, controller.signal)
      .then(setRows).catch((e) => { if (e.name !== 'AbortError') setError(e.message); })
      .finally(() => { if (!controller.signal.aborted) setRowLoading(false); });
    return () => controller.abort();
  }, [page, filterCity, filterOrigin, debounced, stats.total]);

  const downloadCSV = async () => {
    try {
      const params = new URLSearchParams({ limit: '100', offset: '0' });
      if (filterCity) params.set('city', filterCity);
      if (filterOrigin) params.set('origin', filterOrigin);
      if (debounced) params.set('search', debounced);
      const result = await jsonFetch(`/api/listings?${params}`);
      const cols = ['business_name', 'category', 'city', 'address', 'phone', 'source', 'data_origin'];
      const escape = (x) => `"${String(x ?? '').replaceAll('"', '""')}"`;
      const csv = [cols.join(','), ...result.items.map(x => cols.map(c => escape(x[c])).join(','))].join('\r\n');
      const link = document.createElement('a');
      const url = URL.createObjectURL(new Blob([csv], {type: 'text/csv;charset=utf-8'}));
      link.href = url; link.download = 'business-listings-first-100.csv'; link.click();
      URL.revokeObjectURL(url);
    } catch(e) { setError(e.message); }
  };
  const hasData = stats.total > 0;
  const topCities = stats.cities.slice(0, 8);
  const topCategories = stats.categories.slice(0, 7);
  const sources = stats.sources.slice(0, 7);
  const totalPages = Math.max(1, Math.ceil(rows.total / pageSize));

  return <div className="shell">
    <aside className={`sidebar ${mobileMenu ? 'sidebar-open' : ''}`}>
      <a href="#overview" className="brand" onClick={() => setMobileMenu(false)}>
        <div className="brand-icon"><Building2 size={23}/></div><span>Local<span className="brand-accent">Lens</span><small>DATA INTELLIGENCE</small></span>
      </a>
      <p className="nav-group">WORKSPACE</p>
      <a className="nav-link selected" href="#overview" onClick={() => setMobileMenu(false)}><LayoutDashboard size={18}/> Overview</a>
      <a className="nav-link" href="#listings" onClick={() => setMobileMenu(false)}><Database size={18}/> Business listings</a>
      <a className="nav-link" href="#reports" onClick={() => setMobileMenu(false)}><BarChart3 size={18}/> Analytics</a>
      <div className="sidebar-bottom">
        <div className="side-note"><ShieldCheck size={18}/><span>Source transparency<strong>Real and sample records labeled</strong></span></div>
        <a className="source-link" href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">© OpenStreetMap contributors <ExternalLink size={13}/></a>
      </div>
    </aside>
    <main className="main" id="overview">
      <header className="topbar">
        <div className="top-left"><button className="icon-button mobile-toggle" aria-label="Toggle menu" onClick={() => setMobileMenu(!mobileMenu)}><Menu size={23}/></button>
        <span className="breadcrumb">Workspace</span><ChevronRight size={14} className="faint"/><span className="breadcrumb current">Overview</span></div>
        <div className="top-right"><span className={`connection ${error ? 'offline' : ''}`}><i/>{error ? 'API offline' : 'Dashboard'}</span><button className="refresh-button" onClick={refresh}><RefreshCw size={16} className={loading ? 'rotating' : ''}/> Refresh</button><div className="avatar">BL</div></div>
      </header>
      <div className="content">
        <div className="hero"><div><div className="eyebrow"><span className="eyebrow-dot"/> BUSINESS INTELLIGENCE</div><h1>Business overview <span>✳</span></h1><p>Understand your business landscape at a glance. Explore listings, categories, and cities.</p></div>
          <div className="hero-graphic" aria-hidden="true"><div className="orb orb-one"/><div className="orb orb-two"/><BarChart3 size={66}/></div>
        </div>
        {error && <div className="error-banner"><CircleHelp size={18}/><span>{error}</span><button onClick={() => setError('')} aria-label="Close error"><X size={15}/></button></div>}
        {hasData && stats.sample > 0 && <div className="sample-notice"><CircleHelp size={17}/><span><strong>Sample data included.</strong> {format(stats.sample)} records are fictional practice entries. Replace them with collected real listings before a final real-data claim.</span></div>}
        <div className="stat-grid">
          <StatCard icon={Building2} title="Total businesses" value={stats.total} caption="Records in MySQL" tint="purple" />
          <StatCard icon={MapPin} title="Cities covered" value={stats.cities.length} caption="Unique city locations" tint="green" />
          <StatCard icon={Tags} title="Categories" value={stats.categories.length} caption="Business types" tint="orange" />
          <StatCard icon={Phone} title="With phone numbers" value={stats.with_phone} caption="Public phone fields found" tint="blue" />
        </div>
        <div className="section-pad" id="reports"><SectionHeading title="Analytics overview" subtitle="Visual reports built from your FastAPI and MySQL data."/><div className="charts-grid">
          <Panel className="city-panel"><div className="panel-head"><div><h3>Businesses by city</h3><p>Top 8 cities by number of listings</p></div><div className="panel-icon"><MapPin size={18}/></div></div>
            {hasData ? <div className="chart-space"><ResponsiveContainer width="100%" height="100%"><BarChart data={topCities} margin={{top: 12,right: 12,bottom: 2,left: -20}} barSize={29}><CartesianGrid strokeDasharray="4 5" vertical={false} stroke="#edf1f7"/><XAxis dataKey="name" tick={{fill:'#8490a4',fontSize:11}} tickLine={false} axisLine={false} interval={0} angle={-18} textAnchor="end" height={55}/><YAxis allowDecimals={false} tick={{fill:'#8490a4',fontSize:11}} tickLine={false} axisLine={false}/><Tooltip cursor={{fill:'#f3f6fd'}} formatter={(v) => [format(v),'Businesses']} contentStyle={{border:'1px solid #e9edf4',borderRadius:12}}/><Bar dataKey="count" fill="#5767e9" radius={[7,7,0,0]}/></BarChart></ResponsiveContainer></div> : <EmptyState/>}
          </Panel>
          <Panel className="category-panel"><div className="panel-head"><div><h3>Category distribution</h3><p>Top 7 business categories</p></div><div className="panel-icon"><Tags size={18}/></div></div>
            {hasData ? <div className="pie-area"><div className="pie-chart"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={topCategories} dataKey="count" nameKey="name" cx="50%" cy="50%" innerRadius={63} outerRadius={96} strokeWidth={3} stroke="#fff" paddingAngle={2}>{topCategories.map((d,i) => <Cell key={d.name} fill={COLORS[i % COLORS.length]}/>)}</Pie><Tooltip formatter={(v) => [format(v),'Businesses']}/></PieChart></ResponsiveContainer><div className="pie-center"><span>TOP</span><strong>{topCategories.length}</strong><small>categories</small></div></div><MiniLegend items={topCategories}/></div> : <EmptyState/>}
          </Panel>
          <Panel className="source-panel"><div className="panel-head"><div><h3>Listings by source</h3><p>Where your business information comes from</p></div><div className="panel-icon"><Globe2 size={18}/></div></div>
            {hasData ? <><div className="source-bars">{sources.map((d,i) => <div className="source-item" key={d.name}><div className="source-top"><span>{d.name}</span><strong>{format(d.count)}</strong></div><div className="progress-track"><div style={{width: `${100*d.count/Math.max(stats.total,1)}%`,background:COLORS[i%COLORS.length]}}/></div></div>)}</div><p className="source-detail"><Check size={15}/> {format(stats.real)} real · {format(stats.sample)} sample entries</p></> : <EmptyState/>}
          </Panel>
          <Panel className="insights-panel"><div className="panel-head"><div><h3>Quick insights</h3><p>Highlights from your dataset</p></div><div className="panel-icon"><Activity size={18}/></div></div><div className="insights-body">
            <div className="insight-row"><div className="insight-emoji violet"><Building2 size={18}/></div><span>Leading city<small>{stats.cities[0]?.name || 'No data yet'}</small></span><strong>{format(stats.cities[0]?.count)}</strong></div>
            <div className="insight-row"><div className="insight-emoji mint"><Tags size={18}/></div><span>Top category<small>{stats.categories[0]?.name || 'No data yet'}</small></span><strong>{format(stats.categories[0]?.count)}</strong></div>
            <div className="insight-row"><div className="insight-emoji gold"><Phone size={18}/></div><span>Phone coverage<small>Listings with phone fields</small></span><strong>{stats.total ? Math.round(stats.with_phone/stats.total*100) : 0}%</strong></div>
            <div className="insight-row last"><div className="insight-emoji sky"><ShieldCheck size={18}/></div><span>Real data share<small>Collected entries only</small></span><strong>{stats.total ? Math.round(stats.real/stats.total*100) : 0}%</strong></div>
          </div></Panel>
        </div></div>
        <section className="table-section" id="listings"><SectionHeading title="Business directory" subtitle="Explore stored listings. Search, filter, and export up to 100 matching rows." action={<button className="outline-button" onClick={downloadCSV}><Download size={16}/> Export CSV</button>}/>
          <Panel className="table-panel"><div className="table-controls"><div className="search-field"><Search size={18}/><input aria-label="Search businesses" placeholder="Search business name..." value={search} onChange={e => setSearch(e.target.value)}/></div>
          <div className="filter-group"><Filter size={15}/><select aria-label="City" value={filterCity} onChange={e=>setFilterCity(e.target.value)}><option value="">All cities</option>{stats.cities.map(x=><option key={x.name} value={x.name}>{x.name}</option>)}</select>
          <select aria-label="Origin" value={filterOrigin} onChange={e=>setFilterOrigin(e.target.value)}><option value="">All data</option><option value="real">Real data</option><option value="sample">Sample data</option></select></div></div>
          <div className="table-wrap"><table><thead><tr><th>Business</th><th>Category</th><th>City</th><th>Address</th><th>Phone</th><th>Origin</th></tr></thead><tbody>{rows.items.map(r=><tr key={r.id}>
            <td><div className="business-cell"><div className="business-logo">{r.business_name.slice(0,1).toUpperCase()}</div><span><strong>{r.business_name}</strong><small>{r.source}</small></span></div></td><td><span className="category-pill">{r.category}</span></td><td>{r.city}</td><td className="address-cell" title={r.address}>{r.address}</td><td>{r.phone || <span className="muted">Not listed</span>}</td><td><span className={`origin-pill ${r.data_origin}`}>{r.data_origin}</span></td>
          </tr>)}</tbody></table>{!rowLoading && rows.items.length === 0 && <div className="empty-table">No matching listings. Try changing your filters or importing data.</div>}{rowLoading && <div className="loading-table">Loading listings...</div>}</div>
          <div className="table-footer"><span>Showing {rows.total ? format(page*pageSize+1) : '0'}–{format(Math.min((page+1)*pageSize,rows.total))} of {format(rows.total)} listings</span><div className="pagination"><button aria-label="Previous page" disabled={page===0} onClick={()=>setPage(page-1)}><ChevronLeft size={16}/></button><span>Page {page+1} of {totalPages}</span><button aria-label="Next page" disabled={page+1>=totalPages} onClick={()=>setPage(page+1)}><ChevronRight size={16}/></button></div></div>
        </Panel></section>
        <footer><span>LocalLens · Business Listings Dashboard</span><span>Built with React, FastAPI & MySQL · Data © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noreferrer">OpenStreetMap contributors</a> when applicable</span></footer>
      </div>
    </main>
  </div>;
}
function EmptyState(){return <div className="empty-chart"><Database size={27}/><p>No data yet. Import a CSV to see charts.</p></div>}
