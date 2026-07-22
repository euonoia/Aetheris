import { Sparkles, ShieldAlert, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";

interface Insight {
  location: string;
  riskScore: number;
  reasons: string[];
  recommendation: string;
  confidence: number;
}

const insight: Insight = {
  location: "Camarin Rd. corner Zabarte Rd.",
  riskScore: 82,
  reasons: ["Repeated illegal parking incidents", "High traffic density (peak)", "Elevated volume 5:00–7:00 PM"],
  recommendation: "Deploy 2 additional traffic officers",
  confidence: 94,
};

export function AIInsightCard() {
  return (
    <Card className="border-primary/20 bg-gradient-to-b from-primary/[0.04] to-transparent">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-sm">
            <span className="flex h-6 w-6 items-center justify-center rounded-md bg-primary/15 text-primary">
              <Sparkles className="h-3.5 w-3.5" />
            </span>
            AI Road Risk Insight
          </CardTitle>
          <Badge>Beta</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <div className="flex items-end justify-between">
            <p className="text-xs text-muted-foreground">{insight.location}</p>
            <p className="font-display text-xl font-bold text-destructive">{insight.riskScore}%</p>
          </div>
          <Progress value={insight.riskScore} className="mt-1.5 h-1.5 bg-destructive" />
        </div>

        <div className="flex items-start gap-2">
          <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
          <ul className="space-y-1 text-xs text-muted-foreground">
            {insight.reasons.map((r) => (
              <li key={r}>{r}</li>
            ))}
          </ul>
        </div>

        <div className="flex items-center justify-between rounded-md bg-secondary px-3 py-2">
          <div className="flex items-center gap-2">
            <Users className="h-4 w-4 text-primary" />
            <p className="text-xs font-medium">{insight.recommendation}</p>
          </div>
          <span className="text-xs font-semibold text-primary">{insight.confidence}% conf.</span>
        </div>
      </CardContent>
    </Card>
  );
}
