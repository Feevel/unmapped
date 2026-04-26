import {
  SeekerProfile,
  SkillPassport,
  MappedSkill,
  OpportunityRecommendation,
  AIReadinessInsight,
  JobListing,
  LaborMarketSignal,
  ReadinessBreakdown,
} from "./seeker-chat-types";
import { dedupeSignals, getDemoContext } from "./demo-contexts";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Types mirroring backend response shapes
// ---------------------------------------------------------------------------

type BackendWorker = {
  id: number;
  name: string | null;
  location: string;
  country_code?: string | null;
  raw_experience: string;
};

type BackendSkill = {
  id?: string | null;
  name: string;
  confidence?: number | null;
  source?: string | null;
  source_query?: string | null;
  evidence?: string[];
  proficiency_basis?: string | null;
};

type BackendMatch = {
  job_id: number;
  title: string;
  location: string;
  score: number;
  skill_score: number;
  location_score: number;
  matched_skills: string[];
  missing_skills: Array<{
    skill: string;
    importance: string;
    gap_size: string;
    next_step: string;
  }>;
  labor_signals: Array<{
    label: string;
    value: string | number;
    unit?: string | null;
    source: string;
    source_url?: string | null;
    year?: number | null;
    explanation?: string | null;
  }>;
  automation_risk?: {
    score: number;
    level: "low" | "medium" | "high";
    source: string;
    calibration_note?: string | null;
  } | null;
  explanation: string;
};

// ---------------------------------------------------------------------------
// Source tag — callers can inspect which path was used
// ---------------------------------------------------------------------------

export type PassportSource = "backend" | "local_mock";

export type SkillPassportWithSource = SkillPassport & {
  _source: PassportSource;
  _backendError?: string;
};

// ---------------------------------------------------------------------------
// Public entry point
// ---------------------------------------------------------------------------

/**
 * Generate a skill passport.
 *
 * Always attempts the real backend first.  If it fails, returns a local mock
 * passport AND attaches `_source: "local_mock"` and `_backendError` so the
 * UI can surface a visible warning rather than silently serving stale data.
 */
export async function generateSkillPassport(
  profile: SeekerProfile
): Promise<SkillPassportWithSource> {
  try {
    const passport = await generateSkillPassportFromBackend(profile);
    return { ...passport, _source: "backend" };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Unknown error contacting backend";
    console.warn("Backend unavailable, falling back to local mock:", message);
    const passport = await generateMockSkillPassport(profile);
    return { ...passport, _source: "local_mock", _backendError: message };
  }
}

// ---------------------------------------------------------------------------
// HTTP helpers
// ---------------------------------------------------------------------------

async function postJson<TResponse>(
  path: string,
  body: unknown
): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `POST ${path} failed with HTTP ${response.status}${detail ? `: ${detail}` : ""}`
    );
  }

  return response.json();
}

async function getJson<TResponse>(path: string): Promise<TResponse> {
  const response = await fetch(`${API_BASE_URL}${path}`);

  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `GET ${path} failed with HTTP ${response.status}${detail ? `: ${detail}` : ""}`
    );
  }

  return response.json();
}

// ---------------------------------------------------------------------------
// Backend path
// ---------------------------------------------------------------------------

