import {
  Institution,
  InstitutionJobListing,
  CandidateSkillPassport,
  CandidateMatch,
  DashboardMetrics,
} from "./institution-types";
import { MappedSkill } from "./seeker-chat-types";

// Mock institution data
export const mockInstitution: Institution = {
  id: "INST-001",
  name: "Global Impact Foundation",
  type: "NGO",
  industry: "Social Development",
  location: "Nairobi, Kenya",
  description: "Empowering communities through sustainable development programs",
  activeListings: 5,
  totalCandidates: 47,
};

// Mock job listings for the institution
export const mockJobListings: InstitutionJobListing[] = [
  {
    id: "LISTING-001",
    title: "Community Development Officer",
    department: "Field Operations",
    location: "Nairobi, Kenya",
    type: "Full-time",
    salary: "$25,000 - $35,000/year",
    description: "Lead community engagement initiatives and coordinate local development programs.",
    requiredSkills: ["Communication", "Teaching and Training", "Problem Solving", "Sales and Marketing"],
    postedDate: "1 week ago",
    status: "Active",
    applicants: 23,
    matchedCandidates: 8,
  },
  {
    id: "LISTING-002",
    title: "Agricultural Program Coordinator",
    department: "Sustainable Agriculture",
    location: "Rural Kenya",
    type: "Full-time",
    salary: "$30,000 - $40,000/year",
    description: "Oversee agricultural training programs and support local farming communities.",
    requiredSkills: ["Crop Production", "Teaching and Training", "Communication", "Problem Solving"],
    postedDate: "3 days ago",
    status: "Active",
    applicants: 15,
    matchedCandidates: 6,
  },
  {
    id: "LISTING-003",
    title: "Health Outreach Worker",
    department: "Community Health",
    location: "Nairobi, Kenya",
    type: "Part-time",
    salary: "$15 - $20/hour",
    description: "Conduct health education sessions and connect community members with healthcare services.",
    requiredSkills: ["Personal Care Services", "Communication", "Teaching and Training"],
    postedDate: "5 days ago",
    status: "Active",
    applicants: 31,
    matchedCandidates: 12,
  },
  {
    id: "LISTING-004",
    title: "Vocational Training Instructor",
    department: "Skills Development",
    location: "Mombasa, Kenya",
    type: "Contract",
    salary: "$28,000 - $38,000/year",
    description: "Deliver vocational training in technical skills including equipment maintenance and construction.",
    requiredSkills: ["Equipment Repair and Maintenance", "Construction Work", "Teaching and Training"],
    postedDate: "2 weeks ago",
    status: "Active",
    applicants: 18,
    matchedCandidates: 5,
  },
  {
    id: "LISTING-005",
    title: "Digital Literacy Facilitator",
    department: "Education",
    location: "Remote",
    type: "Part-time",
    salary: "$18 - $25/hour",
    description: "Teach basic digital skills and computer literacy to community members.",
    requiredSkills: ["Digital Skills", "Teaching and Training", "Communication"],
    postedDate: "4 days ago",
    status: "Active",
    applicants: 27,
    matchedCandidates: 9,
  },
];

