import { motion } from "framer-motion";
import { Database, Layout, Smartphone, Lock, Globe, Cpu } from "lucide-react";

const skills = [
  { icon: Layout, name: "Frontend", desc: "React, Vue, Tailwind" },
  { icon: Database, name: "Backend", desc: "Node, Python, Go" },
  { icon: Cpu, name: "Systems", desc: "Docker, K8s, AWS" },
  { icon: Smartphone, name: "Mobile", desc: "React Native, Swift" },
  { icon: Lock, name: "Security", desc: "OAuth, Encryption" },
  { icon: Globe, name: "Network", desc: "REST, GraphQL, gRPC" },
];

export function Skills() {
  return (
    <section id="stack" className="py-32 container px-6">
      <div className="mb-16 text-center">
        <span className="text-primary font-mono text-sm tracking-widest uppercase mb-2 block">
          ./Capabilities
        </span>
        <h2 className="text-4xl md:text-6xl font-display font-bold">
          TECH_STACK
        </h2>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {skills.map((skill, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.05 }}
            className="group p-6 border border-white/10 hover:border-primary/50 bg-white/5 hover:bg-white/10 transition-all flex flex-col items-center text-center gap-4"
          >
            <div className="p-3 bg-white/5 rounded-full group-hover:bg-primary group-hover:text-black transition-colors">
              <skill.icon className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-display font-bold text-lg mb-1">{skill.name}</h3>
              <p className="font-mono text-xs text-muted-foreground">{skill.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
