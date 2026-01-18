import { create } from "zustand";
import type { MaterialDetail, Segment, Practice } from "@/api/client";

interface AppState {
  // Current material being practiced
  currentMaterial: MaterialDetail | null;
  setCurrentMaterial: (material: MaterialDetail | null) => void;

  // Current segment being practiced
  currentSegment: Segment | null;
  setCurrentSegment: (segment: Segment | null) => void;

  // Current practice session
  currentPractice: Practice | null;
  setCurrentPractice: (practice: Practice | null) => void;

  // Recording state
  isRecording: boolean;
  setIsRecording: (recording: boolean) => void;

  // Playback state
  isPlaying: boolean;
  setIsPlaying: (playing: boolean) => void;

  // Playback speed
  playbackSpeed: number;
  setPlaybackSpeed: (speed: number) => void;

  // View mode
  viewMode: "library" | "practice" | "evaluation";
  setViewMode: (mode: "library" | "practice" | "evaluation") => void;
}

export const useAppStore = create<AppState>((set) => ({
  currentMaterial: null,
  setCurrentMaterial: (material) => set({ currentMaterial: material }),

  currentSegment: null,
  setCurrentSegment: (segment) => set({ currentSegment: segment }),

  currentPractice: null,
  setCurrentPractice: (practice) => set({ currentPractice: practice }),

  isRecording: false,
  setIsRecording: (recording) => set({ isRecording: recording }),

  isPlaying: false,
  setIsPlaying: (playing) => set({ isPlaying: playing }),

  playbackSpeed: 1.0,
  setPlaybackSpeed: (speed) => set({ playbackSpeed: speed }),

  viewMode: "library",
  setViewMode: (mode) => set({ viewMode: mode }),
}));
