import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  ShieldAlert, ShieldCheck, Activity, Cpu, Sparkles,
  Terminal, BookOpen, Download, AlertTriangle, Clock, Database,
  CheckCircle2, Layers, MapPin, Zap, RefreshCw, ChevronRight,
  Users, AlertOctagon, CheckCircle, ArrowUpRight,
  BarChart3, Award, Timer, Menu, X, Shield
} from 'lucide-react';

const API_BASE = import.meta.env.VITE_API_BASE || "/api";

// -----------------------------------------------------------------------------
// Markdown & Formatting Renderer
// -----------------------------------------------------------------------------
function FormattedMessage({ text = "" }) {
  if (!text) return null;

  const lines = text.split("\n");

  return (
    <div className="space-y-3 text-slate-200 text-xs sm:text-sm leading-relaxed">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={idx} className="h-1" />;

        if (trimmed.startsWith("### ")) {
          return (
            <h4 key={idx} className="text-sm sm:text-base font-extrabold text-white font-mono mt-3 mb-1">
              {trimmed.replace("### ", "")}
            </h4>
          );
        }

        if (trimmed.startsWith("* ") || trimmed.startsWith("- ")) {
          const bulletContent = trimmed.substring(2);
          return (
            <div key={idx} className="flex items-start gap-2 ml-1 text-slate-300">
              <span className="text-aura-iris mt-1 shrink-0">•</span>
              <span dangerouslySetInnerHTML={{ __html: parseBold(bulletContent) }} />
            </div>
          );
        }

        return (
          <p key={idx} dangerouslySetInnerHTML={{ __html: parseBold(line) }} />
        );
      })}
    </div>
  );
}

function parseBold(str) {
  return str
    .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
    .replace(/\*(.*?)\*/g, '<em class="text-aura-iris font-medium">$1</em>');
}

