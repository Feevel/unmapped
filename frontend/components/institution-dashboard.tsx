"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  FieldGroup,
  Field,
  FieldLabel,
} from "@/components/ui/field";
import {
  ArrowLeft,
  Users,
  Briefcase,
  TrendingUp,
  MapPin,
  Building2,
  Award,
  ChevronRight,
  Clock,
  Target,
  Star,
  UserCheck,
  Filter,
  Mail,
  Lock,
  LogIn,
} from "lucide-react";
import {
  Institution,
  InstitutionJobListing,
  CandidateMatch,
  DashboardMetrics,
} from "@/lib/institution-types";
import {
  getInstitution,
  getJobListings,
  getBestCandidateMatches,
  getDashboardMetrics,
  getCandidateMatches,
} from "@/lib/institution-mock-api";

function getRecommendationColor(recommendation: CandidateMatch["recommendation"]) {
  switch (recommendation) {
    case "Strong Fit":
      return "bg-emerald-500/10 text-emerald-600 border-emerald-500/20";
    case "Good Fit":
      return "bg-blue-500/10 text-blue-600 border-blue-500/20";
    case "Potential Fit":
      return "bg-amber-500/10 text-amber-600 border-amber-500/20";
    case "Development Needed":
      return "bg-slate-500/10 text-slate-600 border-slate-500/20";
  }
}

function getScoreColor(score: number) {
  if (score >= 75) return "text-emerald-600";
  if (score >= 55) return "text-blue-600";
  if (score >= 35) return "text-amber-600";
  return "text-slate-600";
}

