import { Mail, Github, Linkedin, Twitter } from "lucide-react";

export function Footer() {
  return (
    <footer id="contact" className="py-20 border-t border-white/10 bg-black">
      <div className="container px-6 flex flex-col items-center text-center">
        <h2 className="text-4xl md:text-6xl font-display font-bold mb-8">
          LET'S BUILD <br />
          <span className="text-primary">THE IMPOSSIBLE</span>
        </h2>

        <p className="text-muted-foreground font-mono mb-12 max-w-md">
          Available for freelance opportunities and technical consulting.
          Drop a line to discuss your next project.
        </p>

        <a
          href="mailto:hello@example.com"
          className="text-2xl font-mono hover:text-primary transition-colors mb-12 border-b border-white/20 pb-1"
        >
          hello@devportfolio.com
        </a>

        <div className="flex gap-8 mb-12">
          {[Github, Linkedin, Twitter, Mail].map((Icon, i) => (
            <a
              key={i}
              href="#"
              className="p-3 border border-white/10 hover:border-primary hover:text-primary hover:bg-white/5 transition-all rounded-full"
            >
              <Icon className="w-5 h-5" />
            </a>
          ))}
        </div>

        <div className="text-white/20 font-mono text-xs">
          © {new Date().getFullYear()} DEV_PORTFOLIO. SYSTEM_STATUS: ONLINE
        </div>
      </div>
    </footer>
  );
}
