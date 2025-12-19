import { useState, useEffect, useMemo } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Shield, Lock, Activity, Server, Wifi } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface Alert {
  id: number;
  type: "CRITICAL" | "WARNING" | "INFO";
  message: string;
  timestamp: string;
  nodeId: number;
}

// Generate mesh topology (implementation details proprietary)
const NODES = Array.from({ length: 24 }, (_, i) => ({
  id: i,
  type: i < 4 ? 'CORE' : 'EDGE',
  x: Math.random() * 100,
  y: Math.random() * 100,
}));

export function ConsentGuardDemo() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [complianceScore, setComplianceScore] = useState(98.2);
  const [activeNode, setActiveNode] = useState<number | null>(null);

  useEffect(() => {
    const mockAlerts = [
      { msg: "TELEHEALTH_CONSENT_MISSING", type: "CRITICAL" },
      { msg: "HIPAA_FLAG: UNENCRYPTED_ID", type: "WARNING" },
      { msg: "SESSION_INIT_SUCCESS", type: "INFO" },
      { msg: "KEY_ROTATION_COMPLETE", type: "INFO" },
      { msg: "AUDIT_LOG_SYNC", type: "INFO" }
    ];

    const interval = setInterval(() => {
      if (Math.random() > 0.6) {
        const randomAlert = mockAlerts[Math.floor(Math.random() * mockAlerts.length)];
        const nodeId = Math.floor(Math.random() * 61);

        setActiveNode(nodeId);
        setTimeout(() => setActiveNode(null), 500);

        const newAlert: Alert = {
          id: Date.now(),
          type: randomAlert.type as any,
          message: randomAlert.msg,
          timestamp: new Date().toLocaleTimeString(),
          nodeId
        };

        setAlerts(prev => [newAlert, ...prev].slice(0, 7));

        if (randomAlert.type === "CRITICAL") setComplianceScore(prev => Math.max(80, prev - 1.2));
        if (randomAlert.type === "INFO") setComplianceScore(prev => Math.min(100, prev + 0.1));
      }
    }, 1500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-[600px] bg-[#050505] text-foreground font-sans flex flex-col selection:bg-green-500/30">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-green-500/10 rounded-md border border-green-500/20">
            <Shield className="w-4 h-4 text-green-500" />
          </div>
          <div>
            <h2 className="font-display font-bold text-sm tracking-wide">CONSENT_GUARD // MONITOR</h2>
            <div className="text-[10px] font-mono text-muted-foreground flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              ENCRYPTION ACTIVE • MESH TOPOLOGY
            </div>
          </div>
        </div>
        <div className="flex gap-4">
           <div className="text-right">
             <div className="text-[10px] font-mono text-muted-foreground uppercase">Global Compliance</div>
             <div className={`text-lg font-bold font-mono ${complianceScore > 95 ? 'text-green-500' : 'text-yellow-500'}`}>
               {complianceScore.toFixed(2)}%
             </div>
           </div>
        </div>
      </div>

      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-hidden">
        {/* Visualization Panel (2/3 width) */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <Card className="flex-1 bg-black/40 border-white/10 relative overflow-hidden group">
            <div className="absolute inset-0 grid-pattern opacity-20" />

            {/* Network Topology Visualization */}
            <div className="absolute inset-0 p-8">
              <div className="w-full h-full relative">
                {/* Connecting Lines (Decorational) */}
                <svg className="absolute inset-0 w-full h-full opacity-20 pointer-events-none">
                  <line x1="10%" y1="50%" x2="90%" y2="50%" stroke="currentColor" strokeWidth="1" />
                  <line x1="50%" y1="10%" x2="50%" y2="90%" stroke="currentColor" strokeWidth="1" />
                  <circle cx="50%" cy="50%" r="30%" fill="none" stroke="currentColor" strokeWidth="1" />
                </svg>

                {/* Nodes */}
                {NODES.map((node) => {
                  const isActive = activeNode === node.id;
                  // Simple grid layout for demo purposes to look organized
                  const isCore = node.type === 'CORE';
                  const left = isCore ? 45 + Math.random() * 10 : node.x;
                  const top = isCore ? 45 + Math.random() * 10 : node.y;

                  return (
                    <motion.div
                      key={node.id}
                      className={`absolute rounded-full transition-all duration-300 ${
                        isCore ? 'w-3 h-3 z-20' : 'w-1.5 h-1.5 z-10'
                      }`}
                      style={{
                        left: `${left}%`,
                        top: `${top}%`,
                        backgroundColor: isActive ? '#ef4444' : isCore ? '#22c55e' : '#ffffff30',
                        boxShadow: isActive ? '0 0 10px #ef4444' : 'none'
                      }}
                      animate={{
                        scale: isActive ? 1.5 : 1,
                      }}
                    />
                  );
                })}

                {/* Central Pulse */}
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                   <div className="w-32 h-32 border border-green-500/20 rounded-full animate-[ping_3s_linear_infinite]" />
                   <div className="w-48 h-48 border border-green-500/10 rounded-full animate-[ping_4s_linear_infinite] absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
                </div>
              </div>
            </div>

            {/* Overlay Stats */}
            <div className="absolute bottom-4 left-4 z-20">
               <div className="flex items-center gap-2 text-xs font-mono text-white/50 bg-black/50 backdrop-blur px-2 py-1 rounded border border-white/5">
                 <Server className="w-3 h-3" />
                 <span>TOPOLOGY: SPECTRAL_MESH</span>
               </div>
            </div>
            <div className="absolute bottom-4 right-4 z-20">
               <div className="flex items-center gap-2 text-xs font-mono text-white/50 bg-black/50 backdrop-blur px-2 py-1 rounded border border-white/5">
                 <Wifi className="w-3 h-3" />
                 <span>LATENCY: 12ms</span>
               </div>
            </div>
          </Card>
        </div>

        {/* Alerts Feed (1/3 width) */}
        <div className="bg-white/[0.02] border border-white/10 rounded-lg flex flex-col h-full overflow-hidden">
          <div className="p-3 border-b border-white/10 bg-white/[0.02] flex justify-between items-center">
            <h3 className="text-xs font-mono text-muted-foreground uppercase flex items-center gap-2">
              <Activity className="w-3 h-3" /> Event Log
            </h3>
            <Badge variant="outline" className="text-[9px] h-4 px-1 border-white/10 text-white/40">REAL-TIME</Badge>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-2">
            <AnimatePresence initial={false}>
              {alerts.map((alert) => (
                <motion.div
                  key={alert.id}
                  initial={{ opacity: 0, height: 0, x: -20 }}
                  animate={{ opacity: 1, height: "auto", x: 0 }}
                  exit={{ opacity: 0, height: 0 }}
                  className={`p-3 rounded border text-xs font-mono relative overflow-hidden ${
                    alert.type === 'CRITICAL' ? 'bg-red-500/5 border-red-500/20 text-red-300' :
                    alert.type === 'WARNING' ? 'bg-yellow-500/5 border-yellow-500/20 text-yellow-300' :
                    'bg-blue-500/5 border-blue-500/20 text-blue-300'
                  }`}
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-bold tracking-tight">{alert.message}</span>
                    <span className="opacity-50 text-[9px]">{alert.timestamp}</span>
                  </div>
                  <div className="flex justify-between items-center opacity-60 text-[9px]">
                    <span>NODE_{alert.nodeId}</span>
                    <span>HASH: {Math.random().toString(36).substr(2, 4).toUpperCase()}</span>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {alerts.length === 0 && (
               <div className="text-center text-muted-foreground text-xs py-10 font-mono">
                 Initializing Stream...
               </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
