import { motion } from "framer-motion";
import {
  TrendingUp,
  Users,
  Target,
  ShieldCheck,
  Zap,
  BarChart3,
  FileText,
  Award,
  PieChart,
  Cpu
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, BarChart, Bar, Cell } from "recharts";

// Data from user's IP_PROTECTION_GUIDE
const REVENUE_PROJECTIONS = [
  { year: "Y1 (Base)", revenue: 100000, conservative: 50000, optimistic: 150000 },
  { year: "Y2 (Growth)", revenue: 300000, conservative: 150000, optimistic: 500000 },
  { year: "Y3 (Scale)", revenue: 750000, conservative: 400000, optimistic: 1500000 },
];

const VALUATION_DATA = [
  { name: "Graph Topology", value: 75000, color: "#22c55e" },
  { name: "Event Mapping", value: 112500, color: "#22c55e" },
  { name: "Thresholds", value: 37500, color: "#eab308" },
  { name: "Rhythm Dynamics", value: 150000, color: "#ef4444" },
  { name: "Spectral Method", value: 350000, color: "#ef4444" },
];

const BENCHMARK_DATA = [
  { metric: "Latency (ms)", sentinel: 12, standard: 145 },
  { metric: "False Positives (%)", sentinel: 0.2, standard: 4.5 },
  { metric: "PHI Retention", sentinel: 0, standard: 100 },
];