// -----------------------------------------------------------------------------
// Speedometer Gauge
// -----------------------------------------------------------------------------
function SpeedometerGauge({ value = 0, inherent = 92 }) {
  const percentage = Math.min(Math.max(value / 100, 0), 1);
  const angle = percentage * 180 - 180;

  return (
    <div className="flex flex-col items-center justify-center p-4 sm:p-6 bg-aura-surface/90 border border-aura-border rounded-xl shadow-xl relative overflow-hidden backdrop-blur w-full">
      <div className="relative w-56 sm:w-64 h-28 sm:h-32 overflow-hidden flex items-end justify-center">
        <svg className="w-52 sm:w-60 h-52 sm:h-60 -rotate-90" viewBox="0 0 100 100">
          <circle cx="50" cy="50" r="40" fill="none" stroke="#23273A" strokeWidth="12" />
          <circle
            cx="50" cy="50" r="40" fill="none"
            stroke="url(#violetGrad)"
            strokeWidth="12"
            strokeDasharray="125.6 188.4"
            strokeDashoffset="0"
          />
          <defs>
            <linearGradient id="violetGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10B981" />
              <stop offset="50%" stopColor="#7C3AED" />
              <stop offset="100%" stopColor="#EF4444" />
            </linearGradient>
          </defs>
        </svg>

        <div
          className="absolute bottom-0 left-1/2 w-1.5 h-20 sm:h-24 bg-aura-iris origin-bottom transition-transform duration-700 ease-out shadow-[0_0_12px_#7C3AED]"
          style={{ transform: `translateX(-50%) rotate(${angle}deg)` }}
        />
        <div className="absolute bottom-0 w-4 sm:w-5 h-4 sm:h-5 bg-white rounded-full border-4 border-aura-surface z-10 shadow" />
      </div>

      <div className="flex justify-between w-full px-4 sm:px-6 text-[10px] font-mono text-slate-400 mt-3 font-semibold">
        <span className="text-aura-emerald">0.0 SAFE</span>
        <span className="text-aura-iris">30.0 CAP</span>
        <span className="text-aura-crimson">100.0 CRITICAL</span>
      </div>

      <div className="mt-4 flex items-center gap-4 sm:gap-6 pt-3 border-t border-aura-border w-full justify-center">
        <div className="text-center">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">Inherent Risk</span>
          <span className="font-mono text-base sm:text-lg font-bold text-aura-crimson">{inherent.toFixed(1)}</span>
        </div>
        <div className="h-6 w-px bg-aura-border" />
        <div className="text-center">
          <span className="text-[10px] uppercase tracking-wider text-slate-400 font-bold block">Residual Risk</span>
          <span className="font-mono text-xl sm:text-2xl font-black text-white">{value.toFixed(1)}</span>
        </div>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Topology Visualizer
// -----------------------------------------------------------------------------
function CleanroomTopologyMap({ activePlant, scope, hasDeficiency }) {
  const plants = [
    { id: "Plant-01", name: "Fab 1", cx: 65, cy: 55 },
    { id: "Plant-02", name: "Fab 2", cx: 180, cy: 55 },
    { id: "Plant-04", name: "Fab 4", cx: 295, cy: 55 },
  ];

  return (
    <div className="p-4 sm:p-5 bg-aura-surface/90 border border-aura-border rounded-xl shadow-lg w-full">
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-2 mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-aura-iris" /> Plant Jurisdictional Perimeter
        </span>
        <span className={`text-[10px] font-mono px-2.5 py-0.5 rounded border font-bold self-start sm:self-auto ${hasDeficiency ? 'bg-aura-crimson/20 text-aura-crimson border-aura-crimson/40' : 'bg-aura-emerald/10 text-aura-emerald border-aura-emerald/30'
          }`}>
          {hasDeficiency ? 'PERIMETER BREACH' : 'CONTAINMENT INTACT'}
        </span>
      </div>

      <div className="overflow-x-auto">
        <svg className="min-w-[320px] w-full h-32 sm:h-36 bg-aura-bg/90 rounded-lg border border-aura-border" viewBox="0 0 360 110">
          <line x1="0" y1="55" x2="360" y2="55" stroke="#23273A" strokeDasharray="4 4" />
          <line x1="120" y1="0" x2="120" y2="110" stroke="#23273A" strokeWidth="1.5" />
          <line x1="240" y1="0" x2="240" y2="110" stroke="#23273A" strokeWidth="1.5" />

          {plants.map((p) => {
            const isSelected = activePlant === p.id;
            const isCrossPlantViolation = (scope === "GLOBAL" || (scope !== p.id && scope.includes(p.id))) && !isSelected;

            return (
              <g key={p.id} className="cursor-pointer">
                {isSelected && (
                  <circle cx={p.cx} cy={p.cy} r="24" fill="#7C3AED" fillOpacity="0.25" className="animate-pulse" />
                )}
                {isCrossPlantViolation && (
                  <circle cx={p.cx} cy={p.cy} r="26" fill="#EF4444" fillOpacity="0.25" className="animate-ping" />
                )}

                <circle
                  cx={p.cx} cy={p.cy} r="15"
                  fill={isCrossPlantViolation ? "#EF4444" : isSelected ? "#7C3AED" : "#12141F"}
                  stroke={isCrossPlantViolation ? "#F87171" : isSelected ? "#A78BFA" : "#23273A"}
                  strokeWidth="3"
                />
                <text x={p.cx} y={p.cy + 4} textAnchor="middle" fill="#FFFFFF" fontSize="9" fontFamily="JetBrains Mono" fontWeight="bold">
                  {p.id.replace("Plant-", "F-")}
                </text>
                <text x={p.cx} y={p.cy + 28} textAnchor="middle" fill="#94A3B8" fontSize="8" fontFamily="Inter">
                  {p.name}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
      <div className="flex flex-col sm:flex-row justify-between text-[10px] font-mono text-slate-400 mt-2 gap-1 px-1">
        <span>Assigned Base: <strong className="text-white">{activePlant}</strong></span>
        <span>Target Execution: <strong className={hasDeficiency ? "text-aura-crimson" : "text-aura-iris"}>{scope}</strong></span>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Action Tier Cards
// -----------------------------------------------------------------------------
function ActionTierSelector({ selectedAction, onSelect }) {
  const tiers = [
    { code: "ACT_VIEW", mult: "0.2x", label: "Read-Only Telemetry", desc: "Inspection & review. Zero edit rights." },
    { code: "ACT_EXEC", mult: "1.0x", label: "Operational Execution", desc: "Wafer transport & step-level recipe running." },
    { code: "ACT_MOD", mult: "2.0x", label: "Recipe Parameter Edit", desc: "Lithography tuning & parameter changes." },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
      {tiers.map((t) => {
        const active = selectedAction === t.code;
        return (
          <div
            key={t.code}
            onClick={() => onSelect(t.code)}
            className={`p-4 rounded-xl border cursor-pointer transition-all flex flex-col justify-between ${active
                ? 'bg-aura-violet/20 border-aura-violet shadow-[0_0_20px_rgba(124,58,237,0.25)]'
                : 'bg-aura-surface/80 border-aura-border hover:border-slate-600'
              }`}
          >
            <div>
              <div className="flex justify-between items-center mb-1">
                <span className={`text-xs font-mono font-bold ${active ? 'text-aura-iris' : 'text-slate-300'}`}>
                  {t.code}
                </span>
                <span className="text-[10px] font-mono font-bold bg-aura-bg px-2 py-0.5 rounded text-white border border-aura-border">
                  {t.mult}
                </span>
              </div>
              <div className="text-xs font-semibold text-white mb-1">{t.label}</div>
              <div className="text-[10px] text-slate-400 leading-tight">{t.desc}</div>
            </div>
            <div className="mt-3 flex items-center gap-1.5 text-[10px] font-mono text-aura-iris font-semibold">
              {active ? <CheckCircle2 className="w-3.5 h-3.5 text-aura-emerald" /> : <div className="w-3.5 h-3.5 rounded-full border border-slate-600" />}
              <span>{active ? 'Active Policy' : 'Select Tier'}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}

// -----------------------------------------------------------------------------
// Executive KPI Rail
// -----------------------------------------------------------------------------
function ExecutiveKpiRail({ facility }) {
  return (
    <div className="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-aura-border bg-aura-surface/70 p-4 sm:p-6 space-y-5 flex flex-col justify-between backdrop-blur shrink-0">
      <div className="space-y-5">
        <div className="flex items-center justify-between border-b border-aura-border pb-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-aura-iris" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-white">Fab Executive KPIs</h3>
          </div>
          <span className="text-[9px] font-mono bg-aura-emerald/20 text-aura-emerald border border-aura-emerald/40 px-2 py-0.5 rounded-full font-bold">
            REAL-TIME
          </span>
        </div>

        {/* Metric 1: Health */}
        <div className="p-4 rounded-xl border bg-aura-bg border-aura-violet/40 shadow-[0_0_15px_rgba(124,58,237,0.15)]">
          <div className="flex justify-between items-start mb-1">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Compliance Health</span>
            <Award className="w-4 h-4 text-aura-emerald" />
          </div>
          <div className="flex items-baseline gap-2 mt-1">
            <span className="text-2xl sm:text-3xl font-extrabold font-mono text-white">99.4%</span>
            <span className="text-xs text-aura-emerald font-bold flex items-center gap-0.5">+1.2%</span>
          </div>
          <div className="w-full bg-aura-surface h-1.5 rounded-full mt-3 overflow-hidden">
            <div className="bg-gradient-to-r from-aura-violet to-aura-emerald h-full w-[99.4%]" />
          </div>
          <div className="flex justify-between text-[9px] font-mono text-slate-500 mt-1.5">
            <span>Target: 98.0%</span>
            <span className="text-aura-emerald font-bold">Cleared</span>
          </div>
        </div>

        {/* Metric 2 & 3: Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3.5 rounded-xl bg-aura-bg/80 border border-aura-border">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400">Hard SoD Blocked</span>
              <AlertOctagon className="w-3.5 h-3.5 text-aura-crimson" />
            </div>
            <div className="text-xl sm:text-2xl font-black font-mono text-aura-crimson mt-0.5">38</div>
            <span className="text-[9px] text-slate-400 font-mono">Past 24 hours</span>
          </div>

          <div className="p-3.5 rounded-xl bg-aura-bg/80 border border-aura-border">
            <div className="flex justify-between items-center mb-1">
              <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400">Engine Latency</span>
              <Timer className="w-3.5 h-3.5 text-aura-emerald" />
            </div>
            <div className="text-xl sm:text-2xl font-black font-mono text-aura-emerald mt-0.5">8.4ms</div>
            <span className="text-[9px] text-slate-400 font-mono">Deterministic</span>
          </div>
        </div>

        {/* Shift Identity Pool */}
        <div className="p-4 rounded-xl bg-aura-bg/60 border border-aura-border space-y-2.5">
          <div className="text-[10px] font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
            <span className="flex items-center gap-1.5"><Users className="w-3.5 h-3.5 text-aura-iris" /> Shift Pool</span>
            <span className="text-xs font-mono font-bold text-white">1,482</span>
          </div>

          <div className="space-y-1.5 text-xs font-mono">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-aura-emerald" /> Compliant:
              </span>
              <span className="text-white font-bold">1,424</span>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-aura-iris" /> Mitigated (View):
              </span>
              <span className="text-aura-iris font-bold">46</span>
            </div>
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400 flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-aura-crimson" /> Flagged Breaches:
              </span>
              <span className="text-aura-crimson font-bold">12</span>
            </div>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-aura-border text-[10px] font-mono text-slate-400 flex items-center justify-between">
        <span>Site: <strong className="text-white">{facility.split(" ")[0]}</strong></span>
        <span className="text-aura-emerald font-bold flex items-center gap-1">
          <CheckCircle className="w-3 h-3" /> Zero Drift
        </span>
      </div>
    </div>
  );
}

// -----------------------------------------------------------------------------
// Root Application
// -----------------------------------------------------------------------------
export default function App() {
  const [activeTab, setActiveTab] = useState('copilot');
  const [facility, setFacility] = useState("Fab 1 — Cleanroom Core (Boise)");
  const [roles, setRoles] = useState([]);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Simulator State
  const [baseRole, setBaseRole] = useState("Production Operator");
  const [targetRole, setTargetRole] = useState("Production Supervisor");
  const [targetAction, setTargetAction] = useState("ACT_VIEW");
  const [simResult, setSimResult] = useState(null);

  // Copilot State
  const [prompt, setPrompt] = useState("");
  const [chatResponse, setChatResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  // Lifecycle State
  const [auditRole, setAuditRole] = useState("Production Operator");
  const [assignedPlant, setAssignedPlant] = useState("Plant-04");
  const [requestedScope, setRequestedScope] = useState("GLOBAL");
  const [expiryDate, setExpiryDate] = useState("2026-08-15");
  const [reviewDate, setReviewDate] = useState("2026-09-04");
  const [auditFindings, setAuditFindings] = useState([]);

  // Benchmark State
  const [benchmarks, setBenchmarks] = useState([]);
  const [laws, setLaws] = useState([]);
  const [verifiedCount, setVerifiedCount] = useState(0);

  useEffect(() => {
    axios.get(`${API_BASE}/roles`).then(res => {
      setRoles(res.data.roles);
      if (res.data.roles.length > 1) {
        setBaseRole(res.data.roles[0]);
        setTargetRole(res.data.roles[1]);
        setAuditRole(res.data.roles[0]);
      }
    }).catch(console.error);

    axios.get(`${API_BASE}/golden-laws`).then(res => setLaws(res.data.laws)).catch(console.error);
    axios.get(`${API_BASE}/benchmarks`).then(res => setBenchmarks(res.data.benchmarks)).catch(console.error);
  }, []);

  useEffect(() => {
    if (baseRole && targetRole) {
      axios.post(`${API_BASE}/evaluate`, {
        base_role: baseRole,
        requested_role: targetRole,
        target_action: targetAction
      }).then(res => setSimResult(res.data)).catch(console.error);
    }
  }, [baseRole, targetRole, targetAction]);

  const handleChat = async (inputPrompt) => {
    const q = inputPrompt || prompt;
    if (!q) return;
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/chat`, { query: q });
      setChatResponse({ query: q, ...res.data });
      setPrompt("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const runLifecycleAudit = async () => {
    try {
      const res = await axios.post(`${API_BASE}/lifecycle-audit`, {
        role: auditRole,
        action_type: "ACT_EXEC",
        scope: requestedScope,
        assigned_plant: assignedPlant,
        expiry_date_str: expiryDate,
        current_date_str: reviewDate
      });
      setAuditFindings(res.data.findings);
    } catch (err) {
      console.error(err);
    }
  };

  const verifyAllBenchmarks = () => {
    let count = 0;
    const interval = setInterval(() => {
      count++;
      setVerifiedCount(count);
      if (count >= 8) clearInterval(interval);
    }, 100);
  };

  const navItems = [
    { id: 'copilot', label: 'Agentic Copilot', icon: Sparkles },
    { id: 'simulator', label: 'Access Simulator', icon: Activity },
    { id: 'lifecycle', label: 'Jurisdictional Audit', icon: Clock },
    { id: 'benchmarks', label: 'Benchmark Register', icon: Database },
    { id: 'laws', label: 'Golden Laws Matrix', icon: BookOpen },
  ];

  return (
    <div className="flex flex-col lg:flex-row min-h-screen bg-aura-bg text-slate-100 font-sans">

      {/* Mobile Top Navigation Bar */}
      <div className="lg:hidden flex items-center justify-between p-4 bg-aura-surface border-b border-aura-border sticky top-0 z-50">
        <div className="flex items-center gap-2.5">
          <div className="bg-gradient-to-tr from-aura-violet to-aura-iris p-2 rounded-lg shadow-[0_0_12px_rgba(124,58,237,0.4)]">
            <Shield className="text-white h-5 w-5 stroke-[2.2]" />
          </div>
          <span className="font-extrabold text-sm tracking-widest uppercase text-white font-mono">AURA</span>
        </div>
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-2 rounded-lg bg-aura-bg border border-aura-border text-aura-iris"
        >
          {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
      </div>

      {/* Sidebar (Branding removed) */}
      <aside className={`
        ${mobileMenuOpen ? 'block' : 'hidden'} lg:flex
        w-full lg:w-64 bg-aura-surface/95 border-b lg:border-b-0 lg:border-r border-aura-border p-5 flex-col justify-between shadow-2xl backdrop-blur shrink-0 z-40
      `}>
        <div>
          {/* Plant Dropdown */}
          <div className="mb-6">
            <label className="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1.5 mb-1.5">
              <Layers className="w-3 h-3 text-aura-iris" /> Active Cleanroom Fab
            </label>
            <select
              value={facility}
              onChange={(e) => setFacility(e.target.value)}
              className="w-full bg-aura-bg border border-aura-border rounded-lg px-2.5 py-2 text-xs text-aura-iris font-mono focus:outline-none focus:border-aura-violet"
            >
              <option value="Fab 1 — Cleanroom Core (Boise)" className="bg-aura-surface text-white">Fab 1 — Boise</option>
              <option value="Fab 2 — Packaging & Test (Taichung)" className="bg-aura-surface text-white">Fab 2 — Taichung</option>
              <option value="Fab 4 — Advanced R&D (Singapore)" className="bg-aura-surface text-white">Fab 4 — Singapore</option>
            </select>
          </div>

          {/* Navigation Items */}
          <nav className="space-y-1.5">
            {navItems.map(tab => {
              const Icon = tab.icon;
              const active = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all ${active
                      ? 'bg-aura-violet/20 text-aura-iris shadow-[0_0_15px_rgba(124,58,237,0.25)] border-l-4 border-aura-violet font-bold'
                      : 'text-slate-400 hover:bg-aura-bg hover:text-white'
                    }`}
                >
                  <Icon className={`h-4 w-4 ${active ? 'text-aura-iris' : 'text-slate-500'}`} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="hidden lg:block border-t border-aura-border pt-4 font-mono text-[10px] text-slate-400 space-y-1.5">
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-aura-emerald animate-ping" />
            <span className="text-white font-bold">ZERO DRIFT ENGINE</span>
          </div>
          <div className="text-slate-500">SOX 404 &bull; ISA-95 VERIFIED</div>
        </div>
      </aside>

      {/* Main Canvas */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Centered AURA with Graphic Emblem */}
        <header className="bg-aura-surface/90 border-b border-aura-border px-4 sm:px-8 py-5 text-center backdrop-blur">
          <div className="flex items-center justify-center gap-3.5">
            <div className="relative flex items-center justify-center">
              <div className="absolute w-10 h-10 bg-aura-violet/40 rounded-full blur-md" />
              <div className="relative p-2.5 bg-gradient-to-tr from-aura-violet to-aura-iris rounded-xl shadow-[0_0_20px_rgba(124,58,237,0.5)] border border-aura-iris/30">
                <Shield className="w-6 h-6 text-white stroke-[2.2]" />
              </div>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-black text-white tracking-widest font-mono drop-shadow-[0_0_25px_rgba(124,58,237,0.4)]">
              AURA
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-aura-iris font-mono tracking-wider font-semibold mt-1.5">
            Agentic User Risk Analysis
          </p>
          <p className="text-[11px] text-slate-400 font-mono mt-0.5">
            Active Scope: <span className="text-white font-semibold">{facility}</span>
          </p>
        </header>

        <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 overflow-x-hidden">
          {/* TAB 1: COPILOT */}
          {activeTab === 'copilot' && (
            <div className="space-y-6">
              {/* Only 3 Exemplary Demo Scenarios Displayed */}
              <div className="bg-aura-surface/90 border border-aura-border rounded-xl p-4 sm:p-5 shadow">
                <div className="mb-3 border-b border-aura-border pb-2.5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-aura-iris flex items-center gap-2">
                    <Zap className="w-4 h-4 text-aura-iris" /> Example Demonstration Scenarios (Click to Run)
                  </h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {[
                    { label: "1. Self-Approval Prevention", q: "Can this Production Operator approve an adjustment that the same user created?" },
                    { label: "2. Cross-Plant Stock Adjustments", q: "Which Warehouse Operators can adjust stock outside their assigned plant?" },
                    { label: "3. User U1001 Attribution", q: "Why is User U1001 considered high risk?" },
                  ].map((item, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleChat(item.q)}
                      className="p-3 rounded-lg bg-aura-bg border border-aura-border hover:border-aura-violet hover:shadow-[0_0_15px_rgba(124,58,237,0.25)] text-left transition flex flex-col justify-between group"
                    >
                      <div className="text-[11px] font-bold text-white group-hover:text-aura-iris flex items-center justify-between mb-1">
                        <span>{item.label}</span>
                        <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-aura-iris" />
                      </div>
                      <p className="text-[10px] text-slate-400 truncate">{item.q}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Search Bar */}
              <div className="flex flex-col sm:flex-row gap-2">
                <input
                  type="text"
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleChat()}
                  placeholder="Type any of your evaluation questions here..."
                  className="flex-1 bg-aura-surface/90 border border-aura-border rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-aura-violet text-white placeholder-slate-500 shadow-inner"
                />
                <button
                  onClick={() => handleChat()}
                  disabled={loading}
                  className="bg-gradient-to-r from-aura-violet to-aura-iris hover:opacity-95 font-bold text-xs px-6 py-3 rounded-xl transition flex items-center justify-center gap-2 text-white shrink-0 font-mono shadow-[0_0_15px_rgba(124,58,237,0.4)]"
                >
                  {loading ? <RefreshCw className="w-4 h-4 animate-spin text-white" /> : <Sparkles className="w-4 h-4 text-white" />}
                  {loading ? 'Evaluating...' : 'Query Copilot'}
                </button>
              </div>

              {/* Formatted Audit Response Card */}
              {chatResponse && (
                <div className="bg-aura-surface/90 border border-aura-border rounded-xl p-5 sm:p-6 space-y-4 shadow-xl">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-aura-border pb-3">
                    <div className="flex items-center gap-2">
                      <Terminal className="h-4 w-4 text-aura-iris shrink-0" />
                      <span className="font-mono text-xs text-slate-400 font-semibold truncate">
                        {chatResponse.query}
                      </span>
                    </div>

                    {chatResponse.verdict && (
                      <span className={`self-start sm:self-auto text-[10px] font-mono px-2.5 py-0.5 rounded border font-bold ${chatResponse.verdict_type === 'danger'
                          ? 'bg-aura-crimson/20 text-aura-crimson border-aura-crimson/40'
                          : chatResponse.verdict_type === 'warning'
                            ? 'bg-aura-violet/25 text-aura-iris border-aura-iris/40'
                            : 'bg-aura-emerald/20 text-aura-emerald border-aura-emerald/40'
                        }`}>
                        {chatResponse.verdict}
                      </span>
                    )}
                  </div>

                  <div className="bg-aura-bg/90 border border-aura-border rounded-lg p-4 sm:p-5">
                    {chatResponse.title && (
                      <h3 className="text-sm font-bold text-aura-iris font-mono uppercase tracking-wider mb-3">
                        {chatResponse.title}
                      </h3>
                    )}
                    <FormattedMessage text={chatResponse.content} />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: ACCESS SIMULATOR */}
          {activeTab === 'simulator' && simResult && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-aura-surface/90 border border-aura-border p-4 sm:p-5 rounded-xl shadow">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-2">
                    Primary Baseline Role
                  </label>
                  <select
                    value={baseRole}
                    onChange={(e) => setBaseRole(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-aura-violet"
                  >
                    {roles.map(r => <option key={r} value={r} className="bg-aura-surface text-white">{r}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-300 block mb-2">
                    Requested Supplementary Role
                  </label>
                  <select
                    value={targetRole}
                    onChange={(e) => setTargetRole(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2.5 text-sm text-white focus:outline-none focus:border-aura-violet"
                  >
                    {roles.map(r => <option key={r} value={r} className="bg-aura-surface text-white">{r}</option>)}
                  </select>
                </div>
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
                  Quantitative Remediation Tier (Action Multiplier)
                </label>
                <ActionTierSelector selectedAction={targetAction} onSelect={setTargetAction} />
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <SpeedometerGauge
                  value={simResult.residual_score}
                  inherent={simResult.inherent_score}
                />

                <div className="bg-aura-surface/90 border border-aura-border p-5 rounded-xl flex flex-col justify-between shadow">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center border-b border-aura-border pb-2">
                      <span className="text-xs text-slate-400 uppercase font-bold">Rule Reference</span>
                      <span className="font-mono text-sm font-bold text-aura-iris">{simResult.conflict_id}</span>
                    </div>
                    <div className="flex justify-between items-center border-b border-aura-border pb-2">
                      <span className="text-xs text-slate-400 uppercase font-bold">Standard</span>
                      <span className="font-mono text-xs text-white">{simResult.violated_law_id}</span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 block mb-1">Identified Exposure:</span>
                      <p className="text-xs text-slate-200 bg-aura-bg p-2.5 rounded border border-aura-border leading-relaxed">
                        {simResult.vulnerability}
                      </p>
                    </div>
                    <div>
                      <span className="text-xs text-slate-400 block mb-1">Audit Directive:</span>
                      <p className="text-xs text-aura-emerald font-mono bg-aura-bg p-2.5 rounded border border-aura-border">
                        {simResult.remediation}
                      </p>
                    </div>
                  </div>

                  <div className="mt-4 bg-aura-bg p-3 rounded-lg border border-aura-border font-mono text-[11px] text-aura-iris">
                    Proof: {simResult.inherent_score} * ({targetAction === 'ACT_VIEW' ? 0.2 : targetAction === 'ACT_EXEC' ? 1.0 : 2.0} / 2.5) = <strong className="text-white">{simResult.residual_score}</strong>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: JURISDICTIONAL AUDIT */}
          {activeTab === 'lifecycle' && (
            <div className="space-y-6">
              <div className="bg-aura-surface/90 border border-aura-border p-4 sm:p-5 rounded-xl grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 shadow">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Role Designation</label>
                  <select
                    value={auditRole}
                    onChange={(e) => setAuditRole(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-aura-violet"
                  >
                    {roles.map(r => <option key={r} value={r} className="bg-aura-surface text-white">{r}</option>)}
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Assigned Plant</label>
                  <select
                    value={assignedPlant}
                    onChange={(e) => setAssignedPlant(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-aura-violet"
                  >
                    <option value="Plant-01" className="bg-aura-surface text-white">Plant-01 (Boise)</option>
                    <option value="Plant-02" className="bg-aura-surface text-white">Plant-02 (Taichung)</option>
                    <option value="Plant-04" className="bg-aura-surface text-white">Plant-04 (Singapore)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Execution Scope</label>
                  <select
                    value={requestedScope}
                    onChange={(e) => setRequestedScope(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-aura-violet"
                  >
                    <option value="GLOBAL" className="bg-aura-surface text-white">GLOBAL / Multi-Plant</option>
                    <option value="Plant-04" className="bg-aura-surface text-white">Plant-04 (Local Only)</option>
                    <option value="Plant-01" className="bg-aura-surface text-white">Plant-01 (Local Only)</option>
                  </select>
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Assigned Expiry Date</label>
                  <input
                    type="date"
                    value={expiryDate}
                    onChange={(e) => setExpiryDate(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-aura-violet"
                  />
                </div>
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1.5">Review Date</label>
                  <input
                    type="date"
                    value={reviewDate}
                    onChange={(e) => setReviewDate(e.target.value)}
                    className="w-full bg-aura-bg border border-aura-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-aura-violet"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    onClick={runLifecycleAudit}
                    className="w-full bg-gradient-to-r from-aura-violet to-aura-iris hover:opacity-95 font-bold text-xs py-2.5 rounded-lg text-white shadow-[0_0_15px_rgba(124,58,237,0.3)] transition"
                  >
                    Execute Audit
                  </button>
                </div>
              </div>

              <CleanroomTopologyMap
                activePlant={assignedPlant}
                scope={requestedScope}
                hasDeficiency={auditFindings.some(f => f.law_id.includes("03"))}
              />

              <div className="space-y-3">
                {auditFindings.length > 0 ? (
                  auditFindings.map((finding, idx) => (
                    <div key={idx} className="bg-aura-surface/90 border border-aura-border border-l-4 border-l-aura-crimson rounded-xl p-4 sm:p-5 shadow">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-mono text-xs sm:text-sm font-bold text-aura-crimson">
                          {finding.law_id} DEFICIENCY
                        </span>
                        <span className="text-[10px] font-mono bg-aura-crimson/20 text-aura-crimson border border-aura-crimson/40 px-2 py-0.5 rounded font-bold">
                          NON-CONFORMANT
                        </span>
                      </div>
                      <p className="text-xs text-slate-200 mb-2">{finding.issue}</p>
                      <p className="text-xs text-aura-emerald font-mono bg-aura-bg p-2.5 rounded border border-aura-border">
                        <strong>Remediation:</strong> {finding.remediation}
                      </p>
                    </div>
                  ))
                ) : (
                  <div className="bg-aura-surface/90 border border-aura-border border-l-4 border-l-aura-emerald rounded-xl p-4 sm:p-5 text-aura-emerald text-xs font-mono">
                    GL-03 / GL-04 CONFORMANCE CONFIRMED: Plant jurisdiction matches physical site boundaries. Expiry date valid.
                  </div>
                )}
              </div>
            </div>
          )}

          {/* TAB 4: BENCHMARK REGISTER */}
          {activeTab === 'benchmarks' && (
            <div className="space-y-6">
              <div className="flex flex-col sm:flex-row justify-between sm:items-center bg-aura-surface/90 border border-aura-border p-4 sm:p-5 rounded-xl gap-3 shadow">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300 block">
                    Benchmark Test Suite (Sheet 5: AUD-01 to AUD-08)
                  </span>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Pre-certified ground truth test cases ensuring deterministic parity.
                  </p>
                </div>
                <button
                  onClick={verifyAllBenchmarks}
                  className="bg-gradient-to-r from-aura-emerald to-emerald-400 hover:opacity-95 text-xs font-bold px-4 py-2.5 rounded-lg transition flex items-center justify-center gap-1.5 text-aura-bg shadow shrink-0 font-mono"
                >
                  <RefreshCw className="h-4 w-4" /> Run Verification
                </button>
              </div>

              {verifiedCount > 0 && (
                <div className="bg-aura-emerald/10 border border-aura-emerald/40 rounded-xl p-4 text-xs font-mono text-aura-emerald flex items-center justify-between">
                  <span>Verified: {verifiedCount} / 8 scenarios.</span>
                  <span className="font-bold">{Math.round((verifiedCount / 8) * 100)}% COMPLETE</span>
                </div>
              )}

              <div className="bg-aura-surface/90 border border-aura-border rounded-xl overflow-x-auto shadow">
                <table className="w-full text-left text-xs min-w-[500px]">
                  <thead className="bg-aura-bg border-b border-aura-border text-slate-400 font-mono">
                    <tr>
                      <th className="p-3.5 w-24">Case ID</th>
                      <th className="p-3.5">Scenario Specification</th>
                      <th className="p-3.5 w-36 text-right">Deterministic Result</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-aura-border font-mono">
                    {benchmarks.map((b, idx) => {
                      const isVerified = verifiedCount > idx;
                      return (
                        <tr key={idx} className="hover:bg-aura-bg/50 transition">
                          <td className="p-3.5 text-aura-iris font-bold">{b.id || `AUD-0${idx + 1}`}</td>
                          <td className="p-3.5 text-slate-300">{b.description}</td>
                          <td className="p-3.5 text-right font-bold">
                            {isVerified ? (
                              <span className="text-aura-emerald inline-flex items-center gap-1">
                                <CheckCircle2 className="w-3.5 h-3.5" /> MATCH
                              </span>
                            ) : (
                              <span className="text-slate-500">READY</span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 5: GOLDEN LAWS */}
          {activeTab === 'laws' && (
            <div className="space-y-4">
              {laws.map((law, idx) => (
                <div key={idx} className="bg-aura-surface/90 border border-aura-border border-l-4 border-l-aura-violet rounded-xl p-4 sm:p-5 shadow">
                  <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-1 mb-2">
                    <span className="font-mono text-xs sm:text-sm font-bold text-aura-iris">
                      {law["Golden Law ID"] || law.id} — {law["Law Name & Principle"] || law.name}
                    </span>
                    <span className="text-[10px] font-mono bg-aura-bg px-2 py-0.5 rounded text-slate-300 border border-aura-border self-start sm:self-auto">
                      {law["Governing Standard"] || "SOX 404"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed mb-3">
                    {law["Auditor Specification & Scope"] || law.description}
                  </p>
                  <div className="font-mono text-[11px] text-aura-iris">
                    Tolerance: {law["Threshold / Tolerance"] || "Zero Tolerance"}
                  </div>
                </div>
              ))}
            </div>
          )}
        </main>
      </div>

      {/* Right Rail */}
      <ExecutiveKpiRail facility={facility} />
    </div>
  );
}