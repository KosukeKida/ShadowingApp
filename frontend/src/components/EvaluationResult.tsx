import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle, XCircle, AlertCircle, TrendingUp } from "lucide-react";
import { cn } from "@/lib/utils";
import type { Evaluation } from "@/api/client";

interface EvaluationResultProps {
  originalText: string;
  transcribedText: string;
  evaluation: Evaluation;
}

export function EvaluationResult({
  originalText,
  transcribedText,
  evaluation,
}: EvaluationResultProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600";
    if (score >= 60) return "text-yellow-600";
    return "text-red-600";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return "bg-green-100";
    if (score >= 60) return "bg-yellow-100";
    return "bg-red-100";
  };

  return (
    <div className="space-y-4">
      {/* Score */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Accuracy Score</span>
            <span
              className={cn(
                "text-3xl font-bold",
                getScoreColor(evaluation.accuracy_score)
              )}
            >
              {evaluation.accuracy_score}%
            </span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-muted rounded-full h-3">
            <div
              className={cn(
                "h-3 rounded-full transition-all",
                getScoreBgColor(evaluation.accuracy_score),
                getScoreColor(evaluation.accuracy_score).replace("text-", "bg-")
              )}
              style={{ width: `${evaluation.accuracy_score}%` }}
            />
          </div>
        </CardContent>
      </Card>

      {/* Comparison */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Original Text
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{originalText}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Your Transcription
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm">{transcribedText}</p>
          </CardContent>
        </Card>
      </div>

      {/* Feedback */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Feedback</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Overall Feedback */}
          <p className="text-muted-foreground">{evaluation.overall_feedback}</p>

          {/* Strengths */}
          {evaluation.strengths.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 font-medium text-green-600 mb-2">
                <CheckCircle className="h-4 w-4" />
                Strengths
              </h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {evaluation.strengths.map((strength, i) => (
                  <li key={i}>{strength}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Areas to Improve */}
          {evaluation.areas_to_improve.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 font-medium text-orange-600 mb-2">
                <TrendingUp className="h-4 w-4" />
                Areas to Improve
              </h4>
              <ul className="list-disc list-inside space-y-1 text-sm">
                {evaluation.areas_to_improve.map((area, i) => (
                  <li key={i}>{area}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Missing Words */}
          {evaluation.missing_words.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 font-medium text-red-600 mb-2">
                <XCircle className="h-4 w-4" />
                Missing Words
              </h4>
              <div className="flex flex-wrap gap-2">
                {evaluation.missing_words.map((word, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-red-100 text-red-700 rounded text-sm"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Added Words */}
          {evaluation.added_words.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 font-medium text-yellow-600 mb-2">
                <AlertCircle className="h-4 w-4" />
                Extra Words
              </h4>
              <div className="flex flex-wrap gap-2">
                {evaluation.added_words.map((word, i) => (
                  <span
                    key={i}
                    className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-sm"
                  >
                    {word}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Pronunciation Notes */}
          {evaluation.pronunciation_notes && (
            <div className="pt-2 border-t">
              <h4 className="font-medium mb-2">Pronunciation Notes</h4>
              <p className="text-sm text-muted-foreground">
                {evaluation.pronunciation_notes}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
