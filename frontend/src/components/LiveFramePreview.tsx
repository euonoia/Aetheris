import type { CSSProperties } from "react";
import type { TrackingSocketMessage } from "../types/api";

interface LiveFramePreviewProps {
  message: TrackingSocketMessage | null;
}

const frameStyle: CSSProperties = {
  width: "100%",
  height: "auto",
  borderRadius: 16,
  background: "#111827",
  objectFit: "contain",
};

function LiveFramePreview({ message }: LiveFramePreviewProps) {
    if (!message) return ;

    const src = `data:image/jpeg;base64,${message.frame}`;

    return (
        <div>
        <h3 style={{ marginTop: 0, color: "#fff" }}>Live Monitor</h3>
        <img src={src} alt="Live annotated frame" style={frameStyle} />
        </div>
    );
}

export default LiveFramePreview;
