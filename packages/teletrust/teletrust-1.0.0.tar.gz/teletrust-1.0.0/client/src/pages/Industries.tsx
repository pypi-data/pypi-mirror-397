import { Link } from "wouter";
import { ArrowLeft, Cpu, Building2, DollarSign, Factory, Heart, GraduationCap, Lock, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useQuery } from "@tanstack/react-query";

interface MarketPack {
  id: string;
  name: string;
  description: string;
  basePrice: number | null;
  features: string[];
  requiredTier: string;
  complianceFrameworks: string[];
  deploymentOptions: string[];
  icon: string;
  available: boolean;
}

const iconMap: Record<string, React.ElementType> = {
  Building2,
  DollarSign,
  Factory,
  Heart,
  GraduationCap,
};

export default function IndustriesPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["market-packs"],
    queryFn: async () => {
      const res = await fetch("/api/market-packs");
      if (!res.ok) throw new Error("Failed to fetch market packs");
      return res.json();
    },
  });

  const packs: MarketPack[] = data?.packs || [];
  const userTier = data?.userTier || "FREE";

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
            INDUSTRY SOLUTIONS
          </Badge>
          <h1 className="text-4xl md:text-6xl font-display font-bold mb-4">
            COMPLIANCE_BY_SECTOR
          </h1>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            Pre-configured compliance packages tailored to your industry's regulatory requirements.
            Each pack includes frameworks, deployment options, and specialized tooling.
          </p>
          {userTier !== "FREE" && (
            <Badge className="mt-4 bg-primary/20 text-primary border-primary/30">
              Your Tier: {userTier}
            </Badge>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto">
            {packs.map((pack) => {
              const Icon = iconMap[pack.icon] || Building2;
              return (
                <Card
                  key={pack.id}
                  data-testid={`card-industry-${pack.id}`}
                  className={`p-6 relative flex flex-col ${
                    pack.available
                      ? "border-primary/30 bg-primary/5"
                      : "border-white/10 bg-[#0a0a0a] opacity-80"
                  }`}
                >
                  {!pack.available && (
                    <div className="absolute top-4 right-4">
                      <Lock className="w-5 h-5 text-white/30" />
                    </div>
                  )}

                  <div className="flex items-start gap-4 mb-4">
                    <div className={`p-3 rounded-lg ${pack.available ? "bg-primary/20" : "bg-white/5"}`}>
                      <Icon className={`w-6 h-6 ${pack.available ? "text-primary" : "text-white/40"}`} />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-display font-bold">{pack.name}</h3>
                      <p className="text-sm text-muted-foreground">{pack.description}</p>
                    </div>
                  </div>

                  {pack.available && pack.basePrice !== null ? (
                    <div className="flex items-baseline gap-1 mb-4">
                      <span className="text-2xl font-bold">${pack.basePrice}</span>
                      <span className="text-muted-foreground text-sm">/month add-on</span>
                    </div>
                  ) : (
                    <div className="mb-4 space-y-2">
                      <Badge variant="outline" className="border-yellow-500/30 text-yellow-500 text-xs">
                        Requires {pack.requiredTier} tier
                      </Badge>
                      <p className="text-sm text-white/40 italic">
                        Pricing available with {pack.requiredTier} subscription
                      </p>
                    </div>
                  )}

                  {pack.complianceFrameworks.length > 0 && (
                    <div className="mb-4">
                      <p className="text-xs font-mono text-muted-foreground mb-2">FRAMEWORKS</p>
                      <div className="flex flex-wrap gap-1">
                        {pack.complianceFrameworks.map((framework) => (
                          <Badge key={framework} variant="outline" className="text-xs border-white/20">
                            {framework}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  <ul className="space-y-2 mb-6 flex-1">
                    {pack.features.map((feature, i) => (
                      <li key={i} className="flex items-start gap-2 text-sm">
                        <ChevronRight className="w-4 h-4 text-primary shrink-0 mt-0.5" />
                        <span className={pack.available ? "text-white/80" : "text-white/50"}>{feature}</span>
                      </li>
                    ))}
                  </ul>

                  {pack.deploymentOptions.length > 0 && (
                    <div className="mb-4 pt-4 border-t border-white/10">
                      <p className="text-xs font-mono text-muted-foreground mb-2">DEPLOYMENT</p>
                      <div className="flex gap-2">
                        {pack.deploymentOptions.map((option) => (
                          <span key={option} className="text-xs text-white/60 capitalize">{option}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button
                    data-testid={`button-industry-${pack.id}`}
                    className="w-full font-mono uppercase"
                    variant={pack.available ? "default" : "outline"}
                    disabled={!pack.available}
                    asChild={pack.available}
                  >
                    {pack.available ? (
                      <Link href="/pricing">View Pricing</Link>
                    ) : (
                      <span>Upgrade to Access</span>
                    )}
                  </Button>
                </Card>
              );
            })}
          </div>
        )}

        <div className="mt-16 text-center">
          <p className="text-muted-foreground mb-4">
            Need a custom compliance configuration for your industry?
          </p>
          <Button variant="outline" className="font-mono" asChild>
            <Link href="/pricing#contact-enterprise">Contact Enterprise Sales</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
