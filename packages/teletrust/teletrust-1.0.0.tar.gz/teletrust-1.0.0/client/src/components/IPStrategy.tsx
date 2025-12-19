import { motion } from "framer-motion";
import { ArrowUpRight, Shield, Rocket, Lock, GitFork, Users, Building2, CheckCircle2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Tier {
  name: string;
  price: string;
  target: string;
  license: string;
  features: string[];
  ip_status: "Open Source" | "Proprietary" | "Trade Secret";
  icon: any;
}

const tiers: Tier[] = [
  {
    name: "ESM Open",
    price: "Free",
    target: "Lead Gen / Devs",
    license: "MIT / Apache 2.0",
    ip_status: "Open Source",
    icon: GitFork,
    features: [
      "Basic Spectral Analysis",
      "Generic Graph Laplacian",
      "Fixed-α Forgetting",
      "3-Node Triangle Demo",
      "Theory Documentation"
    ]
  },
  {
    name: "ESM Pro",
    price: "$49 - $299/mo",
    target: "SaaS / Teams",
    license: "Commercial SaaS",
    ip_status: "Proprietary",
    icon: Users,
    features: [
      "Production Mesh Topology",
      "Healthcare Event Packs",
      "Production Thresholds",
      "FastAPI Wrapper",
      "Priority Support"
    ]
  },
  {
    name: "ESM Enterprise",
    price: "$2,499+/mo",
    target: "Healthcare / Compliance",
    license: "Enterprise Agreement",
    ip_status: "Trade Secret",
    icon: Building2,
    features: [
      "Adaptive Rhythm Dynamics",
      "Custom Calibration",
      "HIPAA Compliance Suite",
      "Audit Trail & Logging",
      "SLA Guarantees"
    ]
  }
];

export function IPStrategy() {
  return (
    <section id="ip-strategy" className="py-32 bg-black/40 border-t border-white/5">
      <div className="container px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-20 gap-8">
          <div>
            <span className="text-primary font-mono text-sm tracking-widest uppercase mb-2 block">
              ./Intellectual_Property
            </span>
            <h2 className="text-4xl md:text-6xl font-display font-bold">
              IP_PROTECTION <br />
              <span className="text-white/40">FRAMEWORK</span>
            </h2>
          </div>
          <p className="max-w-md text-muted-foreground font-mono text-sm leading-relaxed text-right md:text-left">
            Strategic segmentation of codebase to maximize valuation while enabling open-source lead generation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map((tier, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className={`h-full p-8 bg-[#0a0a0a] border-white/10 flex flex-col ${tier.name === 'ESM Enterprise' ? 'border-primary/50 relative overflow-hidden' : ''}`}>
                {tier.name === 'ESM Enterprise' && (
                  <div className="absolute top-0 right-0 p-4">
                    <div className="w-20 h-20 bg-primary/10 rounded-full blur-2xl absolute -top-10 -right-10" />
                  </div>
                )}

                <div className="mb-6 flex items-start justify-between">
                  <div className={`p-3 rounded-lg ${tier.name === 'ESM Open' ? 'bg-white/5' : 'bg-primary/10 text-primary'}`}>
                    <tier.icon className="w-6 h-6" />
                  </div>
                  <Badge variant="outline" className={`font-mono uppercase text-[10px] ${
                    tier.ip_status === 'Open Source' ? 'text-green-500 border-green-500/20' :
                    tier.ip_status === 'Proprietary' ? 'text-yellow-500 border-yellow-500/20' :
                    'text-red-500 border-red-500/20'
                  }`}>
                    {tier.ip_status}
                  </Badge>
                </div>

                <h3 className="text-2xl font-display font-bold mb-2">{tier.name}</h3>
                <div className="text-xl font-mono text-primary mb-4">{tier.price}</div>
                <p className="text-muted-foreground text-sm font-mono mb-8 border-l-2 border-white/10 pl-4">
                  Target: {tier.target}
                  <br />
                  License: {tier.license}
                </p>

                <div className="space-y-4 mb-8 flex-grow">
                  {tier.features.map((feature, i) => (
                    <div key={i} className="flex items-center gap-3 text-sm text-white/80">
                      {tier.ip_status === 'Open Source' ? (
                        <CheckCircle2 className="w-4 h-4 text-white/20" />
                      ) : (
                        <Shield className="w-4 h-4 text-primary" />
                      )}
                      {feature}
                    </div>
                  ))}
                </div>

                <Button variant={tier.name === 'ESM Open' ? 'outline' : 'default'} className="w-full font-mono uppercase text-xs tracking-widest">
                  {tier.name === 'ESM Open' ? 'View Repo' : 'View Licensing'}
                </Button>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="mt-16 p-8 border border-white/10 bg-white/5 rounded-lg">
          <h3 className="text-xl font-display font-bold mb-6 flex items-center gap-2">
            <Lock className="w-5 h-5 text-primary" />
            PROTECTED ASSETS INVENTORY
          </h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { name: "Graph Topology", value: "$50K-100K", status: "Trade Secret", desc: "Specific 61-node architecture" },
              { name: "Event Mapping", value: "$75K-150K", status: "Trade Secret", desc: "Healthcare domain vectors" },
              { name: "Rhythm Dynamics", value: "$100K-200K", status: "Patent Pending", desc: "Adaptive memory algorithm" },
              { name: "Spectral Consensus", value: "$200K-500K", status: "Provisional Patent", desc: "Core detection method" }
            ].map((asset, i) => (
              <div key={i} className="p-4 bg-black/40 border border-white/5 rounded">
                <div className="text-[10px] text-muted-foreground uppercase font-mono mb-1">{asset.status}</div>
                <div className="font-bold text-lg mb-1">{asset.name}</div>
                <div className="text-primary font-mono text-sm mb-2">{asset.value}</div>
                <div className="text-xs text-white/40 leading-relaxed">{asset.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
