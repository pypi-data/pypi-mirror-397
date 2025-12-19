import { motion } from "framer-motion";
import { ArrowRight, Code, Cpu } from "lucide-react";
import { Link } from "wouter";
import heroBg from "@assets/generated_images/abstract_dark_digital_noise_gradient_background.png";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-16">
      {/* Background with overlay */}
      <div className="absolute inset-0 z-0">
        <img
          src={heroBg}
          alt="Background"
          className="w-full h-full object-cover opacity-40 mix-blend-screen"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-background via-transparent to-background" />
        <div className="absolute inset-0 grid-pattern opacity-20" />
      </div>

      <div className="container relative z-10 px-6">
        <div className="max-w-4xl">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="flex items-center gap-2 mb-6">
              <span className="h-px w-8 bg-primary" />
              <span className="font-mono text-primary text-sm tracking-widest uppercase">
                Enterprise Compliance OS
              </span>
            </div>
          </motion.div>

          <motion.h1
            className="text-6xl md:text-8xl font-display font-bold leading-none mb-8 tracking-tighter"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            ONE ENGINE. <br />
            <span className="text-stroke text-transparent hover:text-primary transition-colors duration-500">
              TOTAL COMPLIANCE.
            </span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-muted-foreground max-w-2xl mb-12 font-mono leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
          >
            Unifying Academic Integrity (APA) and Healthcare Privacy (HIPAA)
            under a single Spectral Consensus Architecture.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
          >
            <Link href="/platform" className="group flex items-center justify-center gap-2 bg-primary text-background px-8 py-4 font-mono font-bold uppercase hover:bg-white transition-colors">
              Launch Sentinel OS
              <Cpu className="w-4 h-4 group-hover:rotate-90 transition-transform" />
            </Link>
            <a
              href="#projects"
              className="flex items-center justify-center gap-2 border border-white/20 bg-black/50 backdrop-blur-sm px-8 py-4 font-mono font-bold uppercase hover:bg-white/5 transition-colors"
            >
              View IP Portfolio
            </a>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        className="absolute bottom-10 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 text-muted-foreground/50"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1, duration: 1 }}
      >
        <span className="font-mono text-xs uppercase tracking-widest">Scroll</span>
        <div className="w-px h-12 bg-gradient-to-b from-muted-foreground/50 to-transparent" />
      </motion.div>
    </section>
  );
}