async function generateSkillPassportFromBackend(
  profile: SeekerProfile
): Promise<SkillPassport> {
  const context = getDemoContext(profile.contextId);
  const location =
    parseLocationFromDemographics(profile.demographics) || context.defaultLocation;

  const worker = await postJson<BackendWorker>("/workers/", {
    name: profile.fullName,
    location,
    country_code: context.countryCode,
    raw_experience: [
      `Configured context: ${context.label}`,
      profile.workDescription,
      `Frequency: ${profile.activityFrequency}`,
      `Demographics: ${profile.demographics}`,
    ].join("\n"),
  });

  const skillsResponse = await getJson<{
    worker_id: number;
    skills: BackendSkill[];
  }>(`/workers/${worker.id}/skills`);

  const matchesResponse = await getJson<{
    worker_id: number;
    engine: string;
    matches: BackendMatch[];
  }>(`/matches/worker/${worker.id}`);

  const mappedSkills = skillsResponse.skills.map((skill): MappedSkill => ({
    name: skill.name,
    escoCode: skill.id || "fallback-keyword",
    iscoCategory: "ESCO skill",
    proficiencyLevel: confidenceToProficiency(skill.confidence),
    source: skill.source_query
      ? `${skill.source || "backend"}: ${skill.source_query}`
      : skill.source || "backend extraction",
    evidence: skill.evidence || [],
    confidence: skill.confidence ?? undefined,
  }));

  const credibleMatches = matchesResponse.matches.filter(
    (m) => m.score >= 25 || m.matched_skills.length > 0
  );
  const displayMatches =
    credibleMatches.length > 0
      ? credibleMatches
      : matchesResponse.matches.slice(0, 1);

  const opportunities = displayMatches.slice(0, 3).map(
    (m): OpportunityRecommendation => ({
      title: m.title,
      organization: "UNMAPPED opportunity graph",
      matchScore: Math.round(m.score),
      type: "Employment",
      location: m.location,
    })
  );

  const jobListings = displayMatches.map((m): JobListing => ({
    id: `JOB-${m.job_id}`,
    title: m.title,
    company: "Local opportunity provider",
    location: m.location,
    type: "Full-time",
    salary: laborSignalSummary(m.labor_signals),
    description: jobListingDescription(m),
    postedDate: "Backend match",
    isRemote: m.location.toLowerCase() === "remote",
    matchScore: Math.round(m.score),
    matchedSkills: m.matched_skills,
    laborSignals: normalizeBackendSignals(m.labor_signals),
  }));

  const laborMarketSignals = dedupeSignals(
    matchesResponse.matches.flatMap((m) => normalizeBackendSignals(m.labor_signals))
  );

  const readinessBreakdown = buildReadinessBreakdown(
    displayMatches,
    mappedSkills,
    laborMarketSignals.length > 0 ? laborMarketSignals : context.fallbackSignals
  );
  const overallReadinessScore = readinessBreakdownScore(readinessBreakdown);
  const aiInsights = buildBackendInsights(displayMatches, mappedSkills, readinessBreakdown);

  return {
    id: `SP-${worker.id}`,
    generatedAt: new Date(),
    profile,
    context,
    laborMarketSignals:
      laborMarketSignals.length > 0 ? laborMarketSignals : context.fallbackSignals,
    mappedSkills,
    opportunities,
    jobListings,
    aiInsights,
    overallReadinessScore,
    readinessBreakdown,
  };
}

// ---------------------------------------------------------------------------
// Normalisation helpers
// ---------------------------------------------------------------------------

function normalizeBackendSignals(
  signals: BackendMatch["labor_signals"]
): LaborMarketSignal[] {
  return signals.map((s, i) => ({
    id: `${s.label}-${s.year ?? i}`,
    label: s.label,
    value: s.value,
    unit: s.unit ?? undefined,
    year: s.year ?? undefined,
    source: s.source,
    sourceUrl: s.source_url ?? undefined,
    explanation: s.explanation ?? "Local labor market signal.",
    trend: numericSignalValue(s.value) == null ? "flat" : ("up" as const),
  }));
}

function confidenceToProficiency(
  confidence?: number | null
): MappedSkill["proficiencyLevel"] {
  if (confidence == null) return "Intermediate";
  if (confidence >= 0.85) return "Advanced";
  if (confidence >= 0.65) return "Intermediate";
  return "Basic";
}

function laborSignalSummary(signals: BackendMatch["labor_signals"]): string {
  if (!signals.length) return "Labor signals unavailable";
  return signals
    .slice(0, 2)
    .map((s) => `${s.label}: ${s.value}${s.unit ? ` ${s.unit}` : ""}`)
    .join(" | ");
}

function jobListingDescription(match: BackendMatch): string {
  const matched =
    match.matched_skills.length > 0
      ? `Matched skills: ${match.matched_skills.slice(0, 3).join(", ")}.`
      : "No direct skill overlap yet.";
  const gap = match.missing_skills[0]
    ? `Next step: ${match.missing_skills[0].next_step}`
    : "No major skill gap returned for this opportunity.";
  const locationNote =
    match.location_score >= 100
      ? "Location fit: same configured area."
      : match.location_score > 0
      ? "Location fit: possible with remote work or relocation flexibility."
      : "Location fit: may be a barrier.";

  return `${matched} ${gap} ${locationNote}`;
}

