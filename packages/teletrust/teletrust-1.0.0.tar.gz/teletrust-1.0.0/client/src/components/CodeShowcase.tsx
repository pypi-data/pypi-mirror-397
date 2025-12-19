import { motion } from "framer-motion";
import { Copy, Check, Terminal } from "lucide-react";
import { useState } from "react";

const codeSnippet = `class NeuralNetwork {
  constructor(layers) {
    this.layers = layers;
    this.weights = [];
    this.biases = [];
    this.init();
  }

  init() {
    // Initialize weights and biases
    // using Xavier initialization
    for (let i = 1; i < this.layers.length; i++) {
      this.weights.push(
        Matrix.random(
          this.layers[i],
          this.layers[i-1]
        )
      );
    }
  }

  feedForward(input) {
    // Forward propagation logic
    return output;
  }
}`;

export function CodeShowcase() {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(codeSnippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section className="py-32 bg-secondary/20 border-y border-white/5">
      <div className="container px-6 grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="text-primary font-mono text-sm tracking-widest uppercase mb-2 block">
            ./Code_Quality
          </span>
          <h2 className="text-4xl md:text-6xl font-display font-bold mb-6">
            ENGINEERED <br />
            FOR SCALE
          </h2>
          <p className="text-muted-foreground font-mono text-sm leading-relaxed mb-8 max-w-md">
            I don't just write code that works; I write code that is maintainable,
            performant, and scalable. Every function is crafted with intent.
          </p>

          <ul className="space-y-4 font-mono text-sm">
            {[
              "Test-Driven Development (TDD)",
              "Clean Architecture Principles",
              "CI/CD Pipeline Integration",
              "Performance Optimization"
            ].map((item, i) => (
              <li key={i} className="flex items-center gap-3 text-white/80">
                <span className="w-1.5 h-1.5 bg-primary rounded-full" />
                {item}
              </li>
            ))}
          </ul>
        </div>

        <motion.div
          className="relative group"
          initial={{ opacity: 0, x: 20 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
        >
          {/* Decorative glow */}
          <div className="absolute -inset-1 bg-gradient-to-r from-primary/20 to-transparent blur-xl opacity-20 group-hover:opacity-40 transition-opacity" />

          <div className="relative rounded-lg border border-white/10 bg-[#0a0a0a] overflow-hidden">
            <div className="flex items-center justify-between px-4 py-3 border-b border-white/10 bg-white/5">
              <div className="flex gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500/50" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/50" />
                <div className="w-3 h-3 rounded-full bg-green-500/50" />
              </div>
              <div className="font-mono text-xs text-muted-foreground flex items-center gap-2">
                <Terminal className="w-3 h-3" />
                core_logic.js
              </div>
              <button
                onClick={handleCopy}
                className="text-muted-foreground hover:text-primary transition-colors"
              >
                {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>

            <div className="p-6 overflow-x-auto">
              <pre className="font-mono text-sm leading-relaxed">
                <code className="text-white/80">
                  {codeSnippet.split('\n').map((line, i) => (
                    <div key={i} className="table-row">
                      <span className="table-cell select-none text-white/20 pr-4 text-right w-8">{i + 1}</span>
                      <span className="table-cell" dangerouslySetInnerHTML={{
                        __html: line
                          .replace(/class|constructor|this|return|let|for/g, '<span class="text-purple-400">$&</span>')
                          .replace(/NeuralNetwork|init|feedForward|push/g, '<span class="text-blue-400">$&</span>')
                          .replace(/\/\/.*/g, '<span class="text-green-400/50 italic">$&</span>')
                          .replace(/\(|\)|\{|\}/g, '<span class="text-yellow-400">$&</span>')
                      }} />
                    </div>
                  ))}
                </code>
              </pre>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
