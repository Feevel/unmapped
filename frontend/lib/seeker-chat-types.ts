export interface Message {
  id: string;
  role: "bot" | "user";
  content: string;
  timestamp: Date;
}

export interface SeekerProfile {
  fullName: string;
  workDescription: string;
  activityFrequency: string;
  demographics: string; // age, sex, location combined
}

export interface MappedSkill {
  name: string;
  escoCode: string;
  iscoCategory: string;
  proficiencyLevel: "Basic" | "Intermediate" | "Advanced" | "Expert";
  source: string;
}

export interface OpportunityRecommendation {
  title: string;
  organization: string;
  matchScore: number;
  type: "Employment" | "Training" | "Apprenticeship" | "Volunteer";
  location: string;
}

export interface AIReadinessInsight {
  category: string;
  riskLevel: "Low" | "Medium" | "High";
  description: string;
  recommendation: string;
}

export interface JobListing {
  id: string;
  title: string;
  company: string;
  location: string;
  type: "Full-time" | "Part-time" | "Contract" | "Freelance" | "Internship";
  salary?: string;
  matchScore: number;
  matchedSkills: string[];
  description: string;
  postedDate: string;
  isRemote: boolean;
}

export interface SkillPassport {
  id: string;
  generatedAt: Date;
  profile: SeekerProfile;
  mappedSkills: MappedSkill[];
  opportunities: OpportunityRecommendation[];
  jobListings: JobListing[];
  aiInsights: AIReadinessInsight[];
  overallReadinessScore: number;
}

export type ChatStep =
  | "name"
  | "work_description"
  | "frequency"
  | "demographics"
  | "complete";

export const CHAT_QUESTIONS: Record<ChatStep, string> = {
  name: "Welcome to UNMAPPED! I'm here to help you create your Skill Passport. Let's start by learning about you. What's your full name?",
  work_description:
    "Nice to meet you! Now, please describe your work experience, activities, and skills. This can include formal jobs, informal work, family business, repairs, selling, farming, volunteering, caring work, or any self-taught skills.",
  frequency:
    "How often do you perform these activities? (e.g., daily, weekly, occasionally?",
  demographics:
    "Great, thank you! Now lastly tell us your age, sex and where you are currently located.",
  complete:
    "Thank you for providing all this information! I now have everything I need to generate your Skill Passport.",
};