// ---------------------------------------------------------------------------
// Readiness breakdown
// ---------------------------------------------------------------------------

function buildBackendInsights(
  matches: BackendMatch[],
  mappedSkills: MappedSkill[],
  readinessBreakdown: ReadinessBreakdown
): AIReadinessInsight[] {
  const bestMatch = matches[0];
  const risk = bestMatch?.automation_risk;
  const laborSignals = bestMatch?.labor_signals ?? [];
  const missingSkill = bestMatch?.missing_skills?.[0];
  const strongestSkills = mappedSkills
    .slice()
    .sort((a, b) => (b.confidence ?? 0) - (a.confidence ?? 0))
    .slice(0, 3)
    .map((s) => s.name);

  return [
    {
      category: "Why This Score",
      riskLevel: scoreToStatus(readinessBreakdownScore(readinessBreakdown)),
      description: readinessBreakdown.summary,
      recommendation:
        readinessBreakdown.actions[0]?.nextStep ??
        "Add more task examples to make the passport stronger.",
    },
    {
      category: "Automation Durability",
      riskLevel: riskLevelFromBackend(risk?.level),
      description: risk
        ? `For the closest matched opportunity, automation exposure is ${risk.level}. ${risk.calibration_note ?? ""}`
        : "Automation exposure data is not available for this match yet.",
      recommendation:
        "Document durable evidence: customer trust, local coordination, troubleshooting, creative judgment, or hands-on work.",
    },
    {
      category: "Local Labor Context",
      riskLevel: scoreToStatus(
        readinessBreakdown.components.find((c) => c.label === "Local labor context")
          ?.score ?? 0
      ),
      description: laborSignals.length
        ? laborSignals
            .slice(0, 2)
            .map((s) => `${s.label}: ${s.value}${s.unit ? ` ${s.unit}` : ""}`)
            .join(" | ")
        : "No labor market signals were returned for this profile.",
      recommendation:
        laborSignals[0]?.explanation ??
        "Compare opportunities using both fit score and local market signals.",
    },
    {
      category: "Best Next Skills",
      riskLevel: missingSkill ? "Medium" : "Low",
      description: missingSkill
        ? `The closest opportunity would score higher with stronger evidence for ${missingSkill.skill}.`
        : `Strongest profile signals: ${strongestSkills.join(", ") || "not available yet"}.`,
      recommendation:
        missingSkill?.next_step ?? "Use the matched skills as portable evidence.",
    },
  ];
}

function buildReadinessBreakdown(
  matches: BackendMatch[],
  mappedSkills: MappedSkill[],
  laborMarketSignals: LaborMarketSignal[]
): ReadinessBreakdown {
  const bestMatch = matches[0];
  const opportunityFit = Math.round(bestMatch?.score ?? 0);
  const skillEvidence = Math.round(averageSkillConfidence(mappedSkills) * 100);
  const localContext = Math.round(
    localContextScore(laborMarketSignals, bestMatch)
  );
  const automationResilience = Math.round(
    bestMatch?.automation_risk ? (1 - bestMatch.automation_risk.score) * 100 : 55
  );

  const components = [
    {
      label: "Opportunity fit",
      score: opportunityFit,
      weight: 40,
      explanation: bestMatch
        ? `Best reachable match is ${bestMatch.title} at ${Math.round(bestMatch.score)}%, based on skill overlap and location fit.`
        : "No matching opportunities were available in this configured country.",
    },
    {
      label: "Skill evidence",
      score: skillEvidence,
      weight: 30,
      explanation: mappedSkills.length
        ? `The profile has ${mappedSkills.length} mapped skill(s); confidence is based on concrete evidence from the answers.`
        : "The profile needs more concrete task evidence before the system can trust the skill signal.",
    },
    {
      label: "Local labor context",
      score: localContext,
      weight: 20,
      explanation: localContextExplanation(laborMarketSignals),
    },
    {
      label: "Automation resilience",
      score: automationResilience,
      weight: 10,
      explanation: bestMatch?.automation_risk
        ? `Closest opportunity has ${bestMatch.automation_risk.level} automation exposure; durable human skills keep this component from falling to zero.`
        : "Automation data is not available, so this component uses a cautious default.",
    },
  ];

  const score = readinessBreakdownScore({ summary: "", components, actions: [] });
  const actions = readinessActions(matches, mappedSkills);
  const bestTitle = bestMatch?.title ?? "the current local opportunity set";

  return {
    summary: `Your readiness is ${score}% because your strongest current path is ${bestTitle}. The score combines match quality, evidence strength, local labor signals, and automation resilience.`,
    components,
    actions,
  };
}

