import { Link } from "wouter";
import { CheckCircle, ArrowRight, Cpu, Mail, Download, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function SuccessPage() {
  return (
    <div className="min-h-screen bg-black text-white flex items-center justify-center p-6">
      <div className="absolute inset-0 grid-pattern opacity-10 pointer-events-none" />

      <Card className="max-w-lg w-full p-8 border-primary/20 bg-[#0a0a0a] text-center relative z-10">
        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-primary/20 flex items-center justify-center">
          <CheckCircle className="w-10 h-10 text-primary" />
        </div>

        <h1 className="text-3xl font-display font-bold mb-2">
          PAYMENT_SUCCESSFUL
        </h1>
        <p className="text-muted-foreground mb-8">
          Welcome to Sentinel OS. Your subscription is now active.
        </p>

        <div className="space-y-4 text-left mb-8">
          <div className="flex items-start gap-4 p-4 bg-white/5 rounded-lg border border-white/10">
            <Mail className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-sm">Check Your Email</h3>
              <p className="text-xs text-muted-foreground">
                We've sent you a confirmation email with your login credentials and setup instructions.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 bg-white/5 rounded-lg border border-white/10">
            <Download className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-sm">Download Your Invoice</h3>
              <p className="text-xs text-muted-foreground">
                Your invoice has been emailed and is also available in your Stripe customer portal.
              </p>
            </div>
          </div>

          <div className="flex items-start gap-4 p-4 bg-white/5 rounded-lg border border-white/10">
            <BookOpen className="w-5 h-5 text-primary shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold text-sm">Getting Started Guide</h3>
              <p className="text-xs text-muted-foreground">
                Access our documentation to learn how to integrate Sentinel into your workflow.
              </p>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <Link href="/platform" className="block">
            <Button className="w-full font-mono uppercase" data-testid="button-go-to-platform" asChild>
              <span>
                Launch Sentinel OS
                <ArrowRight className="w-4 h-4 ml-2" />
              </span>
            </Button>
          </Link>

          <Link href="/" className="block">
            <Button variant="ghost" className="w-full font-mono text-sm text-muted-foreground" asChild>
              <span>Return to Homepage</span>
            </Button>
          </Link>
        </div>

        <div className="mt-8 pt-6 border-t border-white/10">
          <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
            <Cpu className="w-4 h-4 text-primary" />
            <span>Powered by SENTINEL<span className="text-primary">_OS</span></span>
          </div>
        </div>
      </Card>
    </div>
  );
}
