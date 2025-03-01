export interface Segment {
  start: number;
  end: number;
  title: string;
  reference: string;
  impact: string;
}

export interface Call {
  id: string;
  personName: string;
  title: string;
  email: string;
  date: Date;
  recordingUrl: string;
  duration?: string;
  company: {
    name: string;
    size: string;
    industry: string;
  };
  avatar_url: string;
  notes: string[];
  context?: {
    summary: string;
    nextSteps: string[];
    previousCalls?: string[]; // IDs of related calls
  };
  callType:
    | "Initial Outreach"
    | "Discovery"
    | "Qualification"
    | "Needs Analysis"
    | "Multithreaded Engagement"
    | "Product Demonstration"
    | "ROI Discussion"
    | "Objection Handling"
    | "Closing"
    | "Contract Negotiation"
    | "Follow-Up"
    | "Post-Sale Onboarding"
    | "Customer Success Handoff"
    | "Feedback"
    | "Referral or Expansion Opportunity"
    | "Proposal Presentation"
    | "Strategy or Planning"
    | "Training and Support"
    | "Renewal Discussion"
    | "Re-engagement";
}

export interface GroupedCalls {
  date: string;
  calls: Call[];
}
