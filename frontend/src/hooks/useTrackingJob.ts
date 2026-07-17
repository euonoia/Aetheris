import { useEffect, useRef, useState } from "react";
import { getTrackingStatus, trackVideo } from "../services/api";
import type { TrackingStatusResponse } from "../types/api";

const POLL_INTERVAL_MS = 1000;

/**
 * Polls tracking job status until the backend marks it completed or failed.
 *
 * Job lifecycle on the client:
 * 1. Upload video -> receive job_id
 * 2. Poll /tracking-status/{job_id} every second
 * 3. Stop polling when status is completed or failed
 */
export function useTrackingJob() {
  const [status, setStatus] = useState<TrackingStatusResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  const stopPolling = () => {
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  };

  const startTracking = async (file: File, threshold: number) => {
    setLoading(true);
    setStatus(null);
    stopPolling();

    const { data } = await trackVideo(file, threshold);
    const jobId = data.job_id;
    setJobId(jobId);

    const pollStatus = async () => {
      const { data: jobStatus } = await getTrackingStatus(jobId);
      setStatus(jobStatus);

      if (jobStatus.status === "completed" || jobStatus.status === "failed") {
        stopPolling();
        setLoading(false);
      }
    };

    await pollStatus();
    intervalRef.current = window.setInterval(pollStatus, POLL_INTERVAL_MS);
  };

  useEffect(() => () => stopPolling(), []);

  return { status, loading, jobId, startTracking };
}
