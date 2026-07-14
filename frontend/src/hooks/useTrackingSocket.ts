import { useEffect, useRef, useState } from "react";
import { getTrackingSocketUrl } from "../services/api";
import type { TrackingSocketMessage } from "../types/api";

const MAX_RECONNECT_DELAY_MS = 5000;

export function useTrackingSocket(jobId: string | null) {
  const [message, setMessage] = useState<TrackingSocketMessage | null>(null);
  const [connectionState, setConnectionState] = useState<"connecting" | "open" | "closed" | "error">("closed");
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const shouldReconnectRef = useRef(false);

  const cleanUp = () => {
    shouldReconnectRef.current = false;
    if (reconnectTimerRef.current !== null) {
      window.clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
  };

  useEffect(() => {
    if (!jobId) {
      cleanUp();
      setConnectionState("closed");
      setReconnectAttempts(0);
      setMessage(null);
      return;
    }

    shouldReconnectRef.current = true;

    const connect = () => {
      setConnectionState("connecting");
      const url = getTrackingSocketUrl(jobId);
      const socket = new WebSocket(url);
      socketRef.current = socket;

      socket.onopen = () => {
        setConnectionState("open");
        setReconnectAttempts(0);
      };

      socket.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data) as TrackingSocketMessage;
          setMessage(payload);
        } catch {
          // Ignore invalid websocket payloads.
        }
      };

      socket.onerror = () => {
        setConnectionState("error");
      };

      socket.onclose = (event) => {
        setConnectionState("closed");
        socketRef.current = null;
        if (shouldReconnectRef.current && event.code !== 1000) {
          const delay = Math.min(1000 * (reconnectAttempts + 1), MAX_RECONNECT_DELAY_MS);
          reconnectTimerRef.current = window.setTimeout(() => {
            setReconnectAttempts((attempts) => attempts + 1);
            connect();
          }, delay);
        }
      };
    };

    connect();

    return () => {
      cleanUp();
    };
  }, [jobId]);

  return {
    message,
    connectionState,
    reconnectAttempts,
    closeSocket: cleanUp,
  };
}
