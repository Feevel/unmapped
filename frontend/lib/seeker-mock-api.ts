import {
  SeekerProfile,
  SkillPassport,
  MappedSkill,
  OpportunityRecommendation,
  AIReadinessInsight,
  JobListing,
} from "./seeker-chat-types";

// Mock API function - replace with real backend endpoint later
export async function generateSkillPassport(
  profile: SeekerProfile
): Promise<SkillPassport> {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 2000));

  // Extract skills based on work description (mock extraction)
  const mappedSkills = extractSkillsFromDescription(profile.workDescription);

  // Parse location from demographics for opportunities
  const location = parseLocationFromDemographics(profile.demographics);

  // Generate opportunity recommendations
  const opportunities = generateOpportunities(mappedSkills, location);

  // Generate matching job listings
  const jobListings = generateJobListings(mappedSkills, location);

  // Generate AI readiness insights
  const aiInsights = generateAIInsights(mappedSkills);

  // Calculate overall readiness score
  const overallReadinessScore = calculateReadinessScore(mappedSkills, aiInsights);

  return {
    id: `SP-${Date.now()}`,
    generatedAt: new Date(),
    profile,
    mappedSkills,
    opportunities,
    jobListings,
    aiInsights,
    overallReadinessScore,
  };
}

function parseLocationFromDemographics(demographics: string): string {
  // Simple extraction - in production this would be more sophisticated
  const parts = demographics.split(",").map((p) => p.trim());
  return parts[parts.length - 1] || "Your Region";
}

