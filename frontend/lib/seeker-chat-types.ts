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
  contextId?: DemoContextId;
}

export type DemoContextId =
  | "ghana_urban_informal"
  | "india_rural_agriculture"
  | "kenya_mixed_services_agriculture"
  | "bangladesh_rural_transition"
  | "nigeria_urban_services";

export interface LaborMarketSignal {
  id: string;
  label: string;
  value: string | number;
  unit?: string;
  year?: number;
  source: string;
  sourceUrl?: string;
  explanation: string;
  trend?: "up" | "flat" | "down";
}

export interface DemoContextConfig {
  id: DemoContextId;
  label: string;
  countryCode: string;
  region: string;
  focus: string;
  language: string;
  educationTaxonomy: string;
  automationCalibration: string;
  opportunityTypes: string[];
  laborDataSource: string;
  defaultLocation: string;
  notes: string;
  fallbackSignals: LaborMarketSignal[];
}

export interface MappedSkill {
  name: string;
  escoCode: string;
  iscoCategory: string;
  proficiencyLevel: "Basic" | "Intermediate" | "Advanced" | "Expert";
  source: string;
  evidence?: string[];
  confidence?: number;
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

export interface ReadinessComponent {
  label: string;
  score: number;
  weight: number;
  explanation: string;
}

export interface ReadinessAction {
  skill: string;
  impact: string;
  nextStep: string;
}

export interface ReadinessBreakdown {
  summary: string;
  components: ReadinessComponent[];
  actions: ReadinessAction[];
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
  laborSignals?: LaborMarketSignal[];
}

export interface SkillPassport {
  id: string;
  generatedAt: Date;
  profile: SeekerProfile;
  context: DemoContextConfig;
  laborMarketSignals: LaborMarketSignal[];
  mappedSkills: MappedSkill[];
  opportunities: OpportunityRecommendation[];
  jobListings: JobListing[];
  aiInsights: AIReadinessInsight[];
  overallReadinessScore: number;
  readinessBreakdown: ReadinessBreakdown;
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
