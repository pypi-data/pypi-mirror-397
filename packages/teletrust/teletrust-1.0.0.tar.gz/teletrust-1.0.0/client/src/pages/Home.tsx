import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { Projects } from "@/components/Projects";
import { Pricing } from "@/components/Pricing";
import { Skills } from "@/components/Skills";
import { CodeShowcase } from "@/components/CodeShowcase";
import { IPStrategy } from "@/components/IPStrategy";
import { Footer } from "@/components/Footer";

export default function Home() {
  return (
    <main className="min-h-screen bg-background text-foreground overflow-x-hidden selection:bg-primary selection:text-black">
      <Navbar />
      <Hero />
      <CodeShowcase />
      <Projects />
      <Pricing />
      <Skills />
      <IPStrategy />
      <Footer />
    </main>
  );
}