export default function InstitutionDashboard() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");
  const [isLoggingIn, setIsLoggingIn] = useState(false);

  const [institution, setInstitution] = useState<Institution | null>(null);
  const [listings, setListings] = useState<InstitutionJobListing[]>([]);
  const [candidateMatches, setCandidateMatches] = useState<CandidateMatch[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [selectedListing, setSelectedListing] = useState<string>("all");
  const [isLoading, setIsLoading] = useState(true);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError("");
    setIsLoggingIn(true);

    // Mock login validation
    await new Promise((resolve) => setTimeout(resolve, 800));

    if (email && password) {
      // Mock successful login - in production this would validate against a backend
      setIsLoggedIn(true);
    } else {
      setLoginError("Please enter both email and password.");
    }
    setIsLoggingIn(false);
  };

  useEffect(() => {
    async function loadData() {
      if (!isLoggedIn) return;
      setIsLoading(true);
      const [instData, listingsData, matchesData, metricsData] = await Promise.all([
        getInstitution(),
        getJobListings(),
        getBestCandidateMatches(),
        getDashboardMetrics(),
      ]);
      setInstitution(instData);
      setListings(listingsData);
      setCandidateMatches(matchesData);
      setMetrics(metricsData);
      setIsLoading(false);
    }
    loadData();
  }, [isLoggedIn]);

  useEffect(() => {
    async function filterMatches() {
      if (selectedListing === "all") {
        const matches = await getBestCandidateMatches();
        setCandidateMatches(matches);
      } else {
        const matches = await getCandidateMatches(selectedListing);
        setCandidateMatches(matches);
      }
    }
    filterMatches();
  }, [selectedListing]);

  // Login Screen
  if (!isLoggedIn) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background px-4">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
              <Building2 className="h-6 w-6 text-primary" />
            </div>
            <CardTitle className="text-2xl">Institution Login</CardTitle>
            <CardDescription>
              Sign in to access your organization dashboard
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin}>
              <FieldGroup>
                <Field>
                  <FieldLabel htmlFor="email">Email Address</FieldLabel>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@organization.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </Field>
                <Field>
                  <FieldLabel htmlFor="password">Password</FieldLabel>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </Field>
              </FieldGroup>

              {loginError && (
                <p className="mt-4 text-sm text-destructive">{loginError}</p>
              )}

              <Button
                type="submit"
                className="mt-6 w-full gap-2"
                disabled={isLoggingIn}
              >
                {isLoggingIn ? (
                  <>
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <LogIn className="h-4 w-4" />
                    Sign In
                  </>
                )}
              </Button>
            </form>

            <div className="mt-6 text-center">
              <Button asChild variant="link" className="text-sm text-muted-foreground">
                <Link href="/">Back to Home</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <Button asChild variant="ghost" size="sm">
              <Link href="/" className="flex items-center gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back
              </Link>
            </Button>
            <div className="h-6 w-px bg-border" />
            <div>
              <h1 className="text-xl font-bold">{institution?.name}</h1>
              <p className="text-sm text-muted-foreground">
                {institution?.type} - {institution?.industry}
              </p>
            </div>
          </div>
          <Badge variant="outline" className="gap-1.5">
            <MapPin className="h-3.5 w-3.5" />
            {institution?.location}
          </Badge>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* Metrics Overview */}
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Candidates</p>
                  <p className="text-3xl font-bold">{metrics?.totalCandidates}</p>
                </div>
                <div className="rounded-full bg-primary/10 p-3">
                  <Users className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg. Compatibility</p>
                  <p className="text-3xl font-bold">{metrics?.averageCompatibility}%</p>
                </div>
                <div className="rounded-full bg-emerald-500/10 p-3">
                  <Target className="h-6 w-6 text-emerald-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Strong Fits</p>
                  <p className="text-3xl font-bold">{metrics?.strongFitCount}</p>
                </div>
                <div className="rounded-full bg-blue-500/10 p-3">
                  <Star className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Active Listings</p>
                  <p className="text-3xl font-bold">{listings.length}</p>
                </div>
                <div className="rounded-full bg-amber-500/10 p-3">
                  <Briefcase className="h-6 w-6 text-amber-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="candidates" className="space-y-6">
          <TabsList>
            <TabsTrigger value="candidates" className="gap-2">
              <UserCheck className="h-4 w-4" />
              Skill Passports
            </TabsTrigger>
            <TabsTrigger value="listings" className="gap-2">
              <Briefcase className="h-4 w-4" />
              Your Listings
            </TabsTrigger>
            <TabsTrigger value="insights" className="gap-2">
              <TrendingUp className="h-4 w-4" />
              Insights
            </TabsTrigger>
          </TabsList>

          {/* Candidates / Skill Passports Tab */}
          <TabsContent value="candidates" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Candidate Skill Passports</h2>
                <p className="text-muted-foreground">
                  View job seekers and their compatibility with your listings
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Filter className="h-4 w-4 text-muted-foreground" />
                <Select value={selectedListing} onValueChange={setSelectedListing}>
                  <SelectTrigger className="w-[250px]">
                    <SelectValue placeholder="Filter by listing" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Listings (Best Match)</SelectItem>
                    {listings.map((listing) => (
                      <SelectItem key={listing.id} value={listing.id}>
                        {listing.title}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid gap-4">
              {candidateMatches.map((match) => (
                <Card key={`${match.candidate.id}-${match.listingId}`} className="overflow-hidden">
                  <CardContent className="p-0">
                    <div className="flex flex-col lg:flex-row">
                      {/* Candidate Info */}
                      <div className="flex-1 border-b p-6 lg:border-b-0 lg:border-r">
                        <div className="mb-4 flex items-start justify-between">
                          <div>
                            <h3 className="text-lg font-semibold">
                              {match.candidate.fullName}
                            </h3>
                            <div className="mt-1 flex items-center gap-3 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <MapPin className="h-3.5 w-3.5" />
                                {match.candidate.location}
                              </span>
                              <span>{match.candidate.age} years old</span>
                            </div>
                          </div>
                          <Badge className={getRecommendationColor(match.recommendation)}>
                            {match.recommendation}
                          </Badge>
                        </div>

                        <p className="mb-4 text-sm text-muted-foreground">
                          {match.candidate.workDescription}
                        </p>

                        <div className="mb-4">
                          <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                            Skills
                          </p>
                          <div className="flex flex-wrap gap-1.5">
                            {match.candidate.mappedSkills.map((skill, idx) => (
                              <Badge
                                key={idx}
                                variant={
                                  match.matchedSkills.includes(skill.name)
                                    ? "default"
                                    : "secondary"
                                }
                                className="text-xs"
                              >
                                {skill.name}
                                <span className="ml-1 opacity-70">
                                  ({skill.proficiencyLevel})
                                </span>
                              </Badge>
                            ))}
                          </div>
                        </div>

                        <div className="flex items-center gap-4 text-sm">
                          <div className="flex items-center gap-1.5">
                            <Award className="h-4 w-4 text-primary" />
                            <span>Readiness: {match.candidate.overallReadinessScore}%</span>
                          </div>
                          <div className="flex items-center gap-1.5">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span>{match.candidate.activityFrequency}</span>
                          </div>
                        </div>
                      </div>

                      {/* Compatibility Score */}
                      <div className="flex flex-col justify-center bg-muted/30 p-6 lg:w-80">
                        <div className="mb-4 text-center">
                          <p className="mb-1 text-sm text-muted-foreground">
                            Compatibility with
                          </p>
                          <p className="font-medium">{match.listingTitle}</p>
                        </div>

                        <div className="mb-4 text-center">
                          <span
                            className={`text-5xl font-bold ${getScoreColor(
                              match.compatibilityScore
                            )}`}
                          >
                            {match.compatibilityScore}%
                          </span>
                        </div>

                        <Progress value={match.compatibilityScore} className="mb-4 h-2" />

                        <div className="space-y-2 text-sm">
                          <div>
                            <p className="text-muted-foreground">Matched Skills:</p>
                            <p className="font-medium">
                              {match.matchedSkills.length > 0
                                ? match.matchedSkills.join(", ")
                                : "None"}
                            </p>
                          </div>
                          {match.missingSkills.length > 0 && (
                            <div>
                              <p className="text-muted-foreground">Skills Gap:</p>
                              <p className="text-amber-600">
                                {match.missingSkills.join(", ")}
                              </p>
                            </div>
                          )}
                        </div>

                        <Button className="mt-4 gap-2">
                          View Full Passport
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Listings Tab */}
          <TabsContent value="listings" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold">Your Job Listings</h2>
              <p className="text-muted-foreground">
                Manage your active opportunities and see candidate matches
              </p>
            </div>

            <div className="grid gap-4">
              {listings.map((listing) => (
                <Card key={listing.id}>
                  <CardContent className="p-6">
                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                      <div className="flex-1">
                        <div className="mb-2 flex items-center gap-3">
                          <h3 className="text-lg font-semibold">{listing.title}</h3>
                          <Badge
                            variant={listing.status === "Active" ? "default" : "secondary"}
                          >
                            {listing.status}
                          </Badge>
                        </div>
                        <p className="mb-3 text-sm text-muted-foreground">
                          {listing.description}
                        </p>
                        <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Building2 className="h-3.5 w-3.5" />
                            {listing.department}
                          </span>
                          <span className="flex items-center gap-1">
                            <MapPin className="h-3.5 w-3.5" />
                            {listing.location}
                          </span>
                          <Badge variant="outline">{listing.type}</Badge>
                          {listing.salary && <span>{listing.salary}</span>}
                        </div>
                      </div>

                      <div className="flex items-center gap-6 lg:gap-8">
                        <div className="text-center">
                          <p className="text-2xl font-bold">{listing.applicants}</p>
                          <p className="text-xs text-muted-foreground">Applicants</p>
                        </div>
                        <div className="text-center">
                          <p className="text-2xl font-bold text-primary">
                            {listing.matchedCandidates}
                          </p>
                          <p className="text-xs text-muted-foreground">Matches</p>
                        </div>
                        <Button
                          variant="outline"
                          onClick={() => setSelectedListing(listing.id)}
                        >
                          View Candidates
                        </Button>
                      </div>
                    </div>

                    <div className="mt-4 border-t pt-4">
                      <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                        Required Skills
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {listing.requiredSkills.map((skill, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {skill}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold">Talent Insights</h2>
              <p className="text-muted-foreground">
                Understand the candidate pool and skill availability
              </p>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              {/* Skills in Demand */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5" />
                    Top Skills in Demand
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {metrics?.topSkillsInDemand.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="font-medium">{item.skill}</span>
                        <div className="flex items-center gap-3">
                          <Progress
                            value={(item.count / listings.length) * 100}
                            className="h-2 w-24"
                          />
                          <span className="w-16 text-right text-sm text-muted-foreground">
                            {item.count} listings
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Candidates by Location */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MapPin className="h-5 w-5" />
                    Candidates by Location
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {metrics?.candidatesByLocation.map((item, idx) => (
                      <div key={idx} className="flex items-center justify-between">
                        <span className="font-medium">{item.location}</span>
                        <div className="flex items-center gap-3">
                          <Progress
                            value={(item.count / (metrics?.totalCandidates || 1)) * 100}
                            className="h-2 w-24"
                          />
                          <span className="w-20 text-right text-sm text-muted-foreground">
                            {item.count} candidates
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Fit Distribution */}
              <Card className="lg:col-span-2">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UserCheck className="h-5 w-5" />
                    Candidate Fit Distribution
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="rounded-lg border bg-emerald-500/5 p-4 text-center">
                      <p className="text-4xl font-bold text-emerald-600">
                        {metrics?.strongFitCount}
                      </p>
                      <p className="mt-1 text-sm text-muted-foreground">Strong Fits</p>
                      <p className="text-xs text-emerald-600">75%+ compatibility</p>
                    </div>
                    <div className="rounded-lg border bg-blue-500/5 p-4 text-center">
                      <p className="text-4xl font-bold text-blue-600">
                        {metrics?.goodFitCount}
                      </p>
                      <p className="mt-1 text-sm text-muted-foreground">Good Fits</p>
                      <p className="text-xs text-blue-600">55-74% compatibility</p>
                    </div>
                    <div className="rounded-lg border bg-amber-500/5 p-4 text-center">
                      <p className="text-4xl font-bold text-amber-600">
                        {metrics?.potentialFitCount}
                      </p>
                      <p className="mt-1 text-sm text-muted-foreground">Potential Fits</p>
                      <p className="text-xs text-amber-600">35-54% compatibility</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
