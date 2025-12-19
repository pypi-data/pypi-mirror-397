import { Link } from "wouter";
import { Terminal, Cpu, Code2, Mail, Github, Twitter, Linkedin, ExternalLink } from "lucide-react";

export function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-white/10 bg-background/80 backdrop-blur-md">
      <div className="container mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="text-xl font-display font-bold tracking-tighter hover:text-primary transition-colors flex items-center gap-2">
          <Terminal className="w-5 h-5 text-primary" />
          DEV_PORTFOLIO
        </Link>

        <div className="hidden md:flex items-center gap-8 font-mono text-sm">
          <a href="#about" className="hover:text-primary transition-colors">./ABOUT</a>
          <a href="#projects" className="text-muted-foreground hover:text-foreground transition-colors">
            Projects
          </a>
          <a href="#stack" className="hover:text-primary transition-colors">./STACK</a>
          <Link href="/pricing" className="hover:text-primary transition-colors">./PRICING</Link>
          <a href="#contact" className="hover:text-primary transition-colors">./CONTACT</a>
        </div>

        <a
          href="https://github.com"
          target="_blank"
          rel="noreferrer"
          className="hidden md:flex items-center gap-2 px-4 py-2 border border-white/20 hover:border-primary hover:text-primary transition-all font-mono text-xs uppercase"
        >
          <Github className="w-4 h-4" />
          GitHub
        </a>
      </div>
    </nav>
  );
}