function readinessBreakdownScore(breakdown: ReadinessBreakdown): number {
  const weighted = breakdown.components.reduce(
    (sum, c) => sum + c.score * (c.weight / 100),
    0
  );
  return Math.round(Math.max(0, Math.min(100, weighted)));
}

function averageSkillConfidence(skills: MappedSkill[]): number {
  if (!skills.length) return 0.15;
  const total = skills.reduce((sum, s) => sum + (s.confidence ?? 0.55), 0);
  return Math.max(0.15, Math.min(0.95, total / skills.length));
}

function localContextScore(
  signals: LaborMarketSignal[],
  bestMatch?: BackendMatch
): number {
  const title = `${bestMatch?.title ?? ""}`.toLowerCase();
  const preferredLabel = title.includes("agric")
    ? "agriculture"
    : title.includes("software") || title.includes("ict") || title.includes("support")
    ? "services"
    : "";
  const preferred = signals.find((s) =>
    s.label.toLowerCase().includes(preferredLabel)
  );
  const internet = signals.find((s) => s.label.toLowerCase().includes("internet"));
  const wage = signals.find((s) => s.label.toLowerCase().includes("wage"));

  const preferredValue = numericSignalValue(preferred?.value ?? "") ?? 35;
  const internetValue = numericSignalValue(internet?.value ?? "") ?? 40;
  const wageValue = numericSignalValue(wage?.value ?? "") ?? 25;

  return Math.max(
    20,
    Math.min(90, preferredValue * 0.5 + internetValue * 0.25 + wageValue * 0.25)
  );
}

function localContextExplanation(signals: LaborMarketSignal[]): string {
  const text = signals
    .slice(0, 2)
    .map((s) => `${s.label} is ${s.value}${s.unit ? ` ${s.unit}` : ""}`)
    .join("; ");
  return text
    ? `${text}. These signals adjust the score toward opportunities that are realistic in the selected country.`
    : "No local labor signals were available, so the score uses a cautious default.";
}

function readinessActions(
  matches: BackendMatch[],
  mappedSkills: MappedSkill[]
): ReadinessBreakdown["actions"] {
  const gaps = matches.flatMap((m) => m.missing_skills);
  const uniqueGaps = gaps.filter(
    (gap, i, list) => list.findIndex((g) => g.skill === gap.skill) === i
  );
  const actions = uniqueGaps.slice(0, 3).map((gap) => ({
    skill: gap.skill,
    impact:
      gap.importance === "required"
        ? "High impact: required by at least one close opportunity."
        : "Medium impact: would improve a close opportunity match.",
    nextStep: gap.next_step,
  }));

  if (mappedSkills.length < 3) {
    actions.push({
      skill: "More skill evidence",
      impact: "High impact: makes the passport and score more reliable.",
      nextStep:
        "Add examples with tools used, customers served, products built, frequency, and years of experience.",
    });
  }

  return actions.slice(0, 3);
}

function scoreToStatus(score: number): AIReadinessInsight["riskLevel"] {
  if (score >= 70) return "Low";
  if (score >= 45) return "Medium";
  return "High";
}

function riskLevelFromBackend(
  level?: "low" | "medium" | "high"
): AIReadinessInsight["riskLevel"] {
  if (level === "low") return "Low";
  if (level === "high") return "High";
  return "Medium";
}

// ---------------------------------------------------------------------------
// Local mock fallback (offline / no backend)
// ---------------------------------------------------------------------------