// Mock candidate skill passports
export const mockCandidates: CandidateSkillPassport[] = [
  {
    id: "SP-001",
    seekerId: "SEEKER-001",
    fullName: "Amina Okonkwo",
    location: "Nairobi, Kenya",
    age: 28,
    generatedAt: new Date("2024-01-15"),
    workDescription: "Community volunteer, farming, teaching children",
    activityFrequency: "Daily",
    overallReadinessScore: 78,
    mappedSkills: [
      { name: "Teaching and Training", escoCode: "S5.1.1", iscoCategory: "2359", proficiencyLevel: "Advanced", source: "teaching children" },
      { name: "Crop Production", escoCode: "S1.1.1", iscoCategory: "6111", proficiencyLevel: "Intermediate", source: "farming" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "community volunteer" },
      { name: "Personal Care Services", escoCode: "S3.1.1", iscoCategory: "5322", proficiencyLevel: "Intermediate", source: "caring work" },
    ],
  },
  {
    id: "SP-002",
    seekerId: "SEEKER-002",
    fullName: "Joseph Mwangi",
    location: "Mombasa, Kenya",
    age: 35,
    generatedAt: new Date("2024-01-14"),
    workDescription: "Mechanic, equipment repair, motorcycle taxi driver",
    activityFrequency: "Daily",
    overallReadinessScore: 82,
    mappedSkills: [
      { name: "Equipment Repair and Maintenance", escoCode: "S2.1.3", iscoCategory: "7231", proficiencyLevel: "Expert", source: "mechanic" },
      { name: "Vehicle Operation", escoCode: "S2.2.1", iscoCategory: "8322", proficiencyLevel: "Advanced", source: "motorcycle taxi driver" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Advanced", source: "equipment repair" },
      { name: "Sales and Marketing", escoCode: "S3.2.1", iscoCategory: "5221", proficiencyLevel: "Basic", source: "taxi services" },
    ],
  },
  {
    id: "SP-003",
    seekerId: "SEEKER-003",
    fullName: "Grace Wanjiku",
    location: "Nairobi, Kenya",
    age: 24,
    generatedAt: new Date("2024-01-16"),
    workDescription: "Market vendor, sewing and tailoring, childcare",
    activityFrequency: "Daily",
    overallReadinessScore: 71,
    mappedSkills: [
      { name: "Sales and Marketing", escoCode: "S3.2.1", iscoCategory: "5221", proficiencyLevel: "Advanced", source: "market vendor" },
      { name: "Textile and Garment Production", escoCode: "S2.3.1", iscoCategory: "7531", proficiencyLevel: "Intermediate", source: "sewing and tailoring" },
      { name: "Personal Care Services", escoCode: "S3.1.1", iscoCategory: "5311", proficiencyLevel: "Intermediate", source: "childcare" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "market vendor" },
    ],
  },
  {
    id: "SP-004",
    seekerId: "SEEKER-004",
    fullName: "Daniel Ochieng",
    location: "Kisumu, Kenya",
    age: 31,
    generatedAt: new Date("2024-01-13"),
    workDescription: "Construction worker, farming, community leader",
    activityFrequency: "Weekly",
    overallReadinessScore: 75,
    mappedSkills: [
      { name: "Construction Work", escoCode: "S2.4.1", iscoCategory: "7111", proficiencyLevel: "Advanced", source: "construction worker" },
      { name: "Crop Production", escoCode: "S1.1.1", iscoCategory: "6111", proficiencyLevel: "Intermediate", source: "farming" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "community leader" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Intermediate", source: "construction" },
    ],
  },
  {
    id: "SP-005",
    seekerId: "SEEKER-005",
    fullName: "Faith Njeri",
    location: "Nairobi, Kenya",
    age: 22,
    generatedAt: new Date("2024-01-17"),
    workDescription: "Student, tutoring, social media management, data entry",
    activityFrequency: "Daily",
    overallReadinessScore: 85,
    mappedSkills: [
      { name: "Digital Skills", escoCode: "S4.3.1", iscoCategory: "2511", proficiencyLevel: "Advanced", source: "social media management, data entry" },
      { name: "Teaching and Training", escoCode: "S5.1.1", iscoCategory: "2359", proficiencyLevel: "Intermediate", source: "tutoring" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "social media" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Intermediate", source: "data management" },
    ],
  },
  {
    id: "SP-006",
    seekerId: "SEEKER-006",
    fullName: "Peter Kamau",
    location: "Rural Kenya",
    age: 42,
    generatedAt: new Date("2024-01-12"),
    workDescription: "Farmer, livestock keeping, local trader, community elder",
    activityFrequency: "Daily",
    overallReadinessScore: 72,
    mappedSkills: [
      { name: "Crop Production", escoCode: "S1.1.1", iscoCategory: "6111", proficiencyLevel: "Expert", source: "farmer" },
      { name: "Sales and Marketing", escoCode: "S3.2.1", iscoCategory: "5221", proficiencyLevel: "Advanced", source: "local trader" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "community elder" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Intermediate", source: "farming" },
    ],
  },
  {
    id: "SP-007",
    seekerId: "SEEKER-007",
    fullName: "Mary Akinyi",
    location: "Nairobi, Kenya",
    age: 29,
    generatedAt: new Date("2024-01-16"),
    workDescription: "Nurse assistant, community health volunteer, first aid trainer",
    activityFrequency: "Daily",
    overallReadinessScore: 88,
    mappedSkills: [
      { name: "Personal Care Services", escoCode: "S3.1.1", iscoCategory: "5322", proficiencyLevel: "Expert", source: "nurse assistant" },
      { name: "Teaching and Training", escoCode: "S5.1.1", iscoCategory: "2359", proficiencyLevel: "Advanced", source: "first aid trainer" },
      { name: "Communication", escoCode: "S4.1.1", iscoCategory: "2166", proficiencyLevel: "Advanced", source: "health volunteer" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Advanced", source: "emergency care" },
    ],
  },
  {
    id: "SP-008",
    seekerId: "SEEKER-008",
    fullName: "Samuel Otieno",
    location: "Mombasa, Kenya",
    age: 26,
    generatedAt: new Date("2024-01-15"),
    workDescription: "Electrician apprentice, solar panel installer, phone repair",
    activityFrequency: "Daily",
    overallReadinessScore: 79,
    mappedSkills: [
      { name: "Equipment Repair and Maintenance", escoCode: "S2.1.3", iscoCategory: "7411", proficiencyLevel: "Advanced", source: "electrician, phone repair" },
      { name: "Problem Solving", escoCode: "S4.2.1", iscoCategory: "2149", proficiencyLevel: "Advanced", source: "electrical troubleshooting" },
      { name: "Digital Skills", escoCode: "S4.3.1", iscoCategory: "2511", proficiencyLevel: "Intermediate", source: "phone repair" },
      { name: "Teaching and Training", escoCode: "S5.1.1", iscoCategory: "2359", proficiencyLevel: "Basic", source: "apprenticeship" },
    ],
  },
];

// Calculate compatibility between a candidate and a job listing
function calculateCompatibility(
  candidate: CandidateSkillPassport,
  listing: InstitutionJobListing
): CandidateMatch {
  const candidateSkillNames = candidate.mappedSkills.map((s) => s.name);
  const matchedSkills = listing.requiredSkills.filter((skill) =>
    candidateSkillNames.includes(skill)
  );
  const missingSkills = listing.requiredSkills.filter(
    (skill) => !candidateSkillNames.includes(skill)
  );

  // Calculate base compatibility score
  const skillMatchRatio = matchedSkills.length / listing.requiredSkills.length;
  
  // Factor in proficiency levels for matched skills
  let proficiencyBonus = 0;
  matchedSkills.forEach((skillName) => {
    const skill = candidate.mappedSkills.find((s) => s.name === skillName);
    if (skill) {
      proficiencyBonus +=
        skill.proficiencyLevel === "Expert"
          ? 10
          : skill.proficiencyLevel === "Advanced"
          ? 7
          : skill.proficiencyLevel === "Intermediate"
          ? 4
          : 1;
    }
  });

  // Calculate final compatibility score (0-100)
  const compatibilityScore = Math.min(
    Math.round(skillMatchRatio * 70 + proficiencyBonus + candidate.overallReadinessScore * 0.1),
    100
  );

  // Determine recommendation
  let recommendation: CandidateMatch["recommendation"];
  if (compatibilityScore >= 75) {
    recommendation = "Strong Fit";
  } else if (compatibilityScore >= 55) {
    recommendation = "Good Fit";
  } else if (compatibilityScore >= 35) {
    recommendation = "Potential Fit";
  } else {
    recommendation = "Development Needed";
  }

  return {
    candidate,
    listingId: listing.id,
    listingTitle: listing.title,
    compatibilityScore,
    matchedSkills,
    missingSkills,
    recommendation,
  };
}

// Get all candidate matches for all listings
export async function getCandidateMatches(
  listingId?: string
): Promise<CandidateMatch[]> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 500));

  const listings = listingId
    ? mockJobListings.filter((l) => l.id === listingId)
    : mockJobListings;

  const allMatches: CandidateMatch[] = [];

  listings.forEach((listing) => {
    mockCandidates.forEach((candidate) => {
      const match = calculateCompatibility(candidate, listing);
      // Only include candidates with at least one matched skill
      if (match.matchedSkills.length > 0) {
        allMatches.push(match);
      }
    });
  });

  // Sort by compatibility score descending
  return allMatches.sort((a, b) => b.compatibilityScore - a.compatibilityScore);
}

// Get best matches for each candidate (their highest scoring listing)
export async function getBestCandidateMatches(): Promise<CandidateMatch[]> {
  const allMatches = await getCandidateMatches();
  
  // Group by candidate and keep best match for each
  const bestMatches = new Map<string, CandidateMatch>();
  
  allMatches.forEach((match) => {
    const existing = bestMatches.get(match.candidate.id);
    if (!existing || match.compatibilityScore > existing.compatibilityScore) {
      bestMatches.set(match.candidate.id, match);
    }
  });

  return Array.from(bestMatches.values()).sort(
    (a, b) => b.compatibilityScore - a.compatibilityScore
  );
}

// Get dashboard metrics
export async function getDashboardMetrics(): Promise<DashboardMetrics> {
  const matches = await getBestCandidateMatches();

  const totalCandidates = mockCandidates.length;
  const averageCompatibility =
    matches.length > 0
      ? Math.round(
          matches.reduce((sum, m) => sum + m.compatibilityScore, 0) / matches.length
        )
      : 0;

  const strongFitCount = matches.filter((m) => m.recommendation === "Strong Fit").length;
  const goodFitCount = matches.filter((m) => m.recommendation === "Good Fit").length;
  const potentialFitCount = matches.filter((m) => m.recommendation === "Potential Fit").length;

  // Calculate skill demand across all listings
  const skillDemand = new Map<string, number>();
  mockJobListings.forEach((listing) => {
    listing.requiredSkills.forEach((skill) => {
      skillDemand.set(skill, (skillDemand.get(skill) || 0) + 1);
    });
  });

  const topSkillsInDemand = Array.from(skillDemand.entries())
    .map(([skill, count]) => ({ skill, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  // Calculate candidates by location
  const locationCounts = new Map<string, number>();
  mockCandidates.forEach((candidate) => {
    locationCounts.set(
      candidate.location,
      (locationCounts.get(candidate.location) || 0) + 1
    );
  });

  const candidatesByLocation = Array.from(locationCounts.entries())
    .map(([location, count]) => ({ location, count }))
    .sort((a, b) => b.count - a.count);

  return {
    totalCandidates,
    averageCompatibility,
    strongFitCount,
    goodFitCount,
    potentialFitCount,
    topSkillsInDemand,
    candidatesByLocation,
  };
}

// Get institution data
export async function getInstitution(): Promise<Institution> {
  await new Promise((resolve) => setTimeout(resolve, 200));
  return mockInstitution;
}

// Get job listings
export async function getJobListings(): Promise<InstitutionJobListing[]> {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return mockJobListings;
}
