import { useEffect, useRef, useState } from "react";
import WaveSurfer from "wavesurfer.js";
import RegionsPlugin from "wavesurfer.js/dist/plugins/regions.js";
import { Button } from "@/components/ui/button";
import { Play, Pause, RotateCcw } from "lucide-react";
import { cn } from "@/lib/utils";

interface WaveformPlayerProps {
  audioUrl: string;
  playbackSpeed?: number;
  startTime?: number;
  endTime?: number;
  onPlayStateChange?: (isPlaying: boolean) => void;
  onTimeUpdate?: (currentTime: number) => void;
  className?: string;
  waveColor?: string;
  progressColor?: string;
}

export function WaveformPlayer({
  audioUrl,
  playbackSpeed = 1.0,
  startTime,
  endTime,
  onPlayStateChange,
  onTimeUpdate,
  className,
  waveColor = "#3b82f6",
  progressColor = "#1d4ed8",
}: WaveformPlayerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const regionsRef = useRef<RegionsPlugin | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isReady, setIsReady] = useState(false);

  // Check if we have a segment region
  const hasRegion = startTime !== undefined && endTime !== undefined;

  useEffect(() => {
    if (!containerRef.current) return;

    // Create regions plugin
    const regions = RegionsPlugin.create();
    regionsRef.current = regions;

    const wavesurfer = WaveSurfer.create({
      container: containerRef.current,
      waveColor: waveColor,
      progressColor: progressColor,
      cursorColor: "#1e40af",
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 80,
      normalize: true,
      plugins: [regions],
    });

    wavesurferRef.current = wavesurfer;

    wavesurfer.load(audioUrl);

    wavesurfer.on("ready", () => {
      const totalDuration = wavesurfer.getDuration();

      if (hasRegion && startTime !== undefined && endTime !== undefined) {
        // For segments with start/end time, set duration to segment length
        setDuration(endTime - startTime);

        // Create a visual region for the segment
        regions.addRegion({
          start: startTime,
          end: endTime,
          color: "rgba(59, 130, 246, 0.2)",
          drag: false,
          resize: false,
        });

        // Seek to start of segment
        wavesurfer.seekTo(startTime / totalDuration);
      } else {
        setDuration(totalDuration);
      }

      setIsReady(true);
    });

    wavesurfer.on("play", () => {
      setIsPlaying(true);
      onPlayStateChange?.(true);
    });

    wavesurfer.on("pause", () => {
      setIsPlaying(false);
      onPlayStateChange?.(false);
    });

    wavesurfer.on("audioprocess", () => {
      const time = wavesurfer.getCurrentTime();

      if (hasRegion && startTime !== undefined && endTime !== undefined) {
        // Display time relative to segment start
        setCurrentTime(Math.max(0, time - startTime));

        // Stop at end of segment
        if (time >= endTime) {
          wavesurfer.pause();
          wavesurfer.seekTo(startTime / wavesurfer.getDuration());
          setIsPlaying(false);
          onPlayStateChange?.(false);
        }
      } else {
        setCurrentTime(time);
      }

      onTimeUpdate?.(time);
    });

    wavesurfer.on("finish", () => {
      setIsPlaying(false);
      onPlayStateChange?.(false);
    });

    return () => {
      wavesurfer.destroy();
    };
  }, [audioUrl, startTime, endTime]);

  useEffect(() => {
    if (wavesurferRef.current) {
      wavesurferRef.current.setPlaybackRate(playbackSpeed);
    }
  }, [playbackSpeed]);

  const togglePlayPause = () => {
    if (!wavesurferRef.current || !isReady) return;

    if (hasRegion && startTime !== undefined) {
      const currentPos = wavesurferRef.current.getCurrentTime();
      const totalDuration = wavesurferRef.current.getDuration();

      // If not playing and we're outside the region, seek to start first
      if (!isPlaying && (currentPos < startTime || (endTime && currentPos >= endTime))) {
        wavesurferRef.current.seekTo(startTime / totalDuration);
      }
    }

    wavesurferRef.current.playPause();
  };

  const restart = () => {
    if (!wavesurferRef.current || !isReady) return;

    const totalDuration = wavesurferRef.current.getDuration();

    if (hasRegion && startTime !== undefined) {
      // Restart from segment start
      wavesurferRef.current.seekTo(startTime / totalDuration);
    } else {
      wavesurferRef.current.seekTo(0);
    }

    wavesurferRef.current.play();
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className={cn("space-y-2", className)}>
      <div ref={containerRef} className="bg-muted/30 rounded-lg p-2" />
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={togglePlayPause}
            disabled={!isReady}
          >
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={restart}
            disabled={!isReady}
          >
            <RotateCcw className="h-4 w-4" />
          </Button>
        </div>
        <div className="text-sm text-muted-foreground">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>
    </div>
  );
}