async function generateMockSkillPassport(
  profile: SeekerProfile
): Promise<SkillPassport> {
  await new Promise((resolve) => setTimeout(resolve, 2000));

  const mappedSkills = extractSkillsFromDescription(profile.workDescription);
  const context = getDemoContext(profile.contextId);
  const location =
    parseLocationFromDemographics(profile.demographics) || context.defaultLocation;

  const opportunities = generateOpportunities(mappedSkills, location);
  const jobListings = generateJobListings(mappedSkills, location);
  const aiInsights = generateAIInsights(mappedSkills);
  const readinessBreakdown = buildMockReadinessBreakdown(
    mappedSkills,
    jobListings,
    context.fallbackSignals
  );
  const overallReadinessScore = readinessBreakdownScore(readinessBreakdown);

  return {
    id: `SP-MOCK-${Date.now()}`,
    generatedAt: new Date(),
    profile,
    context,
    laborMarketSignals: context.fallbackSignals,
    mappedSkills,
    opportunities,
    jobListings,
    aiInsights,
    overallReadinessScore,
    readinessBreakdown,
  };
}

function buildMockReadinessBreakdown(
  skills: MappedSkill[],
  jobs: JobListing[],
  signals: LaborMarketSignal[]
): ReadinessBreakdown {
  const bestJob = jobs[0];
  const components = [
    {
      label: "Opportunity fit",
      score: bestJob?.matchScore ?? 25,
      weight: 40,
      explanation: bestJob
        ? `Best offline-demo match is ${bestJob.title} at ${bestJob.matchScore}%.`
        : "No offline-demo jobs matched the profile.",
    },
    {
      label: "Skill evidence",
      score: Math.round(averageSkillConfidence(skills) * 100),
      weight: 30,
      explanation: `The offline fallback found ${skills.length} skill signal(s).`,
    },
    {
      label: "Local labor context",
      score: Math.round(localContextScore(signals)),
      weight: 20,
      explanation: localContextExplanation(signals),
    },
    {
      label: "Automation resilience",
      score: 55,
      weight: 10,
      explanation:
        "Offline fallback uses a cautious default because occupation-level automation data was not returned.",
    },
  ];

  return {
    summary:
      "This offline fallback score combines job fit, skill evidence, local labor signals, and a cautious automation default.",
    components,
    actions: [
      {
        skill: "More task evidence",
        impact: "High impact: improves skill confidence.",
        nextStep:
          "Add examples with tools used, customers served, products built, frequency, and years of experience.",
      },
    ],
  };
}

// ---------------------------------------------------------------------------
// Mock skill extraction (offline path only)
// ---------------------------------------------------------------------------

function parseLocationFromDemographics(demographics: string): string {
  const parts = demographics.split(",").map((p) => p.trim());
  return parts[parts.length - 1] || "";
}

function numericSignalValue(value: string | number): number | null {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  const parsed = Number.parseFloat(String(value));
  return Number.isFinite(parsed) ? parsed : null;
}

