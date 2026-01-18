import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { materialsApi, practiceApi } from "@/api/client";
import { WaveformPlayer } from "./WaveformPlayer";
import { Recorder } from "./Recorder";
import { EvaluationResult } from "./EvaluationResult";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ArrowLeft, ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface PracticeViewProps {
  materialId: number;
  onBack: () => void;
}

export function PracticeView({ materialId, onBack }: PracticeViewProps) {
  const [currentSegmentIndex, setCurrentSegmentIndex] = useState(0);
  const [playbackSpeed, setPlaybackSpeed] = useState(1.0);

  const { data: material, isLoading } = useQuery({
    queryKey: ["material", materialId],
    queryFn: () => materialsApi.get(materialId).then((res) => res.data),
  });

  const uploadMutation = useMutation({
    mutationFn: ({
      segmentId,
      blob,
    }: {
      segmentId: number;
      blob: Blob;
    }) => practiceApi.uploadRecording(segmentId, blob),
  });

  const evaluateMutation = useMutation({
    mutationFn: (practiceId: number) => practiceApi.evaluate(practiceId),
  });

  const handleRecordingComplete = async (blob: Blob) => {
    if (!currentSegment) return;

    const uploadResult = await uploadMutation.mutateAsync({
      segmentId: currentSegment.id,
      blob,
    });

    // Automatically evaluate after upload
    await evaluateMutation.mutateAsync(uploadResult.data.id);
  };

  if (isLoading || !material) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  const currentSegment = material.segments[currentSegmentIndex];
  const hasNext = currentSegmentIndex < material.segments.length - 1;
  const hasPrev = currentSegmentIndex > 0;

  const speedOptions = [0.5, 0.75, 1.0, 1.25, 1.5];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h2 className="text-xl font-semibold">{material.title}</h2>
          <p className="text-sm text-muted-foreground">
            Segment {currentSegmentIndex + 1} of {material.segments.length}
          </p>
        </div>
      </div>

      {/* Segment Navigation */}
      <div className="flex items-center justify-center gap-4">
        <Button
          variant="outline"
          size="icon"
          onClick={() => setCurrentSegmentIndex((i) => i - 1)}
          disabled={!hasPrev}
        >
          <ChevronLeft className="h-5 w-5" />
        </Button>
        <div className="flex gap-1">
          {material.segments.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentSegmentIndex(index)}
              className={cn(
                "w-2 h-2 rounded-full transition-colors",
                index === currentSegmentIndex
                  ? "bg-primary"
                  : "bg-muted hover:bg-muted-foreground/30"
              )}
            />
          ))}
        </div>
        <Button
          variant="outline"
          size="icon"
          onClick={() => setCurrentSegmentIndex((i) => i + 1)}
          disabled={!hasNext}
        >
          <ChevronRight className="h-5 w-5" />
        </Button>
      </div>

      {/* Script */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Script</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-lg leading-relaxed">{currentSegment?.text}</p>
        </CardContent>
      </Card>

      {/* Audio Player */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-lg">Model Audio</CardTitle>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Speed:</span>
              {speedOptions.map((speed) => (
                <Button
                  key={speed}
                  variant={playbackSpeed === speed ? "default" : "outline"}
                  size="sm"
                  onClick={() => setPlaybackSpeed(speed)}
                >
                  {speed}x
                </Button>
              ))}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <WaveformPlayer
            audioUrl={practiceApi.getSegmentAudio(currentSegment.id)}
            playbackSpeed={playbackSpeed}
            startTime={currentSegment.start_time}
            endTime={currentSegment.end_time}
          />
        </CardContent>
      </Card>

      {/* Recording */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Your Recording</CardTitle>
        </CardHeader>
        <CardContent>
          <Recorder
            onRecordingComplete={handleRecordingComplete}
            isUploading={uploadMutation.isPending || evaluateMutation.isPending}
          />
        </CardContent>
      </Card>

      {/* Evaluation Result */}
      {evaluateMutation.data && (
        <EvaluationResult
          originalText={evaluateMutation.data.data.original_text}
          transcribedText={evaluateMutation.data.data.transcribed_text}
          evaluation={evaluateMutation.data.data.evaluation}
        />
      )}
    </div>
  );
}