function extractSkillsFromDescription(description: string): MappedSkill[] {
  const lowerDesc = description.toLowerCase();
  const skills: MappedSkill[] = [];

  // Mock skill extraction based on keywords
  const skillMappings: Array<{
    keywords: string[];
    skill: Omit<MappedSkill, "source">;
  }> = [
    {
      keywords: ["farm", "agricult", "crop", "harvest", "plant"],
      skill: {
        name: "Crop Production",
        escoCode: "S1.1.1",
        iscoCategory: "6111 - Field Crop Growers",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["sell", "sales", "customer", "shop", "market", "trade"],
      skill: {
        name: "Sales and Marketing",
        escoCode: "S4.1.2",
        iscoCategory: "5221 - Shopkeepers",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["repair", "fix", "mechanic", "maintain", "tool"],
      skill: {
        name: "Equipment Repair and Maintenance",
        escoCode: "S2.3.1",
        iscoCategory: "7233 - Agricultural Mechanics",
        proficiencyLevel: "Advanced",
      },
    },
    {
      keywords: ["care", "child", "elder", "nurse", "health"],
      skill: {
        name: "Personal Care Services",
        escoCode: "S5.2.1",
        iscoCategory: "5311 - Child Care Workers",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["cook", "food", "kitchen", "bake", "prepare"],
      skill: {
        name: "Food Preparation",
        escoCode: "S5.1.3",
        iscoCategory: "5120 - Cooks",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["drive", "transport", "delivery", "vehicle"],
      skill: {
        name: "Vehicle Operation",
        escoCode: "S8.3.1",
        iscoCategory: "8322 - Drivers",
        proficiencyLevel: "Advanced",
      },
    },
    {
      keywords: ["teach", "train", "instruct", "mentor", "tutor"],
      skill: {
        name: "Teaching and Training",
        escoCode: "S2.4.1",
        iscoCategory: "2359 - Teaching Professionals",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["build", "construct", "carpent", "mason", "weld"],
      skill: {
        name: "Construction Work",
        escoCode: "S7.1.1",
        iscoCategory: "7111 - Building Construction",
        proficiencyLevel: "Intermediate",
      },
    },
    {
      keywords: ["sew", "tailor", "cloth", "fabric", "fashion"],
      skill: {
        name: "Textile and Garment Production",
        escoCode: "S7.5.1",
        iscoCategory: "7531 - Tailors",
        proficiencyLevel: "Advanced",
      },
    },
    {
      keywords: ["computer", "software", "program", "tech", "digital"],
      skill: {
        name: "Digital Skills",
        escoCode: "S2.1.1",
        iscoCategory: "2512 - Software Developers",
        proficiencyLevel: "Basic",
      },
    },
  ];

  skillMappings.forEach((mapping) => {
    if (mapping.keywords.some((keyword) => lowerDesc.includes(keyword))) {
      skills.push({
        ...mapping.skill,
        source: "Work Description Analysis",
      });
    }
  });

  // Add default transferable skills
  skills.push(
    {
      name: "Communication",
      escoCode: "S0.1.1",
      iscoCategory: "Transversal",
      proficiencyLevel: "Intermediate",
      source: "Default Assessment",
    },
    {
      name: "Problem Solving",
      escoCode: "S0.2.1",
      iscoCategory: "Transversal",
      proficiencyLevel: "Basic",
      source: "Default Assessment",
    }
  );

  return skills;
}

function generateOpportunities(
  skills: MappedSkill[],
  location: string
): OpportunityRecommendation[] {
  const opportunities: OpportunityRecommendation[] = [];

  // Generate opportunities based on skills
  skills.slice(0, 3).forEach((skill, index) => {
    opportunities.push({
      title: `${skill.name} Position`,
      organization: ["Local NGO", "Community Center", "Regional Enterprise"][index % 3],
      matchScore: 85 - index * 10,
      type: ["Employment", "Training", "Apprenticeship"][index % 3] as OpportunityRecommendation["type"],
      location: location,
    });
  });

  // Add training opportunity
  opportunities.push({
    title: "Digital Skills Certificate Program",
    organization: "UNMAPPED Training Center",
    matchScore: 70,
    type: "Training",
    location: "Online",
  });

  return opportunities;
}

function generateJobListings(
  skills: MappedSkill[],
  location: string
): JobListing[] {
  // Mock job database - in production this would query a real job listings API
  const allJobs: Omit<JobListing, "matchScore" | "matchedSkills">[] = [
    {
      id: "JOB-001",
      title: "Agricultural Field Supervisor",
      company: "Green Valley Farms",
      location: location,
      type: "Full-time",
      salary: "$35,000 - $45,000/year",
      description: "Oversee daily farming operations, manage crop production schedules, and coordinate with field workers to ensure optimal harvest yields.",
      postedDate: "2 days ago",
      isRemote: false,
    },
    {
      id: "JOB-002",
      title: "Sales Representative",
      company: "Regional Trade Co.",
      location: location,
      type: "Full-time",
      salary: "$30,000 - $40,000/year + commission",
      description: "Drive sales growth in assigned territory, build customer relationships, and achieve monthly sales targets.",
      postedDate: "1 week ago",
      isRemote: false,
    },
    {
      id: "JOB-003",
      title: "Equipment Maintenance Technician",
      company: "Industrial Solutions Ltd.",
      location: location,
      type: "Full-time",
      salary: "$40,000 - $55,000/year",
      description: "Perform preventive maintenance and repairs on industrial equipment, diagnose mechanical issues, and ensure operational efficiency.",
      postedDate: "3 days ago",
      isRemote: false,
    },
    {
      id: "JOB-004",
      title: "Community Health Worker",
      company: "Local Health Initiative",
      location: location,
      type: "Part-time",
      salary: "$18 - $22/hour",
      description: "Provide basic health education, conduct home visits, and connect community members with healthcare resources.",
      postedDate: "5 days ago",
      isRemote: false,
    },
    {
      id: "JOB-005",
      title: "Kitchen Assistant / Prep Cook",
      company: "Sunrise Restaurant Group",
      location: location,
      type: "Full-time",
      salary: "$28,000 - $35,000/year",
      description: "Assist in food preparation, maintain kitchen cleanliness, and support head chef in daily operations.",
      postedDate: "1 day ago",
      isRemote: false,
    },
    {
      id: "JOB-006",
      title: "Delivery Driver",
      company: "FastTrack Logistics",
      location: location,
      type: "Full-time",
      salary: "$32,000 - $42,000/year",
      description: "Deliver packages to residential and commercial locations, maintain delivery schedules, and ensure safe transportation of goods.",
      postedDate: "4 days ago",
      isRemote: false,
    },
    {
      id: "JOB-007",
      title: "Teaching Assistant",
      company: "Community Learning Center",
      location: location,
      type: "Part-time",
      salary: "$15 - $20/hour",
      description: "Support lead teachers in classroom activities, assist students with learning materials, and help maintain a positive learning environment.",
      postedDate: "1 week ago",
      isRemote: false,
    },
    {
      id: "JOB-008",
      title: "Construction Laborer",
      company: "BuildRight Construction",
      location: location,
      type: "Contract",
      salary: "$20 - $28/hour",
      description: "Assist in construction projects, operate hand and power tools, and follow safety protocols on job sites.",
      postedDate: "2 days ago",
      isRemote: false,
    },
    {
      id: "JOB-009",
      title: "Tailor / Seamstress",
      company: "Fashion Forward Boutique",
      location: location,
      type: "Full-time",
      salary: "$30,000 - $40,000/year",
      description: "Create custom garments, perform alterations, and work with clients to design personalized clothing.",
      postedDate: "6 days ago",
      isRemote: false,
    },
    {
      id: "JOB-010",
      title: "Data Entry Specialist",
      company: "TechConnect Services",
      location: "Remote",
      type: "Freelance",
      salary: "$15 - $20/hour",
      description: "Enter and verify data in digital systems, maintain accurate records, and perform basic digital administrative tasks.",
      postedDate: "3 days ago",
      isRemote: true,
    },
    {
      id: "JOB-011",
      title: "Childcare Provider",
      company: "Happy Kids Daycare",
      location: location,
      type: "Full-time",
      salary: "$25,000 - $32,000/year",
      description: "Care for children ages 0-5, plan educational activities, and ensure a safe and nurturing environment.",
      postedDate: "1 week ago",
      isRemote: false,
    },
    {
      id: "JOB-012",
      title: "Market Vendor Assistant",
      company: "Local Farmers Market Association",
      location: location,
      type: "Part-time",
      salary: "$14 - $18/hour",
      description: "Assist vendors with setting up stalls, handle customer transactions, and promote products to market visitors.",
      postedDate: "5 days ago",
      isRemote: false,
    },
  ];

  // Skill to job matching keywords
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

  // Calculate match scores for each job
  const jobMatches = allJobs.map((job) => {
    const matchedSkills: string[] = [];
    let totalScore = 0;

    skills.forEach((skill) => {
      const matchingJobIds = skillJobMappings[skill.name] || [];
      if (matchingJobIds.includes(job.id)) {
        matchedSkills.push(skill.name);
        // Weight by proficiency level
        const proficiencyWeight =
          skill.proficiencyLevel === "Expert"
            ? 25
            : skill.proficiencyLevel === "Advanced"
            ? 20
            : skill.proficiencyLevel === "Intermediate"
            ? 15
            : 10;
        totalScore += proficiencyWeight;
      }
    });

    // Normalize score to percentage (max 100)
    const matchScore = Math.min(Math.round(totalScore + matchedSkills.length * 5), 100);

    return {
      ...job,
      matchScore,
      matchedSkills,
    };
  });

  // Filter jobs with at least one matching skill and sort by match score
  return jobMatches
    .filter((job) => job.matchedSkills.length > 0)
    .sort((a, b) => b.matchScore - a.matchScore)
    .slice(0, 6); // Return top 6 matches
}

function generateAIInsights(skills: MappedSkill[]): AIReadinessInsight[] {
  const hasDigitalSkills = skills.some((s) =>
    s.name.toLowerCase().includes("digital")
  );
  const hasAdvancedSkills = skills.some((s) => s.proficiencyLevel === "Advanced");

  return [
    {
      category: "Automation Risk",
      riskLevel: hasAdvancedSkills ? "Low" : "Medium",
      description: hasAdvancedSkills
        ? "Your advanced skills provide good protection against automation."
        : "Some of your current tasks may be automatable in the future.",
      recommendation: "Consider developing specialized expertise in your strongest areas.",
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

function calculateReadinessScore(
  skills: MappedSkill[],
  insights: AIReadinessInsight[]
): number {
  let score = 50; // Base score

  // Add points for skills
  score += Math.min(skills.length * 5, 25);

  // Add points for advanced skills
  score += skills.filter((s) => s.proficiencyLevel === "Advanced").length * 5;

  // Adjust based on risk levels
  insights.forEach((insight) => {
    if (insight.riskLevel === "Low") score += 5;
    if (insight.riskLevel === "High") score -= 5;
  });

  return Math.min(Math.max(score, 0), 100);
}
