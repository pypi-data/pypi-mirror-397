import { Check, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useState } from "react";
import { Link } from "wouter";

const pricingTiers = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Try before you buy",
    features: [
      "5 analyses per month",
      "Basic banned word detection",
      "Cadence scoring",
      "Community support"
    ],
    cta: "Start Free",
    popular: false
  },
  {
    name: "Student",
    price: "$19",
    period: "month",
    description: "Perfect for academic writing",
    features: [
      "Unlimited analyses",
      "Multi-source citation search",
      "APA-7 formatting",
      "Priority support",
      "Export to Word/PDF",
      "Plagiarism detection"
    ],
    cta: "Start 7-Day Trial",
    popular: false
  },
  {
    name: "Pro",
    price: "$99",
    period: "month",
    description: "For power users and developers",
    features: [
      "Everything in Student",
      "API Access (REST + Python SDK)",
      "Bulk operations (100+ docs)",
      "Webhook notifications",
      "Priority queue processing",
      "Usage analytics dashboard"
    ],
    cta: "Start 7-Day Trial",
    popular: true
  },
  {
    name: "Compliance",
    price: "$499",
    period: "month",
    description: "For telehealth providers needing auditability",
    features: [
      "Everything in Pro",
      "Fail-Closed Logic",
      "HMAC Cryptographic Receipts",
      "Policy Snapshot Included",
      "Priority SLA Support",
      "Court-Ready Evidence Packs"
    ],
    cta: "Contact Sales",
    popular: false
  }
];

export function Pricing() {
  const [loading, setLoading] = useState<string | null>(null);

  const handleCheckout = async (tierName: string, priceId: string) => {
    setLoading(tierName);
    try {
      // Determine plan based on tierName or priceId
      const plan = tierName.toLowerCase().includes('compliance') ? 'compliance' : 'free';

      const res = await fetch(`/api/subscribe?plan=${plan}&email=demo@client.com`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer sk_example_demo'
        }
      });

      if (!res.ok) throw new Error('Subscription failed');

      const { checkout_url } = await res.json();
      if (checkout_url) window.location.href = checkout_url;
    } catch (error) {
      console.error(error);
      alert('Checkout failed. Is the backend running?');
    } finally {
      setLoading(null);
    }
  };


  return (
    <section id="pricing" className="py-32 bg-black/20 border-t border-white/5">
      <div className="container px-6">
        <div className="text-center mb-16">
          <span className="text-primary font-mono text-sm tracking-widest uppercase mb-2 block">
            ./Pricing
          </span>
          <h2 className="text-4xl md:text-6xl font-display font-bold mb-4">
            SIMPLE_PRICING
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Start free. Upgrade when you need more. Cancel anytime.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricingTiers.map((tier) => (
            <Card
              key={tier.name}
              className={`p-8 relative ${tier.popular
                ? 'border-primary bg-primary/5'
                  : 'border-white/10 bg-black/40'
                }`}
            >
              {tier.popular && (
                <Badge className="absolute -top-3 left-1/2 -translate-x-1/2 bg-primary text-black">
                  MOST POPULAR
                </Badge>
              )}

              <div className="mb-6">
                <h3 className="text-2xl font-display font-bold mb-2">{tier.name}</h3>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-5xl font-bold">{tier.price}</span>
                  <span className="text-muted-foreground">/{tier.period}</span>
                </div>
                <p className="text-sm text-muted-foreground">{tier.description}</p>
              </div>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-start gap-3 text-sm">
                    <Check className="w-5 h-5 text-primary shrink-0 mt-0.5" />
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Link href="/pricing" className="block">
                <Button
                  className="w-full font-mono uppercase"
                  variant={tier.popular ? "default" : "outline"}
                  data-testid={`button-pricing-${tier.name.toLowerCase()}`}
                >
                  {tier.cta}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </Link>
            </Card>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm text-muted-foreground">
            All plans include 7-day money-back guarantee. No credit card required for free tier.
          </p>
        </div>
      </div>
    </section>
  );
}
