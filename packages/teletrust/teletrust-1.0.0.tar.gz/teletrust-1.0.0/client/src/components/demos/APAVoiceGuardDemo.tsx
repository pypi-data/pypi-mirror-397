import { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Search, FileText, AlertTriangle, Check, BookOpen, Activity, RefreshCw } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { DialogTitle } from "@/components/ui/dialog";
import { VisuallyHidden } from "@radix-ui/react-visually-hidden";

// Actual banned words from your Python codebase
const BANNED_WORDS = [
  "signal", "streamline", "streamlined", "tighten", "mitigate",
  "facilitate", "leverage", "safety work", "link", "linked", "linking",
  "clarify", "clarifies", "clarifying", "centering", "centered", "center",
  "frame", "framing", "rung", "stepwise", "taken together", "together",
  "anchor", "anchoring", "huddle", "trajectory", "guide", "guides", "guideposts",
  "game changer", "whole nine yards", "kind of", "sort of", "pretty much",
  "in conclusion", "to conclude", "this post", "this paper", "this discussion",
  "this essay", "arguably", "very", "really", "etc", "and so on", "and so forth",
  "crucial", "robust", "utilize", "utilization", "optimize", "synergy",
  "impactful", "stakeholder", "paradigm", "holistic", "proactive"
];

interface Citation {
  id: string;
  title: string;
  author: string;
  year: number;
  source: "PubMed" | "OpenAlex";
}

