"use client";

import { Button } from "@/components/ui/button";
import { useCallback, useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import {
  Mic,
  MicOff,
  MonitorUp,
  PhoneOff,
  Video,
  VideoOff,
} from "lucide-react";

interface CallVideoOverlayProps {
  status: "idle" | "connecting" | "active";
  duration: number;
  formatDuration: (seconds: number) => string;
  isMuted: boolean;
  setIsMuted: (muted: boolean) => void;
  onEndCall: () => void;
}

export function CallVideoOverlay({
  status,
  duration,
  formatDuration,
  isMuted,
  setIsMuted,
  onEndCall,
}: CallVideoOverlayProps) {
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [screenStream, setScreenStream] = useState<MediaStream | null>(null);
  const [screenShareError, setScreenShareError] = useState<string | null>(null);
  const [isLayoutShifted, setIsLayoutShifted] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const screenVideoRef = useRef<HTMLVideoElement>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);

  const toggleCamera = useCallback(async () => {
    if (!isCameraOn) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true,
        });
        setCameraStream(stream);
        setIsCameraOn(true);
        setCameraError(null);
      } catch (err: any) {
        console.error("Error accessing camera:", err);
        setCameraError(err.message || "Unable to access camera");
      }
    } else {
      cameraStream?.getTracks().forEach((track) => track.stop());
      setCameraStream(null);
      setIsCameraOn(false);
    }
  }, [isCameraOn, cameraStream]);

  const toggleScreenShare = useCallback(async () => {
    if (!isScreenSharing) {
      try {
        const stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
        });
        stream.getVideoTracks()[0].addEventListener("ended", () => {
          setScreenStream(null);
          setIsScreenSharing(false);
          setIsLayoutShifted(false);
        });
        if (isCameraOn) await toggleCamera();
        setScreenStream(stream);
        setIsScreenSharing(true);
        setScreenShareError(null);
        setTimeout(() => setIsLayoutShifted(true), 50);
      } catch (err: any) {
        console.error("Error accessing screen:", err);
        setScreenShareError(err.message || "Unable to start screen sharing");
      }
    } else {
      screenStream?.getTracks().forEach((track) => track.stop());
      setScreenStream(null);
      setIsScreenSharing(false);
      setIsLayoutShifted(false);
      if (!isCameraOn) await toggleCamera();
    }
  }, [isScreenSharing, screenStream, isCameraOn, toggleCamera]);

  useEffect(() => {
    if (!isCameraOn) toggleCamera();
  }, [isCameraOn, toggleCamera]);

  useEffect(() => {
    if (videoRef.current) videoRef.current.srcObject = cameraStream;
  }, [cameraStream]);

  useEffect(() => {
    if (screenVideoRef.current) screenVideoRef.current.srcObject = screenStream;
  }, [screenStream]);

  useEffect(() => {
    return () => {
      cameraStream?.getTracks().forEach((track) => track.stop());
      screenStream?.getTracks().forEach((track) => track.stop());
    };
  }, [cameraStream, screenStream]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key.toLowerCase() === "s") {
        e.preventDefault();
        toggleScreenShare();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [toggleScreenShare]);

  return (
    <div className="fixed inset-0 bg-black/95 z-50 flex items-center justify-center overflow-hidden">
      {!isScreenSharing && (
        <div className="flex flex-col items-center space-y-4">
          <h2 className="text-white text-2xl font-medium">
            {"Bad System Prompt"}
          </h2>
          <p className="text-white/60">
            {status === "connecting"
              ? "Connecting..."
              : formatDuration(duration)}
          </p>
        </div>
      )}

      {isScreenSharing && (
        <div className="absolute inset-0 transition-all duration-500 ease-in-out transform scale-95 rounded-md overflow-clip">
          <div className="relative w-full h-full">
            <video
              ref={screenVideoRef}
              className="w-full h-full object-contain border-2"
              autoPlay
              playsInline
            />
            <div className="absolute top-4 left-1/2 -translate-x-1/2 px-4 py-2 bg-black/90 text-white text-sm rounded-full flex items-center gap-2 shadow-lg backdrop-blur-sm">
              <MonitorUp className="h-4 w-4" />
              <span>Screen shared</span>
            </div>
          </div>
        </div>
      )}

      {isCameraOn && (
        <div className="absolute right-2 bottom-2 w-96 h-96 rounded-lg overflow-hidden shadow-lg ring-1 ring-white/20 bg-black/50 backdrop-blur-sm transition-all duration-300 hover:ring-white/40">
          <video
            ref={videoRef}
            className="w-full h-full object-cover scale-x-[-1]"
            autoPlay
            playsInline
            muted
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />
          <div className="absolute top-2 left-2 text-xs text-white/80 font-medium">
            Me
          </div>
        </div>
      )}

      <div
        className={cn(
          "fixed bottom-12 flex items-center gap-4 transition-all duration-500",
          isLayoutShifted
            ? "right-[200px] -translate-x-1/2"
            : "left-1/2 -translate-x-1/2"
        )}
      >
        <Button
          variant="outline"
          size="icon"
          className="rounded-full h-14 w-14 bg-white/10 border-0 hover:bg-white/20"
          onClick={() => setIsMuted(!isMuted)}
        >
          {isMuted ? (
            <MicOff className="h-6 w-6 text-white" />
          ) : (
            <Mic className="h-6 w-6 text-white" />
          )}
        </Button>

        <Button
          variant="outline"
          size="icon"
          className="rounded-full h-14 w-14 bg-white/10 border-0 hover:bg-white/20"
          onClick={toggleCamera}
        >
          {isCameraOn ? (
            <VideoOff className="h-6 w-6 text-white" />
          ) : (
            <Video className="h-6 w-6 text-white" />
          )}
        </Button>

        <Button
          variant="outline"
          size="icon"
          className={cn(
            "rounded-full h-14 w-14 border-0 transition-colors duration-300 relative group",
            isScreenSharing
              ? "bg-red-500/20 hover:bg-red-500/30"
              : "bg-white/10 hover:bg-white/20"
          )}
          onClick={toggleScreenShare}
          title={
            isScreenSharing ? "Stop sharing (Alt+S)" : "Share screen (Alt+S)"
          }
        >
          <MonitorUp
            className={cn(
              "h-6 w-6 transition-colors duration-300",
              isScreenSharing ? "text-red-500" : "text-white"
            )}
          />
          <div className="absolute -top-10 left-1/2 -translate-x-1/2 px-2 py-1 bg-black/90 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 whitespace-nowrap pointer-events-none">
            {isScreenSharing ? "Stop sharing (Alt+S)" : "Share screen (Alt+S)"}
          </div>
        </Button>

        <Button
          className="rounded-full h-14 w-14 bg-red-600 hover:bg-red-700"
          size="icon"
          onClick={onEndCall}
        >
          <PhoneOff className="h-6 w-6" />
        </Button>
      </div>

      {cameraError && (
        <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-red-500/90 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg backdrop-blur-sm">
          {cameraError}
        </div>
      )}
      {screenShareError && (
        <div className="absolute top-16 left-1/2 -translate-x-1/2 bg-red-500/90 text-white px-4 py-2 rounded-full text-sm font-medium shadow-lg backdrop-blur-sm">
          {screenShareError}
        </div>
      )}

      <div className="absolute bottom-4 right-4 w-64 h-48 rounded-md shadow-lg overflow-hidden z-50">
        <video
          ref={localVideoRef}
          autoPlay
          muted
          className="w-full h-full object-cover"
        />
      </div>
    </div>
  );
}