function extractSkillsFromDescription(description: string): MappedSkill[] {
  const lowerDesc = description.toLowerCase();
  const skills: MappedSkill[] = [];

  const skillMappings: Array<{
    keywords: string[];
    skill: Omit<MappedSkill, "source">;
  }> = [
    {
      keywords: ["farm", "agricult", "crop", "harvest", "plant"],
      skill: { name: "Crop Production", escoCode: "S1.1.1", iscoCategory: "6111 - Field Crop Growers", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["sell", "sales", "customer", "shop", "market", "trade"],
      skill: { name: "Sales and Marketing", escoCode: "S4.1.2", iscoCategory: "5221 - Shopkeepers", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["repair", "fix", "mechanic", "maintain", "tool"],
      skill: { name: "Equipment Repair and Maintenance", escoCode: "S2.3.1", iscoCategory: "7233 - Agricultural Mechanics", proficiencyLevel: "Advanced" },
    },
    {
      keywords: ["care", "child", "elder", "nurse", "health"],
      skill: { name: "Personal Care Services", escoCode: "S5.2.1", iscoCategory: "5311 - Child Care Workers", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["cook", "food", "kitchen", "bake", "prepare"],
      skill: { name: "Food Preparation", escoCode: "S5.1.3", iscoCategory: "5120 - Cooks", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["drive", "transport", "delivery", "vehicle"],
      skill: { name: "Vehicle Operation", escoCode: "S8.3.1", iscoCategory: "8322 - Drivers", proficiencyLevel: "Advanced" },
    },
    {
      keywords: ["teach", "train", "instruct", "mentor", "tutor"],
      skill: { name: "Teaching and Training", escoCode: "S2.4.1", iscoCategory: "2359 - Teaching Professionals", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["build", "construct", "carpent", "mason", "weld"],
      skill: { name: "Construction Work", escoCode: "S7.1.1", iscoCategory: "7111 - Building Construction", proficiencyLevel: "Intermediate" },
    },
    {
      keywords: ["sew", "tailor", "cloth", "fabric", "fashion"],
      skill: { name: "Textile and Garment Production", escoCode: "S7.5.1", iscoCategory: "7531 - Tailors", proficiencyLevel: "Advanced" },
    },
    {
      keywords: ["computer", "software", "program", "tech", "digital"],
      skill: { name: "Digital Skills", escoCode: "S2.1.1", iscoCategory: "2512 - Software Developers", proficiencyLevel: "Basic" },
    },
  ];

  skillMappings.forEach((mapping) => {
    if (mapping.keywords.some((kw) => lowerDesc.includes(kw))) {
      skills.push({ ...mapping.skill, source: "Work Description Analysis" });
    }
  });

  skills.push(
    { name: "Communication", escoCode: "S0.1.1", iscoCategory: "Transversal", proficiencyLevel: "Intermediate", source: "Default Assessment" },
    { name: "Problem Solving", escoCode: "S0.2.1", iscoCategory: "Transversal", proficiencyLevel: "Basic", source: "Default Assessment" }
  );

  return skills;
}

function generateOpportunities(
  skills: MappedSkill[],
  location: string
): OpportunityRecommendation[] {
  return skills.slice(0, 3).map((skill, i) => ({
    title: `${skill.name} Position`,
    organization: (["Local NGO", "Community Center", "Regional Enterprise"] as const)[i % 3],
    matchScore: 85 - i * 10,
    type: (["Employment", "Training", "Apprenticeship"] as const)[i % 3],
    location,
  }));
}

function generateJobListings(skills: MappedSkill[], location: string): JobListing[] {
  const allJobs: Omit<JobListing, "matchScore" | "matchedSkills">[] = [
    { id: "JOB-001", title: "Agricultural Field Supervisor", company: "Green Valley Farms", location, type: "Full-time", salary: "$35,000 - $45,000/year", description: "Oversee daily farming operations, manage crop production schedules, and coordinate with field workers.", postedDate: "2 days ago", isRemote: false },
    { id: "JOB-002", title: "Sales Representative", company: "Regional Trade Co.", location, type: "Full-time", salary: "$30,000 - $40,000/year + commission", description: "Drive sales growth in assigned territory, build customer relationships, and achieve monthly targets.", postedDate: "1 week ago", isRemote: false },
    { id: "JOB-003", title: "Equipment Maintenance Technician", company: "Industrial Solutions Ltd.", location, type: "Full-time", salary: "$40,000 - $55,000/year", description: "Perform preventive maintenance and repairs on industrial equipment.", postedDate: "3 days ago", isRemote: false },
    { id: "JOB-004", title: "Community Health Worker", company: "Local Health Initiative", location, type: "Part-time", salary: "$18 - $22/hour", description: "Provide basic health education, conduct home visits, and connect community members with healthcare resources.", postedDate: "5 days ago", isRemote: false },
    { id: "JOB-005", title: "Kitchen Assistant / Prep Cook", company: "Sunrise Restaurant Group", location, type: "Full-time", salary: "$28,000 - $35,000/year", description: "Assist in food preparation, maintain kitchen cleanliness, and support head chef.", postedDate: "1 day ago", isRemote: false },
    { id: "JOB-006", title: "Delivery Driver", company: "FastTrack Logistics", location, type: "Full-time", salary: "$32,000 - $42,000/year", description: "Deliver packages to residential and commercial locations.", postedDate: "4 days ago", isRemote: false },
    { id: "JOB-007", title: "Teaching Assistant", company: "Community Learning Center", location, type: "Part-time", salary: "$15 - $20/hour", description: "Support lead teachers and assist students with learning materials.", postedDate: "1 week ago", isRemote: false },
    { id: "JOB-008", title: "Construction Laborer", company: "BuildRight Construction", location, type: "Contract", salary: "$20 - $28/hour", description: "Assist in construction projects, operate hand and power tools.", postedDate: "2 days ago", isRemote: false },
    { id: "JOB-009", title: "Tailor / Seamstress", company: "Fashion Forward Boutique", location, type: "Full-time", salary: "$30,000 - $40,000/year", description: "Create custom garments, perform alterations, and work with clients.", postedDate: "6 days ago", isRemote: false },
    { id: "JOB-010", title: "Data Entry Specialist", company: "TechConnect Services", location: "Remote", type: "Freelance", salary: "$15 - $20/hour", description: "Enter and verify data in digital systems, maintain accurate records.", postedDate: "3 days ago", isRemote: true },
    { id: "JOB-011", title: "Childcare Provider", company: "Happy Kids Daycare", location, type: "Full-time", salary: "$25,000 - $32,000/year", description: "Care for children ages 0-5, plan educational activities.", postedDate: "1 week ago", isRemote: false },
    { id: "JOB-012", title: "Market Vendor Assistant", company: "Local Farmers Market Association", location, type: "Part-time", salary: "$14 - $18/hour", description: "Assist vendors with setting up stalls and handle customer transactions.", postedDate: "5 days ago", isRemote: false },
  ];

  const skillJobMappings: Record<string, string[]> = {
    "Crop Production": ["JOB-001", "JOB-012"],
    "Sales and Marketing": ["JOB-002", "JOB-012"],
    "Equipment Repair and Maintenance": ["JOB-003", "JOB-008"],
    "Personal Care Services": ["JOB-004", "JOB-011"],
    "Food Preparation": ["JOB-005"],
    "Vehicle Operation": ["JOB-006"],
    "Teaching and Training": ["JOB-007"],
    "Construction Work": ["JOB-008"],
    "Textile and Garment Production": ["JOB-009"],
    "Digital Skills": ["JOB-010"],
    "Communication": ["JOB-002", "JOB-004", "JOB-007", "JOB-012"],
    "Problem Solving": ["JOB-003", "JOB-008"],
  };

  return allJobs
    .map((job) => {
      const matchedSkills: string[] = [];
      let totalScore = 0;
      skills.forEach((skill) => {
        if ((skillJobMappings[skill.name] ?? []).includes(job.id)) {
          matchedSkills.push(skill.name);
          totalScore += skill.proficiencyLevel === "Expert" ? 25 : skill.proficiencyLevel === "Advanced" ? 20 : skill.proficiencyLevel === "Intermediate" ? 15 : 10;
        }
      });
      return { ...job, matchScore: Math.min(Math.round(totalScore + matchedSkills.length * 5), 100), matchedSkills };
    })
    .filter((j) => j.matchedSkills.length > 0)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 6);
}

function generateAIInsights(skills: MappedSkill[]): AIReadinessInsight[] {
  const hasDigitalSkills = skills.some((s) => s.name.toLowerCase().includes("digital"));
  const hasAdvancedSkills = skills.some((s) => s.proficiencyLevel === "Advanced");
  return [
    {
      category: "Automation Risk",
      riskLevel: hasAdvancedSkills ? "Low" : "Medium",
      description: hasAdvancedSkills
        ? "Your advanced skills provide good protection against automation."
        : "Some of your current tasks may be automatable in the future.",
      recommendation: "Consider developing specialised expertise in your strongest areas.",
    },
    {
      category: "Digital Readiness",
      riskLevel: hasDigitalSkills ? "Low" : "High",
      description: hasDigitalSkills
        ? "You have foundational digital skills for the modern economy."
        : "Digital skills are increasingly important across all sectors.",
      recommendation: hasDigitalSkills
        ? "Continue building on your digital foundation."
        : "Consider basic digital literacy training to expand opportunities.",
    },
    {
      category: "Market Demand",
      riskLevel: "Low",
      description: "Your skill set aligns with current market demands in your region.",
      recommendation: "Stay updated on industry trends and emerging opportunities.",
    },
  ];
}