export function APAVoiceGuardDemo() {
  const [text, setText] = useState("The goal of this paper is to utilize a robust framework to leverage existing synergies. In conclusion, this streamlined approach will facilitate better outcomes.");
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState<{ score: number; foundWords: string[] } | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    setReport(null);

    try {
      // Call real backend API
      const response = await fetch('/api/apa/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      });

      if (!response.ok) {
        throw new Error('Analysis failed');
      }

      const data = await response.json();

      setReport({
        score: data.score,
        foundWords: data.bannedWords
      });

      // Optional: Search for citations if user has entered a topic
      if (text.length > 100) {
        const searchResponse = await fetch('/api/apa/search-citations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: text.split(' ').slice(0, 5).join(' '),
            maxResults: 3
          })
        });

        if (searchResponse.ok) {
          const searchData = await searchResponse.json();
          setCitations(searchData.citations.map((c: any) => ({
            id: c.id,
            title: c.title,
            author: c.authors.join(', '),
            year: c.year,
            source: c.source
          })));
        }
      }

    } catch (error) {
      console.error('Analysis error:', error);
      alert('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const highlightText = (inputText: string, wordsToHighlight: string[]) => {
    if (!wordsToHighlight.length) return inputText;
    const regex = new RegExp(`\\b(${wordsToHighlight.join('|')})\\b`, 'gi');
    return inputText.split(regex).map((part, i) =>
      wordsToHighlight.some(w => w.toLowerCase() === part.toLowerCase()) ?
      <span key={i} className="bg-red-500/30 text-red-200 border-b border-red-500 px-1 rounded-sm">{part}</span> :
      part
    );
  };

  return (
    <div className="flex flex-col h-[600px] bg-black text-foreground font-sans selection:bg-primary selection:text-black">
      <div className="p-4 border-b border-white/10 flex items-center justify-between bg-white/5">
        <div className="flex items-center gap-2">
          <BookOpen className="w-5 h-5 text-primary" />
          <h2 className="font-display font-bold">APA_VOICE_GUARD // v2.0</h2>
        </div>
        <div className="flex items-center gap-3">
           <div className="flex items-center gap-2 text-[10px] font-mono text-muted-foreground uppercase">
             <div className={`w-2 h-2 rounded-full ${analyzing ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`} />
             {analyzing ? 'PROCESSING...' : 'SYSTEM READY'}
           </div>
           <Badge variant="outline" className="border-primary/50 text-primary bg-primary/10 font-mono">
             LIVE AUDIT
           </Badge>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Editor Pane */}
        <div className="flex-1 p-6 border-r border-white/10 flex flex-col gap-4 relative group">
          <div className="absolute inset-0 bg-grid-white/[0.02] pointer-events-none" />

          <div className="flex justify-between items-center z-10">
             <label className="text-xs font-mono text-muted-foreground uppercase flex items-center gap-2">
               <FileText className="w-3 h-3" /> Input Buffer
             </label>
             <span className="text-xs font-mono text-white/40">{text.length} chars</span>
          </div>

          <div className="relative flex-1 font-mono text-sm bg-black/50 border border-white/10 rounded-md p-4 focus-within:ring-1 focus-within:ring-primary/50 transition-all">
             {report ? (
               <div className="absolute inset-0 p-4 whitespace-pre-wrap break-words pointer-events-none text-transparent/0">
                 {/* This layer is just for matching layout if we wanted rich text editing overlay,
                     but for now we'll just show the textarea or the results */}
               </div>
             ) : null}
             <textarea
               value={text}
               onChange={(e) => setText(e.target.value)}
               placeholder="Paste academic text..."
               className="w-full h-full bg-transparent border-none outline-none resize-none placeholder:text-white/20"
               spellCheck={false}
             />
          </div>

          <div className="flex justify-between items-center z-10">
             <div className="text-[10px] text-white/30 font-mono">
               Database: PubMed, OpenAlex, SemanticScholar
             </div>
             <Button onClick={handleAnalyze} disabled={analyzing || !text} className="bg-primary text-black font-bold uppercase tracking-wide hover:bg-white transition-colors">
               {analyzing ? (
                 <>
                   <Activity className="w-4 h-4 mr-2 animate-spin" /> Analyzing
                 </>
               ) : (
                 <>
                   <Search className="w-4 h-4 mr-2" /> Run Audit
                 </>
               )}
             </Button>
          </div>
        </div>

        {/* Results Pane */}
        <div className="w-[350px] bg-[#0a0a0a] border-l border-white/10 flex flex-col">
          <div className="p-4 border-b border-white/10 bg-white/5">
             <h3 className="font-mono text-xs text-muted-foreground uppercase">Compliance Report</h3>
          </div>

          <div className="p-6 overflow-y-auto flex-1">
            <AnimatePresence mode="wait">
              {!report ? (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex flex-col items-center justify-center h-full text-muted-foreground text-center opacity-40"
                >
                  <Activity className="w-12 h-12 mb-4" />
                  <p className="font-mono text-xs uppercase">Awaiting Input Stream</p>
                </motion.div>
              ) : (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  {/* Score Card */}
                  <Card className="p-4 bg-black border-white/10 relative overflow-hidden group">
                    <div className={`absolute inset-0 opacity-20 ${report.score > 80 ? 'bg-green-500/20' : 'bg-red-500/20'}`} />
                    <div className="relative z-10">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-xs font-mono text-muted-foreground">ADHERENCE SCORE</span>
                        <Badge variant="outline" className={report.score > 80 ? "border-green-500 text-green-500" : "border-red-500 text-red-500"}>
                          {report.score > 80 ? "PASSING" : "FLAGGED"}
                        </Badge>
                      </div>
                      <div className="text-5xl font-display font-bold text-white tracking-tighter">
                        {report.score}<span className="text-2xl text-muted-foreground">/100</span>
                      </div>
                    </div>
                  </Card>

                  {/* Detected Issues */}
                  <div>
                     <div className="flex items-center justify-between mb-3">
                       <div className="flex items-center gap-2 text-xs font-mono text-white/60">
                         <AlertTriangle className="w-3 h-3 text-yellow-500" />
                         DETECTED VIOLATIONS ({report.foundWords.length})
                       </div>
                     </div>

                     {report.foundWords.length > 0 ? (
                       <div className="flex flex-wrap gap-2">
                         {report.foundWords.map((word, i) => (
                           <motion.div
                             key={i}
                             initial={{ scale: 0 }}
                             animate={{ scale: 1 }}
                             transition={{ delay: i * 0.05 }}
                           >
                             <Badge variant="destructive" className="font-mono text-xs bg-red-500/10 text-red-400 border-red-500/30 hover:bg-red-500/20">
                               {word}
                             </Badge>
                           </motion.div>
                         ))}
                       </div>
                     ) : (
                       <div className="text-xs font-mono text-green-500 flex items-center gap-2">
                         <Check className="w-3 h-3" /> No banned patterns found.
                       </div>
                     )}
                  </div>

                  {/* Context Preview */}
                  {report.foundWords.length > 0 && (
                    <div className="p-3 rounded bg-white/5 border border-white/10 text-xs font-mono text-muted-foreground leading-relaxed">
                      {highlightText(text, report.foundWords)}
                    </div>
                  )}

                  {/* Citations */}
                  <div className="pt-4 border-t border-white/10">
                     <div className="flex items-center gap-2 mb-3 text-xs font-mono text-primary">
                       <BookOpen className="w-3 h-3" /> SUGGESTED CITATIONS
                     </div>
                     <div className="space-y-2">
                       {citations.map((cite, i) => (
                         <motion.div
                           key={cite.id}
                           initial={{ opacity: 0, y: 10 }}
                           animate={{ opacity: 1, y: 0 }}
                           transition={{ delay: 0.2 + (i * 0.1) }}
                           className="p-3 bg-black border border-white/10 rounded hover:border-primary/50 transition-colors cursor-pointer group"
                         >
                           <div className="font-bold text-white group-hover:text-primary truncate text-xs mb-1">{cite.title}</div>
                           <div className="flex justify-between items-center">
                             <span className="text-[10px] text-muted-foreground">{cite.author}, {cite.year}</span>
                             <Badge variant="secondary" className="text-[9px] h-4 px-1 rounded-sm">{cite.source}</Badge>
                           </div>
                         </motion.div>
                       ))}
                     </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
}
