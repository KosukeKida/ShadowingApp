import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Material {
  id: number;
  title: string;
  source_type: "youtube" | "pdf" | "file";
  source_url: string | null;
  audio_path: string;
  duration: number;
  thumbnail_path: string | null;
  created_at: string;
}

export interface Segment {
  id: number;
  text: string;
  start_time: number;
  end_time: number;
  audio_path: string | null;
  order: number;
}

export interface MaterialDetail extends Material {
  segments: Segment[];
}

export interface Practice {
  id: number;
  segment_id: number;
  recording_path: string;
  transcribed_text: string | null;
  evaluation: Evaluation | null;
  created_at: string;
}

export interface Evaluation {
  accuracy_score: number;
  missing_words: string[];
  added_words: string[];
  pronunciation_notes: string;
  overall_feedback: string;
  strengths: string[];
  areas_to_improve: string[];
}

// API functions
export const materialsApi = {
  list: () => apiClient.get<Material[]>("/api/materials"),
  get: (id: number) => apiClient.get<MaterialDetail>(`/api/materials/${id}`),
  delete: (id: number) => apiClient.delete(`/api/materials/${id}`),
  importYoutube: (url: string) =>
    apiClient.post("/api/materials/youtube", { url }),
  importPdf: (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    return apiClient.post("/api/materials/pdf", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
};

export const practiceApi = {
  getSegmentAudio: (segmentId: number) =>
    `${API_BASE_URL}/api/segments/${segmentId}/audio`,
  uploadRecording: (segmentId: number, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.webm");
    return apiClient.post<Practice>(
      `/api/segments/${segmentId}/practice`,
      formData,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
  },
  getPractice: (id: number) => apiClient.get<Practice>(`/api/practice/${id}`),
  listPractices: (segmentId: number) =>
    apiClient.get<Practice[]>(`/api/segments/${segmentId}/practices`),
  evaluate: (practiceId: number) =>
    apiClient.post<{
      practice_id: number;
      transcribed_text: string;
      original_text: string;
      evaluation: Evaluation;
    }>(`/api/practice/${practiceId}/evaluate`),
};
