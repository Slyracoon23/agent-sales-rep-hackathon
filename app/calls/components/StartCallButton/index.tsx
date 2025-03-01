"use client";

import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import Vapi from "@vapi-ai/web";
import { CallVideoOverlay } from "./VideoOverlay";

const VAPI_PUBLIC_KEY = "e818039e-a962-40a5-a2bc-1b42667cac0e";

export const vapi = new Vapi(VAPI_PUBLIC_KEY);

interface CallContentProps {
  agentId: string;
  type: "bad" | "good";
}

export function StartCallContent({ agentId, type }: CallContentProps) {
  const [isStarted, setIsStarted] = useState(false);
  const [status, setStatus] = useState<"idle" | "connecting" | "active">(
    "idle"
  );
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isStarted && status === "active") {
      interval = setInterval(() => {
        setDuration((d) => d + 1);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isStarted, status]);

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const handleCallToggle = () => {
    if (isStarted) {
      vapi.stop();
      setIsStarted(false);
      setStatus("idle");
      setDuration(0);
    } else {
      setStatus("connecting");
      vapi.start(agentId);
      setIsStarted(true);
      setTimeout(() => setStatus("active"), 1500);
    }
  };

  return (
    <>
      {type === "bad" && (
        <Button
          variant="default"
          className="bg-red-500 hover:bg-red-600 text-white text-4xl p-12"
          onClick={handleCallToggle}
        >
          Bad System Prompt
        </Button>
      )}
      {type === "good" && (
        <Button
          variant="default"
          className="bg-green-500 hover:bg-green-600 text-white text-4xl p-12"
          onClick={handleCallToggle}
        >
          Good System Prompt
        </Button>
      )}
      {isStarted && (
        <CallVideoOverlay
          status={status}
          duration={duration}
          formatDuration={formatDuration}
          isMuted={isMuted}
          setIsMuted={setIsMuted}
          onEndCall={handleCallToggle}
        />
      )}
    </>
  );
}
