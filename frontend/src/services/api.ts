import axios from "axios";
import type { TrackVideoJobResponse, TrackingStatusResponse } from "../types/api";

export const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export const getTrackingSocketUrl = (jobId: string) => {
  const host = "localhost:8000";
  return `ws://${host}/ws/tracking/${jobId}`;
};

export const detectImage = async (file: File, threshold: number) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("threshold", String(threshold));

  return api.post("/detect-image", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const detectVideo = async (file: File, threshold: number) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("threshold", String(threshold));

  return api.post("/detect-video", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const trackVideo = async (file: File, threshold: number) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("threshold", String(threshold));

  return api.post<TrackVideoJobResponse>("/track-video", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getTrackingStatus = async (jobId: string) => {
  return api.get<TrackingStatusResponse>(`/tracking-status/${jobId}`);
};
