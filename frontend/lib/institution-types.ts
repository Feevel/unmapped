import { MappedSkill } from "./seeker-chat-types";

export interface Institution {
  id: string;
  name: string;
  type: "NGO" | "Company" | "Government";
  industry: string;
  location: string;
  description: string;
  activeListings: number;
  totalCandidates: number;
}

export interface InstitutionJobListing {
  id: string;
  title: string;
  department: string;
  location: string;
  type: "Full-time" | "Part-time" | "Contract" | "Freelance" | "Internship";
  salary?: string;
  description: string;
  requiredSkills: string[];
  postedDate: string;
  status: "Active" | "Paused" | "Closed";
  applicants: number;
  matchedCandidates: number;
}

export interface CandidateSkillPassport {
  id: string;
  seekerId: string;
  fullName: string;
  location: string;
  age: number;
  generatedAt: Date;
  mappedSkills: MappedSkill[];
  overallReadinessScore: number;
  workDescription: string;
  activityFrequency: string;
}

export interface CandidateMatch {
  candidate: CandidateSkillPassport;
  listingId: string;
  listingTitle: string;
  compatibilityScore: number;
  matchedSkills: string[];
  missingSkills: string[];
  recommendation: "Strong Fit" | "Good Fit" | "Potential Fit" | "Development Needed";
}

export interface DashboardMetrics {
  totalCandidates: number;
  averageCompatibility: number;
  strongFitCount: number;
  goodFitCount: number;
  potentialFitCount: number;
  topSkillsInDemand: { skill: string; count: number }[];
  candidatesByLocation: { location: string; count: number }[];
}
