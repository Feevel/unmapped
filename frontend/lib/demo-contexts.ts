import {
  DemoContextConfig,
  DemoContextId,
  LaborMarketSignal,
} from "./seeker-chat-types";

const SIGNALS_BY_COUNTRY: Record<string, LaborMarketSignal[]> = {
  GH: [
    signal("GH_internet_users_2024", "Individuals using the Internet", 72.18, "% of population", 2024, "World Bank WDI / ITU", "https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=GH", "Digital access affects whether ICT support, blended training, platform work, or remote support are realistic opportunities.", "up"),
    signal("GH_services_employment_2025", "Employment in services", 47.17, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.SRV.EMPL.ZS?locations=GH", "Services employment supports realistic pathways in repair, retail, customer-facing work, ICT support, and local service businesses.", "flat"),
    signal("GH_wage_salaried_workers_2025", "Wage and salaried workers", 32.54, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.EMP.WORK.ZS?locations=GH", "Formal wage work is only part of the market, so the matcher also keeps self-employment visible.", "up"),
    signal("GH_agriculture_employment_2025", "Employment in agriculture", 34.57, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.AGR.EMPL.ZS?locations=GH", "Agriculture remains a major employment sector for relevant rural or field skills.", "down"),
  ],
  IN: [
    signal("IN_internet_users_2025", "Individuals using the Internet", 70.0, "% of population", 2025, "World Bank WDI / ITU", "https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=IN", "Connectivity supports digital extension, phone-based training, and platform-enabled services, while rural access gaps still matter.", "up"),
    signal("IN_agriculture_employment_2025", "Employment in agriculture", 41.63, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.AGR.EMPL.ZS?locations=IN", "Agriculture is still a large employment sector, so rural matching should include farm services and adjacent training.", "down"),
    signal("IN_services_employment_2025", "Employment in services", 32.56, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.SRV.EMPL.ZS?locations=IN", "Services employment indicates reachable opportunities in local support, retail, logistics, and digital assistance.", "flat"),
    signal("IN_wage_salaried_workers_2025", "Wage and salaried workers", 25.1, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.EMP.WORK.ZS?locations=IN", "Formal wage work is a smaller share of employment, so the system should surface mixed livelihood pathways.", "up"),
  ],
  KE: [
    signal("KE_agriculture_employment_2025", "Employment in agriculture", 45.79, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.AGR.EMPL.ZS?locations=KE", "Agriculture is a major employment base, so agricultural and extension-linked opportunities are locally realistic.", "down"),
    signal("KE_services_employment_2025", "Employment in services", 41.73, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.SRV.EMPL.ZS?locations=KE", "A large service sector supports pathways in local services, repair, digital support, and small businesses.", "up"),
    signal("KE_wage_salaried_workers_2025", "Wage and salaried workers", 35.2, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.EMP.WORK.ZS?locations=KE", "The formal wage share is meaningful but limited, so matching should blend jobs, informal work, and enterprise pathways.", "flat"),
    signal("KE_internet_users_2024", "Individuals using the Internet", 34.98, "% of population", 2024, "World Bank WDI / ITU", "https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=KE", "Connectivity constraints should shape online training, remote support, and platform-work recommendations.", "up"),
  ],
  BD: [
    signal("BD_agriculture_employment_2025", "Employment in agriculture", 44.26, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.AGR.EMPL.ZS?locations=BD", "Agriculture remains a large employment base, so rural pathways should include crop work, records, and cooperative work.", "flat"),
    signal("BD_wage_salaried_workers_2025", "Wage and salaried workers", 38.96, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.EMP.WORK.ZS?locations=BD", "The wage-work share helps calibrate the balance between formal jobs, factory work, informal work, and training.", "flat"),
    signal("BD_services_employment_2025", "Employment in services", 37.71, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.SRV.EMPL.ZS?locations=BD", "Services employment supports matching into local services, retail, logistics, customer support, and digital assistance.", "flat"),
    signal("BD_internet_users_2024", "Individuals using the Internet", 53.42, "% of population", 2024, "World Bank WDI / ITU", "https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=BD", "Digital access supports blended training and digital-adjacent work, but recommendations should account for uneven connectivity.", "up"),
  ],
  NG: [
    signal("NG_services_employment_2025", "Employment in services", 49.46, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.SRV.EMPL.ZS?locations=NG", "A large service sector supports reachable pathways in local services, repair, retail, logistics, and small enterprise work.", "up"),
    signal("NG_agriculture_employment_2025", "Employment in agriculture", 33.53, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.AGR.EMPL.ZS?locations=NG", "Agriculture remains significant, so field work, agribusiness support, and adjacent training can be realistic.", "down"),
    signal("NG_internet_users_2024", "Individuals using the Internet", 41.21, "% of population", 2024, "World Bank WDI / ITU", "https://data.worldbank.org/indicator/IT.NET.USER.ZS?locations=NG", "Connectivity is sufficient for some digital pathways but still uneven enough for offline and low-bandwidth options.", "up"),
    signal("NG_wage_salaried_workers_2025", "Wage and salaried workers", 13.85, "% of total employment", 2025, "World Bank WDI / ILOSTAT", "https://data.worldbank.org/indicator/SL.EMP.WORK.ZS?locations=NG", "A low formal wage share means self-employment, apprenticeships, informal work, and training must be first-class pathways.", "up"),
  ],
};

export const DEMO_CONTEXTS: DemoContextConfig[] = [
  context("ghana_urban_informal", "Ghana - Urban informal services", "GH", "Accra / urban informal economy", "Phone repair, ICT support, customer-facing service work", "English", "Ghana education levels mapped to ISCED-style bands", "Lower full automation exposure where hands-on repair, cash trust, and local customer relationships matter.", ["formal employment", "self-employment", "apprenticeship", "short training"], "Accra"),
  context("india_rural_agriculture", "India - Rural agriculture", "IN", "Rural Maharashtra / agricultural economy", "Crop work, local coordination, record keeping, agri-services", "English / Hindi-ready", "Local credentials mapped to ISCED-style bands", "Automation risk is moderated by smallholder context, low mechanization variance, and field-based tasks.", ["agricultural wage work", "self-employment", "cooperative work", "extension training"], "Rural Maharashtra"),
  context("kenya_mixed_services_agriculture", "Kenya - Mixed services and agriculture", "KE", "Peri-urban Kenya / mixed livelihoods", "Service work, repair, agriculture, mobile-enabled small enterprise", "English / Kiswahili-ready", "Kenya education levels mapped to ISCED-style bands", "Digital tools may augment coordination and sales, but hands-on services and field work remain durable.", ["formal employment", "self-employment", "apprenticeship", "cooperative work"], "Nakuru"),
  context("bangladesh_rural_transition", "Bangladesh - Rural transition", "BD", "Rural Bangladesh / agriculture-service transition", "Crop work, local services, factory-adjacent pathways, digital training", "Bangla-ready", "Bangladesh credentials mapped to ISCED-style bands", "Routine production tasks face pressure, while field coordination, customer trust, and local services remain resilient.", ["factory work", "self-employment", "agricultural work", "short training"], "Rangpur"),
  context("nigeria_urban_services", "Nigeria - Urban services", "NG", "Lagos / urban informal services", "Repair, retail, logistics, customer support, small enterprise", "English", "Nigeria education levels mapped to ISCED-style bands", "Automation exposure is tempered by informality, trust-based service work, infrastructure variance, and low-bandwidth constraints.", ["self-employment", "apprenticeship", "formal employment", "gig/local services"], "Lagos"),
];

export const DEFAULT_CONTEXT_ID: DemoContextId = "ghana_urban_informal";

export function getDemoContext(
  contextId: DemoContextId | undefined
): DemoContextConfig {
  return (
    DEMO_CONTEXTS.find((context) => context.id === contextId) ||
    DEMO_CONTEXTS[0]
  );
}

export function dedupeSignals(
  signals: LaborMarketSignal[]
): LaborMarketSignal[] {
  const seen = new Set<string>();
  return signals.filter((signal) => {
    const key = `${signal.id}:${signal.label}:${signal.year ?? ""}`;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function context(
  id: DemoContextId,
  label: string,
  countryCode: string,
  region: string,
  focus: string,
  language: string,
  educationTaxonomy: string,
  automationCalibration: string,
  opportunityTypes: string[],
  defaultLocation: string
): DemoContextConfig {
  return {
    id,
    label,
    countryCode,
    region,
    focus,
    language,
    educationTaxonomy,
    automationCalibration,
    opportunityTypes,
    laborDataSource:
      "World Bank WDI indicators backed by ILOSTAT and ITU source series",
    defaultLocation,
    notes:
      "This context uses the same configurable schema: country code, sector signals, education taxonomy, language, opportunity types, and automation calibration can change without code changes to the graph engine.",
    fallbackSignals: SIGNALS_BY_COUNTRY[countryCode] || [],
  };
}

function signal(
  id: string,
  label: string,
  value: number,
  unit: string,
  year: number,
  source: string,
  sourceUrl: string,
  explanation: string,
  trend: "up" | "flat" | "down"
): LaborMarketSignal {
  return {
    id,
    label,
    value,
    unit,
    year,
    source,
    sourceUrl,
    explanation,
    trend,
  };
}
