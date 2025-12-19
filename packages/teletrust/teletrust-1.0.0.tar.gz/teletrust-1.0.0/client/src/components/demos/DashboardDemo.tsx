
import { useState, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Brain, Activity, TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { motion } from "framer-motion";

interface TrainingMetrics {
  epoch: number;
  loss: number;
  accuracy: number;
  val_loss?: number;
  val_accuracy?: number;
}

export function DashboardDemo() {
  const [metrics, setMetrics] = useState<TrainingMetrics[]>([]);
  const [isTraining, setIsTraining] = useState(false);
  const [currentEpoch, setCurrentEpoch] = useState(0);

  useEffect(() => {
    // Simulate real-time training updates
    const interval = setInterval(() => {
      if (isTraining && currentEpoch < 50) {
        const newEpoch = currentEpoch + 1;
        const newMetric: TrainingMetrics = {
          epoch: newEpoch,
          loss: 2.5 * Math.exp(-newEpoch * 0.05) + Math.random() * 0.1,
          accuracy: 100 * (1 - Math.exp(-newEpoch * 0.08)) + Math.random() * 2,
          val_loss: 2.5 * Math.exp(-newEpoch * 0.045) + Math.random() * 0.15,
          val_accuracy: 100 * (1 - Math.exp(-newEpoch * 0.075)) + Math.random() * 3,
        };

        setMetrics(prev => [...prev, newMetric]);
        setCurrentEpoch(newEpoch);

        if (newEpoch >= 50) {
          setIsTraining(false);
        }
      }
    }, 500);

    return () => clearInterval(interval);
  }, [isTraining, currentEpoch]);

  const startTraining = () => {
    setMetrics([]);
    setCurrentEpoch(0);
    setIsTraining(true);
  };

  const currentMetrics = metrics[metrics.length - 1];

  return (
    <div className="h-[600px] bg-gradient-to-br from-purple-950/20 to-black text-foreground font-sans flex flex-col">
      <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/[0.02]">
        <div className="flex items-center gap-3">
          <div className="p-1.5 bg-purple-500/10 rounded-md border border-purple-500/20">
            <Brain className="w-4 h-4 text-purple-400" />
          </div>
          <div>
            <h2 className="font-display font-bold text-sm">NEURAL_NEXUS // TRAINING</h2>
            <div className="text-[10px] font-mono text-muted-foreground flex items-center gap-2">
              <span className={`w-1.5 h-1.5 rounded-full ${isTraining ? 'bg-green-500 animate-pulse' : 'bg-gray-500'}`} />
              {isTraining ? `EPOCH ${currentEpoch}/50` : 'READY'}
            </div>
          </div>
        </div>
        <button
          onClick={startTraining}
          disabled={isTraining}
          className="px-4 py-2 bg-purple-500 hover:bg-purple-600 disabled:bg-gray-600 text-white rounded font-mono text-xs uppercase transition-colors"
        >
          {isTraining ? 'Training...' : 'Start Training'}
        </button>
      </div>

      <div className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-4">
          <Card className="p-6 bg-black/40 border-white/10">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-mono text-muted-foreground uppercase">Training Loss</h3>
              {currentMetrics && (
                <span className="text-2xl font-bold text-purple-400">
                  {currentMetrics.loss.toFixed(4)}
                </span>
              )}
            </div>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metrics}>
                  <defs>
                    <linearGradient id="lossGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <XAxis dataKey="epoch" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" fontSize={10} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000', border: '1px solid #333' }}
                    itemStyle={{ fontSize: '12px', fontFamily: 'monospace' }}
                  />
                  <Area type="monotone" dataKey="loss" stroke="#a855f7" strokeWidth={2} fill="url(#lossGradient)" />
                  <Area type="monotone" dataKey="val_loss" stroke="#ec4899" strokeWidth={1} strokeDasharray="5 5" fill="none" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card className="p-6 bg-black/40 border-white/10">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xs font-mono text-muted-foreground uppercase">Accuracy</h3>
              {currentMetrics && (
                <span className="text-2xl font-bold text-green-400">
                  {currentMetrics.accuracy.toFixed(2)}%
                </span>
              )}
            </div>
            <div className="h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={metrics}>
                  <defs>
                    <linearGradient id="accGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#22c55e" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#22c55e" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#333" vertical={false} />
                  <XAxis dataKey="epoch" stroke="#666" fontSize={10} />
                  <YAxis stroke="#666" fontSize={10} domain={[0, 100]} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#000', border: '1px solid #333' }}
                    itemStyle={{ fontSize: '12px', fontFamily: 'monospace' }}
                  />
                  <Area type="monotone" dataKey="accuracy" stroke="#22c55e" strokeWidth={2} fill="url(#accGradient)" />
                  <Area type="monotone" dataKey="val_accuracy" stroke="#10b981" strokeWidth={1} strokeDasharray="5 5" fill="none" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>

        <div className="space-y-4">
          <Card className="p-6 bg-black/40 border-white/10">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="w-4 h-4 text-purple-400" />
              <h3 className="text-xs font-mono text-muted-foreground uppercase">Live Metrics</h3>
            </div>
            <div className="space-y-4">
              {currentMetrics ? (
                <>
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">TRAINING LOSS</div>
                    <div className="text-2xl font-bold text-purple-400">{currentMetrics.loss.toFixed(4)}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">VALIDATION LOSS</div>
                    <div className="text-2xl font-bold text-pink-400">{currentMetrics.val_loss?.toFixed(4)}</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">ACCURACY</div>
                    <div className="text-2xl font-bold text-green-400">{currentMetrics.accuracy.toFixed(2)}%</div>
                  </div>
                  <div>
                    <div className="text-[10px] text-muted-foreground mb-1">VAL ACCURACY</div>
                    <div className="text-2xl font-bold text-emerald-400">{currentMetrics.val_accuracy?.toFixed(2)}%</div>
                  </div>
                </>
              ) : (
                <div className="text-center text-muted-foreground text-xs py-8">
                  Start training to see metrics
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6 bg-black/40 border-white/10">
            <div className="flex items-center gap-2 mb-4">
              <TrendingUp className="w-4 h-4 text-green-400" />
              <h3 className="text-xs font-mono text-muted-foreground uppercase">Progress</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-xs">
                <span>Epochs</span>
                <span className="font-mono">{currentEpoch}/50</span>
              </div>
              <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-purple-500 to-green-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${(currentEpoch / 50) * 100}%` }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
