import { useEffect, useRef } from "react";
import type { CSSProperties } from "react";
import type { TrackingSocketMessage } from "../types/api";

interface LiveFramePreviewProps {
  message: TrackingSocketMessage | null;
}

const canvasStyle: CSSProperties = {
    width: "100%",
    height: "auto",
    borderRadius: 16,
    background: "#111827",
    display: "block",
};

function LiveFramePreview({ message }: LiveFramePreviewProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        if (!message || !canvasRef.current) return;

        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        if (!ctx) return;

        const image = new Image();

        image.onload = () => {
            // Match canvas resolution to the incoming frame
            canvas.width = image.width;
            canvas.height = image.height;

            ctx.drawImage(image, 0, 0);
        };

        image.src = `data:image/jpeg;base64,${message.frame}`;
    }, [message]);

    return (
        <div>
            <h3 style={{ marginTop: 0, color: "#fff" }}>Live Monitor</h3>

            <canvas
                ref={canvasRef}
                style={canvasStyle}
            />
        </div>
    );    
}

export default LiveFramePreview;