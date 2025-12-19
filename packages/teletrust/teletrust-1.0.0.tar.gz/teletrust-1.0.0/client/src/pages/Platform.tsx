import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  BookOpen,
  Activity,
  LayoutDashboard,
  Settings,
  Menu,
  LogOut,
  Cpu,
  Lock,
  Network,
  PieChart
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { APAVoiceGuardDemo } from "@/components/demos/APAVoiceGuardDemo";
import { ConsentGuardDemo } from "@/components/demos/ConsentGuardDemo";
import { DashboardDemo } from "@/components/demos/DashboardDemo";
import { ViabilityEngine } from "@/components/demos/ViabilityEngine";

type Module = "dashboard" | "education" | "health" | "validation";

export function Platform() {
  const [activeModule, setActiveModule] = useState<Module>("dashboard");
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-black text-foreground overflow-hidden font-sans selection:bg-primary selection:text-black">
      {/* Sidebar */}
      <motion.div
        initial={false}
        animate={{ width: isSidebarOpen ? 280 : 80 }}
        className="border-r border-white/10 bg-[#050505] flex flex-col z-20"
      >
        <div className="p-6 flex items-center gap-3 border-b border-white/10 h-20">
          <div className="w-8 h-8 bg-primary rounded-sm flex items-center justify-center shrink-0">
            <Cpu className="w-5 h-5 text-black" />
          </div>
          {isSidebarOpen && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="font-display font-bold text-lg tracking-tight"
            >
              SENTINEL<span className="text-primary">_OS</span>
            </motion.div>
          )}
        </div>

        <div className="flex-1 py-6 px-3 space-y-2">
          <NavButton
            active={activeModule === "dashboard"}
            onClick={() => setActiveModule("dashboard")}
            icon={LayoutDashboard}
            label="Command Center"
            isOpen={isSidebarOpen}
          />

          <NavButton
            active={activeModule === "validation"}
            onClick={() => setActiveModule("validation")}
            icon={PieChart}
            label="Viability Proof"
            isOpen={isSidebarOpen}
            badge="INVESTOR"
          />

          <div className="px-4 py-2 mt-6 mb-2 text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
            {isSidebarOpen ? "Active Modules" : "MODS"}
          </div>

          <NavButton
            active={activeModule === "education"}
            onClick={() => setActiveModule("education")}
            icon={BookOpen}
            label="Sentinel Edu (APA)"
            isOpen={isSidebarOpen}
          />
          <NavButton
            active={activeModule === "health"}
            onClick={() => setActiveModule("health")}
            icon={Shield}
            label="Sentinel Health"
            isOpen={isSidebarOpen}
          />

          <div className="px-4 py-2 mt-6 mb-2 text-[10px] font-mono text-muted-foreground uppercase tracking-wider">
            {isSidebarOpen ? "System Core" : "SYS"}
          </div>

          <NavButton
            active={false}
            onClick={() => {}}
            icon={Network}
            label="ESM Topology"
            isOpen={isSidebarOpen}
            badge="ONLINE"
          />
        </div>

        <div className="p-4 border-t border-white/10">
          <Button
            variant="ghost"
            className="w-full justify-start text-muted-foreground hover:text-white"
            onClick={() => setSidebarOpen(!isSidebarOpen)}
          >
            <Menu className="w-5 h-5 mr-2" />
            {isSidebarOpen && "Collapse Menu"}
          </Button>
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#080808] relative">
        <div className="absolute inset-0 grid-pattern opacity-10 pointer-events-none" />

        {/* Header */}
        <header className="h-20 border-b border-white/10 flex items-center justify-between px-8 bg-black/50 backdrop-blur-sm z-10">
          <div className="flex items-center gap-4">
            <h1 className="font-display font-bold text-2xl">
              {activeModule === "dashboard" && "COMMAND_CENTER"}
              {activeModule === "education" && "MODULE: ACADEMIC_AUDIT"}
              {activeModule === "health" && "MODULE: PRIVACY_SHIELD"}
              {activeModule === "validation" && "COMMERCIAL_VALIDATION"}
            </h1>
            <Badge variant="outline" className="font-mono text-xs border-primary/20 text-primary bg-primary/5">
              v2.4.0-STABLE
            </Badge>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right hidden md:block">
              <div className="text-[10px] font-mono text-muted-foreground uppercase">System Status</div>
              <div className="flex items-center justify-end gap-2 text-xs font-bold text-green-500">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                OPERATIONAL
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center border border-white/10">
              <div className="font-display font-bold text-sm">MO</div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="flex-1 overflow-auto p-8 relative z-0">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeModule}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {activeModule === "dashboard" && <DashboardView setActive={setActiveModule} />}
              {activeModule === "validation" && <ViabilityEngine />}
              {activeModule === "education" && (
                <div className="h-full border border-white/10 rounded-lg overflow-hidden shadow-2xl">
                  <APAVoiceGuardDemo />
                </div>
              )}
              {activeModule === "health" && (
                <div className="h-full border border-white/10 rounded-lg overflow-hidden shadow-2xl">
                  <ConsentGuardDemo />
                </div>
              )}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}

