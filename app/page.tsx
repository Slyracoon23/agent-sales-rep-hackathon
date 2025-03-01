"use client";

import { StartCallContent } from "./calls/components/StartCallButton";

const VAPI_AGENT_ID1 = "6e1b2494-d500-4e26-8975-42b4d8985814";
const VAPI_AGENT_ID2 = "d6840c2a-715f-4b0a-a0e7-13ab2e3770fd";

export default function CallsPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-blue-100 p-4">
      <div className="bg-white shadow-md rounded-lg p-6 m-4 gap-8 flex">
        <StartCallContent agentId={VAPI_AGENT_ID1} type="bad" />
        <StartCallContent agentId={VAPI_AGENT_ID2} type="good" />
      </div>
    </div>
  );
}
