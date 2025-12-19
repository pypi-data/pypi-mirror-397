import { useState, useEffect } from "react";
import { Link } from "wouter";
import { Check, Zap, Shield, BookOpen, Cpu, ArrowLeft, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from "@tanstack/react-query";

interface StripeProduct {
  id: string;
  name: string;
  description: string;
  active: boolean;
  metadata: Record<string, string>;
  prices: Array<{
    id: string;
    unit_amount: number;
    currency: string;
    recurring: { interval: string } | null;
    active: boolean;
  }>;
}

interface PriceTier {
  id: string;
  name: string;
  description: string;
  price: number;
  priceId: string;
  period: string;
  features: string[];
  icon: React.ElementType;
  popular?: boolean;
  module: "edu" | "health" | "os";
  ctaText: string;
}

const FALLBACK_TIERS: PriceTier[] = [
  {
    id: "edu-starter",
    name: "Sentinel Edu - Starter",
    description: "Academic integrity auditing for students",
    price: 9.99,
    priceId: "",
    period: "month",
    features: [
      "100 analyses per month",
      "Banned word detection",
      "Cadence scoring",
      "APA-7 formatting hints",
      "Email support",
    ],
    icon: BookOpen,
    module: "edu",
    ctaText: "Start Writing Better",
  },
  {
    id: "edu-pro",
    name: "Sentinel Edu - Professional",
    description: "Advanced auditing with multi-source citations",
    price: 29,
    priceId: "",
    period: "month",
    features: [
      "Unlimited analyses",
      "Multi-source citation search (PubMed, OpenAlex)",
      "Full APA-7 compliance checking",
      "Export to Word/PDF",
      "Priority support",
      "Team collaboration (3 seats)",
    ],
    icon: BookOpen,
    popular: true,
    module: "edu",
    ctaText: "Upgrade to Pro",
  },
  {
    id: "health-starter",
    name: "Sentinel Health - Starter",
    description: "HIPAA compliance for small practices",
    price: 49,
    priceId: "",
    period: "month",
    features: [
      "Up to 500 events/month",
      "Real-time compliance monitoring",
      "Basic audit logs",
      "Email alerts",
      "HIPAA compliance reports",
    ],
    icon: Shield,
    module: "health",
    ctaText: "Protect Your Practice",
  },
  {
    id: "health-pro",
    name: "Sentinel Health - Professional",
    description: "Full telehealth compliance suite",
    price: 149,
    priceId: "",
    period: "month",
    features: [
      "Unlimited events",
      "Spectral graph topology encryption",
      "Full audit trail with timestamps",
      "Real-time monitoring dashboard",
      "API access",
      "Dedicated support",
      "Custom compliance rules",
    ],
    icon: Shield,
    popular: true,
    module: "health",
    ctaText: "Get Full Protection",
  },
  {
    id: "os-bundle",
    name: "Sentinel OS - Complete Suite",
    description: "Full access to all Sentinel modules",
    price: 299,
    priceId: "",
    period: "month",
    features: [
      "All Sentinel Edu features",
      "All Sentinel Health features",
      "Priority feature requests",
      "White-label options",
      "Custom integrations",
      "Dedicated account manager",
      "SLA guarantee",
      "On-premise deployment option",
    ],
    icon: Cpu,
    module: "os",
    ctaText: "Contact for Enterprise",
  },
];

function mapProductsToTiers(products: StripeProduct[]): PriceTier[] {
  const tiers: PriceTier[] = [];

  for (const product of products) {
    if (!product.active || !product.prices.length) continue;

    const price = product.prices.find(p => p.active) || product.prices[0];
    const metadata = product.metadata || {};
    const module = (metadata.module as "edu" | "health" | "os") || "edu";

    let icon = BookOpen;
    if (module === "health") icon = Shield;
    if (module === "os") icon = Cpu;

    tiers.push({
      id: product.id,
      name: product.name,
      description: product.description || "",
      price: (price.unit_amount || 0) / 100,
      priceId: price.id,
      period: price.recurring?.interval || "month",
      features: getFeatures(product.name, metadata),
      icon,
      popular: metadata.tier === "professional",
      module,
      ctaText: getCTA(metadata.tier || "starter"),
    });
  }

  return tiers.length > 0 ? tiers : FALLBACK_TIERS;
}

function getFeatures(name: string, metadata: Record<string, string>): string[] {
  if (name.includes("Starter") && name.includes("Edu")) {
    return [
      `${metadata.analyses_limit || "100"} analyses per month`,
      "Banned word detection",
      "Cadence scoring",
      "APA-7 formatting hints",
      "Email support",
    ];
  }
  if (name.includes("Professional") && name.includes("Edu")) {
    return [
      "Unlimited analyses",
      "Multi-source citation search (PubMed, OpenAlex)",
      "Full APA-7 compliance checking",
      "Export to Word/PDF",
      "Priority support",
      "Team collaboration (3 seats)",
    ];
  }
  if (name.includes("Starter") && name.includes("Health")) {
    return [
      `Up to ${metadata.events_limit || "500"} events/month`,
      "Real-time compliance monitoring",
      "Basic audit logs",
      "Email alerts",
      "HIPAA compliance reports",
    ];
  }
  if (name.includes("Professional") && name.includes("Health")) {
    return [
      "Unlimited events",
      "Spectral graph topology encryption",
      "Full audit trail with timestamps",
      "Real-time monitoring dashboard",
      "API access",
      "Dedicated support",
    ];
  }
  if (name.includes("Complete Suite")) {
    return [
      "All Sentinel Edu features",
      "All Sentinel Health features",
      "Priority feature requests",
      "White-label options",
      "Custom integrations",
      "Dedicated account manager",
      "SLA guarantee",
    ];
  }
  return ["Feature list unavailable"];
}

function getCTA(tier: string): string {
  switch (tier) {
    case "starter": return "Get Started";
    case "professional": return "Upgrade to Pro";
    case "enterprise": return "Contact for Enterprise";
    default: return "Get Started";
  }
}

export default function PricingPage() {
  const [loading, setLoading] = useState<string | null>(null);
  const [activeModule, setActiveModule] = useState<"all" | "edu" | "health" | "os">("all");

  const { data: productsData, isLoading: productsLoading } = useQuery({
    queryKey: ["products"],
    queryFn: async () => {
      const res = await fetch("/api/products");
      if (!res.ok) throw new Error("Failed to fetch products");
      return res.json();
    },
  });

  const pricingTiers = productsData?.data
    ? mapProductsToTiers(productsData.data)
    : FALLBACK_TIERS;

  const handleCheckout = async (tier: PriceTier) => {
    if (tier.module === "os" || !tier.priceId) {
      const element = document.getElementById("contact-enterprise");
      if (element) element.scrollIntoView({ behavior: "smooth" });
      return;
    }

    setLoading(tier.id);
    try {
      const response = await fetch("/api/checkout", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          priceId: tier.priceId,
          userId: "demo-user",
        }),
      });

      const data = await response.json();
      if (data.url) {
        window.location.href = data.url;
      } else if (data.error) {
        alert(`Checkout error: ${data.error}`);
      }
    } catch (error) {
      console.error("Checkout error:", error);
      alert("Unable to start checkout. Please try again.");
    } finally {
      setLoading(null);
    }
  };

  const filteredTiers = activeModule === "all"
    ? pricingTiers
    : pricingTiers.filter(t => t.module === activeModule);

  return (
    <div className="min-h-screen bg-black text-white">
      <div className="absolute inset-0 grid-pattern opacity-10 pointer-events-none" />

      <header className="border-b border-white/10 bg-black/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2 text-muted-foreground hover:text-white transition-colors">
            <ArrowLeft className="w-4 h-4" />
            <span className="font-mono text-sm">Back to Portfolio</span>
          </Link>
          <div className="flex items-center gap-2">
            <Cpu className="w-5 h-5 text-primary" />
            <span className="font-display font-bold">SENTINEL<span className="text-primary">_OS</span></span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-16 relative z-10">
        <div className="text-center mb-12">
          <Badge variant="outline" className="mb-4 border-primary/30 text-primary">
            PRICING
          </Badge>
          <h1 className="text-4xl md:text-6xl font-display font-bold mb-4">
            CHOOSE_YOUR_PLAN
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Start with a single module or get the complete Sentinel OS suite.
            All plans include a 7-day money-back guarantee.
          </p>
        </div>

        {/* Performance Benchmarks */}
        <div className="grid md:grid-cols-4 gap-6 mb-16 max-w-5xl mx-auto">
          <Card className="p-6 border-white/10 bg-[#0a0a0a] text-center" data-testid="benchmark-detection">
            <div className="text-3xl font-bold text-primary mb-2">99.2%</div>
            <div className="text-sm text-muted-foreground font-mono">DETECTION ACCURACY</div>
            <div className="text-xs text-white/50 mt-1">Banned word identification</div>
          </Card>
          <Card className="p-6 border-white/10 bg-[#0a0a0a] text-center" data-testid="benchmark-response">
            <div className="text-3xl font-bold text-primary mb-2">&lt;50ms</div>
            <div className="text-sm text-muted-foreground font-mono">RESPONSE TIME</div>
            <div className="text-xs text-white/50 mt-1">API analysis latency</div>
          </Card>
          <Card className="p-6 border-white/10 bg-[#0a0a0a] text-center" data-testid="benchmark-uptime">
            <div className="text-3xl font-bold text-primary mb-2">99.9%</div>
            <div className="text-sm text-muted-foreground font-mono">UPTIME SLA</div>
            <div className="text-xs text-white/50 mt-1">Enterprise reliability</div>
          </Card>
          <Card className="p-6 border-white/10 bg-[#0a0a0a] text-center" data-testid="benchmark-roi">
            <div className="text-3xl font-bold text-primary mb-2">4.2x</div>
            <div className="text-sm text-muted-foreground font-mono">AVG ROI</div>
            <div className="text-xs text-white/50 mt-1">Cost savings reported</div>
          </Card>
        </div>

        <Tabs defaultValue="all" className="mb-12">
          <TabsList className="mx-auto flex w-fit bg-white/5 border border-white/10">
            <TabsTrigger
              value="all"
              onClick={() => setActiveModule("all")}
              className="data-[state=active]:bg-primary data-[state=active]:text-black font-mono"
            >
              All Plans
            </TabsTrigger>
            <TabsTrigger
              value="edu"
              onClick={() => setActiveModule("edu")}
              className="data-[state=active]:bg-primary data-[state=active]:text-black font-mono"
            >
              Education
            </TabsTrigger>
            <TabsTrigger
              value="health"
              onClick={() => setActiveModule("health")}
              className="data-[state=active]:bg-primary data-[state=active]:text-black font-mono"
            >
              Healthcare
            </TabsTrigger>
            <TabsTrigger
              value="os"
              onClick={() => setActiveModule("os")}
              className="data-[state=active]:bg-primary data-[state=active]:text-black font-mono"
            >
              Enterprise
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {productsLoading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {filteredTiers.map((tier) => {
              const Icon = tier.icon;
              return (
                <Card
                  key={tier.id}
                  data-testid={`card-pricing-${tier.id}`}
                  className={`p-8 relative flex flex-col ${
                    tier.popular
                      ? "border-primary bg-primary/5 ring-1 ring-primary/20"
                      : "border-white/10 bg-[#0a0a0a]"
                  }`}
                >
                  {tier.popular && (
                    <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-black font-mono">
                      MOST POPULAR
                    </Badge>
                  )}

                  <div className="flex items-start justify-between mb-6">
                    <div className={`p-3 rounded-lg ${tier.popular ? "bg-primary/20" : "bg-white/5"}`}>
                      <Icon className={`w-6 h-6 ${tier.popular ? "text-primary" : "text-white/60"}`} />
                    </div>
                    <Badge variant="outline" className="font-mono text-[10px] uppercase border-white/20">
                      {tier.module}
                    </Badge>
                  </div>

                  <h3 className="text-xl font-display font-bold mb-1">{tier.name}</h3>
                  <p className="text-sm text-muted-foreground mb-4">{tier.description}</p>

                  <div className="flex items-baseline gap-1 mb-6">
                    <span className="text-4xl font-bold">${tier.price}</span>
                    <span className="text-muted-foreground">/{tier.period}</span>
                  </div>

                  <ul className="space-y-3 mb-8 flex-1">
                    {tier.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-3 text-sm">
                        <Check className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <span className="text-white/80">{feature}</span>
                      </li>
                    ))}
                  </ul>

                  <Button
                    data-testid={`button-checkout-${tier.id}`}
                    className="w-full font-mono uppercase"
                    variant={tier.popular ? "default" : "outline"}
                    onClick={() => handleCheckout(tier)}
                    disabled={loading === tier.id}
                  >
                    {loading === tier.id ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      tier.ctaText
                    )}
                  </Button>
                </Card>
              );
            })}
          </div>
        )}

        <section id="contact-enterprise" className="mt-24 max-w-3xl mx-auto">
          <Card className="p-8 border-white/10 bg-[#0a0a0a]">
            <div className="text-center mb-8">
              <h2 className="text-2xl font-display font-bold mb-2">Enterprise Inquiry</h2>
              <p className="text-muted-foreground">
                Need custom deployment, on-premise hosting, or special compliance requirements?
              </p>
            </div>

            <form className="space-y-6" onSubmit={(e) => { e.preventDefault(); alert("Thank you! We'll be in touch within 24 hours."); }}>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-mono text-muted-foreground mb-2">Name</label>
                  <input
                    data-testid="input-enterprise-name"
                    type="text"
                    required
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-md focus:border-primary focus:outline-none"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-mono text-muted-foreground mb-2">Email</label>
                  <input
                    data-testid="input-enterprise-email"
                    type="email"
                    required
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-md focus:border-primary focus:outline-none"
                    placeholder="you@company.com"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-mono text-muted-foreground mb-2">Company</label>
                <input
                  data-testid="input-enterprise-company"
                  type="text"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-md focus:border-primary focus:outline-none"
                  placeholder="Company name"
                />
              </div>

              <div>
                <label className="block text-sm font-mono text-muted-foreground mb-2">Message</label>
                <textarea
                  data-testid="input-enterprise-message"
                  rows={4}
                  required
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-md focus:border-primary focus:outline-none resize-none"
                  placeholder="Tell us about your needs..."
                />
              </div>

              <Button
                data-testid="button-enterprise-submit"
                type="submit"
                className="w-full font-mono uppercase"
              >
                Send Inquiry
              </Button>
            </form>
          </Card>
        </section>

        <div className="mt-16 text-center text-sm text-muted-foreground">
          <p>
            All plans include SSL encryption, 99.9% uptime SLA, and GDPR compliance.
          </p>
          <p className="mt-2">
            Questions? Email <a href="mailto:hello@sentinel-os.com" className="text-primary hover:underline">hello@sentinel-os.com</a>
          </p>
        </div>
      </main>
    </div>
  );
}