function NavButton({ active, onClick, icon: Icon, label, isOpen, badge }: any) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-md transition-all group relative ${
        active
          ? "bg-primary text-black font-bold"
          : "text-muted-foreground hover:bg-white/5 hover:text-white"
      }`}
    >
      <Icon className={`w-5 h-5 ${active ? "text-black" : "text-white/60 group-hover:text-white"}`} />
      {isOpen && (
        <>
          <span className="font-mono text-sm tracking-wide flex-1 text-left">{label}</span>
          {badge && (
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-green-500/20 text-green-500 border border-green-500/30">
              {badge}
            </span>
          )}
        </>
      )}
      {!isOpen && active && (
        <div className="absolute left-0 w-1 h-full bg-primary rounded-r-full" />
      )}
    </button>
  );
}

function DashboardView({ setActive }: { setActive: (mod: Module) => void }) {
  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="p-6 rounded-lg bg-[#111] border border-white/10 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-primary/10 rounded text-primary">
              <Activity className="w-6 h-6" />
            </div>
            <Badge variant="secondary" className="font-mono text-xs">+12.5%</Badge>
          </div>
          <div className="text-4xl font-display font-bold text-white mb-1">98.2%</div>
          <div className="text-sm text-muted-foreground font-mono">Global Compliance Score</div>
        </div>

        <div className="p-6 rounded-lg bg-[#111] border border-white/10 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-blue-500/10 rounded text-blue-500">
              <Network className="w-6 h-6" />
            </div>
            <Badge variant="secondary" className="font-mono text-xs">ONLINE</Badge>
          </div>
          <div className="text-4xl font-display font-bold text-white mb-1">61</div>
          <div className="text-sm text-muted-foreground font-mono">Active Consensus Nodes</div>
        </div>

        <div className="p-6 rounded-lg bg-[#111] border border-white/10 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex justify-between items-start mb-4">
            <div className="p-2 bg-purple-500/10 rounded text-purple-500">
              <Lock className="w-6 h-6" />
            </div>
            <Badge variant="secondary" className="font-mono text-xs">SECURE</Badge>
          </div>
          <div className="text-4xl font-display font-bold text-white mb-1">24/7</div>
          <div className="text-sm text-muted-foreground font-mono">Real-time Monitoring</div>
        </div>
      </div>

      {/* Module Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 h-[400px]">
        <div
          onClick={() => setActive('education')}
          className="group relative rounded-xl border border-white/10 bg-[#0a0a0a] overflow-hidden cursor-pointer hover:border-primary/50 transition-all"
        >
          <div className="absolute inset-0 grid-pattern opacity-10" />
          <div className="p-8 h-full flex flex-col relative z-10">
            <div className="flex justify-between items-start mb-6">
              <div className="p-3 bg-white/5 rounded-lg border border-white/5 group-hover:bg-primary group-hover:text-black transition-colors">
                <BookOpen className="w-8 h-8" />
              </div>
              <Badge variant="outline" className="font-mono text-xs uppercase">Module A</Badge>
            </div>
            <h3 className="text-2xl font-display font-bold mb-2">Sentinel Edu</h3>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-sm">
              Automated academic integrity auditing using multi-source verification (PubMed, OpenAlex).
            </p>

            <div className="mt-auto pt-6 flex items-center gap-4 text-xs font-mono text-white/40">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                APA-7 Engine
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                NLP Audit
              </div>
            </div>
          </div>
        </div>

        <div
          onClick={() => setActive('health')}
          className="group relative rounded-xl border border-white/10 bg-[#0a0a0a] overflow-hidden cursor-pointer hover:border-green-500/50 transition-all"
        >
          <div className="absolute inset-0 grid-pattern opacity-10" />
          <div className="p-8 h-full flex flex-col relative z-10">
            <div className="flex justify-between items-start mb-6">
              <div className="p-3 bg-white/5 rounded-lg border border-white/5 group-hover:bg-green-500 group-hover:text-black transition-colors">
                <Shield className="w-8 h-8" />
              </div>
              <Badge variant="outline" className="font-mono text-xs uppercase">Module B</Badge>
            </div>
            <h3 className="text-2xl font-display font-bold mb-2">Sentinel Health</h3>
            <p className="text-muted-foreground text-sm leading-relaxed max-w-sm">
              Telehealth compliance enforcement with spectral graph topology encryption.
            </p>

            <div className="mt-auto pt-6 flex items-center gap-4 text-xs font-mono text-white/40">
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                HIPAA Mesh
              </div>
              <div className="flex items-center gap-2">
                <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                Real-time Logs
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Validation Link */}
      <div
        onClick={() => setActive('validation')}
        className="p-4 border border-white/10 rounded-lg bg-white/5 hover:bg-white/10 cursor-pointer flex items-center justify-between group transition-all"
      >
        <div className="flex items-center gap-4">
           <div className="p-2 bg-primary/20 text-primary rounded">
             <PieChart className="w-5 h-5" />
           </div>
           <div>
             <div className="font-bold text-white group-hover:text-primary transition-colors">Investor Validation Data</div>
             <div className="text-xs text-muted-foreground">Review commercial viability, TAM/SAM, and competitive moat analysis.</div>
           </div>
        </div>
        <Button size="sm" variant="ghost" className="text-primary">View Report →</Button>
      </div>
    </div>
  );
}
