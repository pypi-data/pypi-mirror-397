import { motion } from "framer-motion";
import { ArrowUpRight, CreditCard, Rocket, CheckCircle2, AlertCircle, DollarSign, Play } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogTrigger, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";
import { DashboardDemo } from "@/components/demos/DashboardDemo";
import { APAVoiceGuardDemo } from "@/components/demos/APAVoiceGuardDemo";
import { ConsentGuardDemo } from "@/components/demos/ConsentGuardDemo";

interface Project {
  title: string;
  category: string;
  description: string;
  tech: string[];
  mrr_potential: string;
  deployability_score: number;
  stripe_ready: boolean;
  has_demo: boolean;
  demo_component?: React.ReactNode;
}

const projects: Project[] = [
  {
    title: "APA_Voice_Guard",
    category: "EdTech SaaS",
    description: "AI-powered academic writing assistant with multi-source citation (PubMed, OpenAlex) and style enforcement.",
    tech: ["Python", "Streamlit", "NLP", "PubMed API"],
    mrr_potential: "$3.5k",
    deployability_score: 92,
    stripe_ready: false,
    has_demo: true,
    demo_component: <APAVoiceGuardDemo />
  },
  {
    title: "Consent_Guard",
    category: "HealthTech",
    description: "Telehealth compliance and revenue assurance platform. Automates patient consent tracking.",
    tech: ["Python", "Encryption", "Audit Logs"],
    mrr_potential: "$5.0k",
    deployability_score: 85,
    stripe_ready: false,
    has_demo: true,
    demo_component: <ConsentGuardDemo />
  },
  {
    title: "Neural_Nexus",
    category: "AI Concept",
    description: "Enterprise-grade AI model training dashboard. Subscription-ready for data science teams.",
    tech: ["React", "Python", "Stripe API"],
    mrr_potential: "$2.5k",
    deployability_score: 95,
    stripe_ready: true,
    has_demo: true,
    demo_component: <DashboardDemo />
  }
];

export function Projects() {
  return (
    <section id="projects" className="py-32 border-t border-white/5 bg-black/40">
      <div className="container px-6">
        <div className="flex flex-col md:flex-row md:items-end justify-between mb-20 gap-8">
          <div>
            <span className="text-primary font-mono text-sm tracking-widest uppercase mb-2 block">
              ./MicroSaaS_Portfolio
            </span>
            <h2 className="text-5xl md:text-7xl font-display font-bold">
              VENTURE_LAB
            </h2>
          </div>
          <p className="max-w-md text-muted-foreground font-mono text-sm leading-relaxed text-right md:text-left">
            Analyzing codebase for commercial viability.
            Monitoring deployment readiness and Stripe integration status.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {projects.map((project, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="group relative border border-white/10 bg-[#0a0a0a] hover:border-primary/50 transition-all p-8 flex flex-col h-full rounded-sm"
            >
              <div className="absolute top-4 right-4 flex gap-2">
                 <Badge variant="outline" className={`font-mono text-[10px] uppercase ${project.stripe_ready ? 'border-primary/50 text-primary' : 'border-white/10 text-muted-foreground'}`}>
                    {project.stripe_ready ? 'Stripe Connected' : 'Stripe Pending'}
                 </Badge>
              </div>

              <div className="mb-6">
                <span className="inline-block px-3 py-1 bg-white/5 text-xs font-mono text-primary rounded-full mb-4 border border-white/5">
                  {project.category}
                </span>
                <h3 className="text-2xl font-display font-bold mb-2 group-hover:text-primary transition-colors">
                  {project.title}
                </h3>
                <p className="text-muted-foreground font-mono text-xs leading-relaxed mb-6 border-l-2 border-white/10 pl-4">
                  {project.description}
                </p>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 gap-4 mb-8 p-4 bg-white/5 rounded-sm border border-white/5">
                <div>
                    <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">Deployability</span>
                    <div className="flex items-center gap-2">
                        <Rocket className="w-3 h-3 text-primary" />
                        <span className="font-mono font-bold">{project.deployability_score}%</span>
                    </div>
                </div>
                <div>
                    <span className="text-[10px] text-muted-foreground uppercase font-mono block mb-1">Est. MRR</span>
                    <div className="flex items-center gap-2">
                        <DollarSign className="w-3 h-3 text-green-500" />
                        <span className="font-mono font-bold text-green-500">{project.mrr_potential}</span>
                    </div>
                </div>
              </div>

              <div className="mt-auto space-y-3">
                {project.has_demo ? (
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button className="w-full font-mono uppercase text-xs tracking-widest bg-primary text-black hover:bg-primary/90">
                        <Play className="w-3 h-3 mr-2" /> Launch Live Demo
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-4xl bg-black border-white/10 p-0 overflow-hidden">
                      <VisuallyHidden>
                        <DialogTitle>{project.title} Demo</DialogTitle>
                        <DialogDescription>Interactive demonstration of {project.title}</DialogDescription>
                      </VisuallyHidden>
                      {project.demo_component}
                    </DialogContent>
                  </Dialog>
                ) : (
                  <Button className="w-full font-mono uppercase text-xs tracking-widest bg-white/5 hover:bg-primary hover:text-black border border-white/10" variant="outline">
                      {project.stripe_ready ? 'Manage Subscription' : 'Connect Stripe'}
                  </Button>
                )}

                <div className="flex justify-between items-center text-[10px] font-mono text-white/30 pt-4 border-t border-white/5">
                  <span>STACK_ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</span>
                  <div className="flex gap-1">
                      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                      <span>ONLINE</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