export function ViabilityEngine() {
  return (
    <div className="h-full flex flex-col space-y-6 overflow-y-auto pr-2">
      <div className="flex justify-between items-end">
        <div>
           <h2 className="font-display font-bold text-2xl mb-2">COMMERCIAL VIABILITY_PROOF</h2>
           <p className="text-muted-foreground font-mono text-sm">
             Evidence-based validation of Sentinel OS architecture and market fit.
           </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" className="font-mono text-xs uppercase">
            <FileText className="w-3 h-3 mr-2" /> Export PDF
          </Button>
          <Button size="sm" className="font-mono text-xs uppercase bg-primary text-black hover:bg-white">
            <Award className="w-3 h-3 mr-2" /> Investor Deck
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         <Card className="p-6 bg-[#111] border-white/10 flex flex-col">
            <div className="flex items-center gap-2 mb-4 text-muted-foreground font-mono text-xs uppercase">
              <ShieldCheck className="w-4 h-4 text-primary" />
              IP Valuation
            </div>
            <div className="text-4xl font-display font-bold text-white mb-2">$725K+</div>
            <div className="text-xs text-muted-foreground mb-6">Current Asset Value (Pre-Revenue)</div>

            <div className="flex-1 space-y-3">
               {VALUATION_DATA.map((item, i) => (
                 <div key={i} className="flex justify-between items-center text-xs">
                   <span className="text-white/60">{item.name}</span>
                   <div className="flex items-center gap-2">
                     <div className="h-1.5 w-16 bg-white/10 rounded-full overflow-hidden">
                       <div
                         className="h-full rounded-full"
                         style={{ width: `${(item.value / 350000) * 100}%`, backgroundColor: item.color }}
                       />
                     </div>
                     <span className="font-mono text-white">${(item.value / 1000).toFixed(0)}k</span>
                   </div>
                 </div>
               ))}
            </div>
         </Card>

         <Card className="col-span-2 p-6 bg-[#111] border-white/10 flex flex-col">
            <div className="flex justify-between items-center mb-6">
               <div className="flex items-center gap-2 text-muted-foreground font-mono text-xs uppercase">
                 <TrendingUp className="w-4 h-4 text-primary" />
                 Revenue Trajectory (ARR)
               </div>
               <div className="flex gap-4 text-[10px] font-mono">
                 <div className="flex items-center gap-1"><div className="w-2 h-2 bg-primary rounded-full" /> Base Case</div>
                 <div className="flex items-center gap-1"><div className="w-2 h-2 bg-green-500/50 rounded-full" /> Optimistic</div>
               </div>
            </div>

            <div className="flex-1 min-h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={REVENUE_PROJECTIONS}>
                  <defs>
                    <linearGradient id="colorBase" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(80, 100%, 50%)" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="hsl(80, 100%, 50%)" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="colorOpt" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.1}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <XAxis dataKey="year" stroke="#666" fontSize={10} tickLine={false} axisLine={false} />
                  <YAxis stroke="#666" fontSize={10} tickFormatter={(val) => `$${val/1000}k`} tickLine={false} axisLine={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000', border: '1px solid #333' }}
                    itemStyle={{ fontSize: '12px', fontFamily: 'monospace' }}
                  />
                  <Area type="monotone" dataKey="optimistic" stroke="#22c55e" strokeWidth={1} strokeDasharray="5 5" fill="url(#colorOpt)" />
                  <Area type="monotone" dataKey="revenue" stroke="hsl(80, 100%, 50%)" strokeWidth={3} fill="url(#colorBase)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
         </Card>
      </div>

      <Tabs defaultValue="tech" className="w-full">
        <TabsList className="bg-white/5 border border-white/10 w-full justify-start h-12 p-1">
          <TabsTrigger value="tech" className="font-mono text-xs uppercase data-[state=active]:bg-primary data-[state=active]:text-black">
            Technical Superiority
          </TabsTrigger>
          <TabsTrigger value="market" className="font-mono text-xs uppercase data-[state=active]:bg-primary data-[state=active]:text-black">
            Market Fit (TAM/SAM)
          </TabsTrigger>
          <TabsTrigger value="moat" className="font-mono text-xs uppercase data-[state=active]:bg-primary data-[state=active]:text-black">
            Competitive Moat
          </TabsTrigger>
        </TabsList>

        <TabsContent value="tech" className="mt-4">
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <Card className="p-6 bg-[#111] border-white/10">
               <h3 className="font-display font-bold text-lg mb-4 flex items-center gap-2">
                 <Zap className="w-5 h-5 text-yellow-500" /> Performance Benchmarks
               </h3>
               <div className="space-y-6">
                 {BENCHMARK_DATA.map((item, i) => (
                   <div key={i}>
                     <div className="flex justify-between text-xs font-mono mb-2">
                       <span className="text-white/60">{item.metric}</span>
                       <span className="text-primary">{item.metric === "Latency (ms)" ? "-" : ""}{Math.abs(((item.standard - item.sentinel) / item.standard) * 100).toFixed(0)}% Better</span>
                     </div>
                     <div className="h-8 flex gap-1">
                       <div className="h-full bg-primary flex items-center justify-center text-[10px] font-bold text-black" style={{ width: item.metric === "PHI Retention" ? "0%" : "40%" }}>
                         {item.sentinel}
                       </div>
                       <div className="h-full bg-white/10 flex items-center justify-center text-[10px] text-white/40" style={{ width: "60%" }}>
                         {item.standard} (Competitor)
                       </div>
                     </div>
                   </div>
                 ))}
               </div>
             </Card>

             <Card className="p-6 bg-[#111] border-white/10 relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-20">
                 <Cpu className="w-24 h-24 text-primary" />
               </div>
               <h3 className="font-display font-bold text-lg mb-2">Why Sentinel Wins</h3>
               <ul className="space-y-4 mt-6">
                 {[
                   { title: "Spectral vs Text", desc: "We analyze mathematical topology, not raw text. Zero PHI/PII risk." },
                   { title: "Adaptive Memory", desc: "Rhythm dynamics (Patent Pending) adapt to user workflow speed." },
                   { title: "Mesh Topology", desc: "Proprietary graph structure calibrated for 99.9% consensus accuracy." }
                 ].map((feat, i) => (
                   <li key={i} className="flex gap-3">
                     <div className="w-6 h-6 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold shrink-0">
                       {i + 1}
                     </div>
                     <div>
                       <div className="font-bold text-sm text-white">{feat.title}</div>
                       <div className="text-xs text-muted-foreground">{feat.desc}</div>
                     </div>
                   </li>
                 ))}
               </ul>
             </Card>
           </div>
        </TabsContent>

        <TabsContent value="market" className="mt-4">
           <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card className="p-6 bg-blue-900/10 border-blue-500/20 flex flex-col items-center text-center">
                 <div className="mb-2 text-blue-400 font-mono text-sm uppercase">EdTech (APA)</div>
                 <div className="text-3xl font-bold text-white mb-1">$128B</div>
                 <div className="text-xs text-white/40 mb-4">Total Addressable Market</div>
                 <Badge variant="outline" className="border-blue-500/40 text-blue-400 bg-blue-500/10">High Velocity</Badge>
              </Card>
              <Card className="p-6 bg-green-900/10 border-green-500/20 flex flex-col items-center text-center">
                 <div className="mb-2 text-green-400 font-mono text-sm uppercase">HealthTech (HIPAA)</div>
                 <div className="text-3xl font-bold text-white mb-1">$50B</div>
                 <div className="text-xs text-white/40 mb-4">Compliance Software SAM</div>
                 <Badge variant="outline" className="border-green-500/40 text-green-400 bg-green-500/10">High Margin</Badge>
              </Card>
              <Card className="p-6 bg-purple-900/10 border-purple-500/20 flex flex-col items-center text-center">
                 <div className="mb-2 text-purple-400 font-mono text-sm uppercase">Sentinel SOM</div>
                 <div className="text-3xl font-bold text-white mb-1">$2.5M</div>
                 <div className="text-xs text-white/40 mb-4">Serviceable Obtainable Market (Y1-3)</div>
                 <Badge variant="outline" className="border-purple-500/40 text-purple-400 bg-purple-500/10">Realistic Target</Badge>
              </Card>
           </div>
        </TabsContent>

        <TabsContent value="moat">
           <Card className="p-8 bg-[#111] border-white/10">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
                 <div>
                    <h3 className="font-display font-bold text-xl mb-6">Defensibility Matrix</h3>
                    <div className="space-y-6">
                       <div>
                          <div className="flex justify-between text-sm font-bold mb-1">
                             <span>Technical Complexity</span>
                             <span className="text-primary">High</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                             <div className="h-full bg-primary w-[85%]" />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">Requires specialized spectral graph theory knowledge.</p>
                       </div>
                       <div>
                          <div className="flex justify-between text-sm font-bold mb-1">
                             <span>Regulatory Barrier</span>
                             <span className="text-primary">Very High</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                             <div className="h-full bg-primary w-[95%]" />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">Healthcare compliance requires rigorous audit trails (built-in).</p>
                       </div>
                       <div>
                          <div className="flex justify-between text-sm font-bold mb-1">
                             <span>Network Effects</span>
                             <span className="text-primary">Medium</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                             <div className="h-full bg-primary w-[60%]" />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">Consensus improves as more agents/nodes join the mesh.</p>
                       </div>
                    </div>
                 </div>
                 <div className="border-l border-white/10 pl-12 flex flex-col justify-center">
                    <div className="mb-6">
                       <h4 className="font-mono text-xs uppercase text-muted-foreground mb-2">Primary Competitors</h4>
                       <div className="flex gap-2 flex-wrap">
                          <Badge variant="outline" className="border-white/20 text-white/60">Turnitin</Badge>
                          <Badge variant="outline" className="border-white/20 text-white/60">Vanta</Badge>
                          <Badge variant="outline" className="border-white/20 text-white/60">Drata</Badge>
                       </div>
                    </div>
                    <div>
                       <h4 className="font-mono text-xs uppercase text-muted-foreground mb-2">Our "Unfair" Advantage</h4>
                       <p className="text-lg font-bold text-white italic">
                         "We don't read the data to protect it. We measure its rhythm."
                       </p>
                       <p className="text-sm text-muted-foreground mt-2">
                         Competitors ingest text (risk). We ingest spectral signals (safe).
                       </p>
                    </div>
                 </div>
              </div>
           </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
