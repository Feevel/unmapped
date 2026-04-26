"use client";

import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Progress } from "@/components/ui/progress";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  Send,
  Bot,
  User,
  Sparkles,
  Shield,
  Briefcase,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  MapPin,
  Clock,
  Building2,
  ExternalLink,
} from "lucide-react";
import {
  Message,
  SeekerProfile,
  SkillPassport,
  ChatStep,
  CHAT_QUESTIONS,
} from "@/lib/seeker-chat-types";
import { generateSkillPassport } from "@/lib/seeker-mock-api";

const STEP_ORDER: ChatStep[] = [
  "name",
  "work_description",
  "frequency",
  "demographics",
  "complete",
];

export function SeekerChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [currentStep, setCurrentStep] = useState<ChatStep>("name");
  const [profile, setProfile] = useState<Partial<SeekerProfile>>({});
  const [skillPassport, setSkillPassport] = useState<SkillPassport | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const hasInitialized = useRef(false);

  const progressPercentage =
    (STEP_ORDER.indexOf(currentStep) / (STEP_ORDER.length - 1)) * 100;

  useEffect(() => {
    // Initial bot message - only run once
    if (!hasInitialized.current && messages.length === 0) {
      hasInitialized.current = true;
      addBotMessage(CHAT_QUESTIONS.name);
    }
  }, []);

  useEffect(() => {
    // Scroll to bottom on new messages
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const addBotMessage = (content: string) => {
    setIsTyping(true);
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: `bot-${Date.now()}`,
          role: "bot",
          content,
          timestamp: new Date(),
        },
      ]);
      setIsTyping(false);
    }, 800);
  };

  const handleSendMessage = () => {
    if (!input.trim() || currentStep === "complete") return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    // Store the answer based on current step
    const updatedProfile = { ...profile };
    switch (currentStep) {
      case "name":
        updatedProfile.fullName = input;
        break;
      case "work_description":
        updatedProfile.workDescription = input;
        break;
      case "frequency":
        updatedProfile.activityFrequency = input;
        break;
      case "demographics":
        updatedProfile.demographics = input;
        break;
    }
    setProfile(updatedProfile);

    // Move to next step
    const currentIndex = STEP_ORDER.indexOf(currentStep);
    const nextStep = STEP_ORDER[currentIndex + 1];
    setCurrentStep(nextStep);

    // Add bot response for next step
    setInput("");
    setTimeout(() => {
      addBotMessage(CHAT_QUESTIONS[nextStep]);
    }, 300);
  };

  const handleGeneratePassport = async () => {
    setIsGenerating(true);
    try {
      const passport = await generateSkillPassport(profile as SeekerProfile);
      setSkillPassport(passport);
    } catch (error) {
      console.error("Error generating skill passport:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  const getRiskColor = (level: "Low" | "Medium" | "High") => {
    switch (level) {
      case "Low":
        return "bg-green-500/10 text-green-600 border-green-500/20";
      case "Medium":
        return "bg-yellow-500/10 text-yellow-600 border-yellow-500/20";
      case "High":
        return "bg-red-500/10 text-red-600 border-red-500/20";
    }
  };

  const getRiskIcon = (level: "Low" | "Medium" | "High") => {
    switch (level) {
      case "Low":
        return <CheckCircle className="h-4 w-4" />;
      case "Medium":
        return <AlertTriangle className="h-4 w-4" />;
      case "High":
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  if (skillPassport) {
    return (
      <div className="flex flex-col gap-6">
        {/* Skill Passport Header */}
        <Card className="border-primary/20 bg-gradient-to-br from-primary/5 to-transparent">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">Skill Passport</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    ID: {skillPassport.id}
                  </p>
                </div>
              </div>
              <Badge variant="outline" className="text-sm">
                Generated {skillPassport.generatedAt.toLocaleDateString()}
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="rounded-lg bg-background p-4">
                <p className="text-sm text-muted-foreground">Name</p>
                <p className="font-semibold">{skillPassport.profile.fullName}</p>
              </div>
              <div className="rounded-lg bg-background p-4">
                <p className="text-sm text-muted-foreground">Demographics</p>
                <p className="font-semibold">{skillPassport.profile.demographics}</p>
              </div>
              <div className="rounded-lg bg-background p-4">
                <p className="text-sm text-muted-foreground">Readiness Score</p>
                <div className="flex items-center gap-2">
                  <p className="text-2xl font-bold text-primary">
                    {skillPassport.overallReadinessScore}%
                  </p>
                  <TrendingUp className="h-5 w-5 text-green-500" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Mapped Skills */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5" />
              ESCO/ISCO Mapped Skills
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {skillPassport.mappedSkills.map((skill, index) => (
                <div
                  key={index}
                  className="flex items-start justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{skill.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {skill.iscoCategory}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      ESCO: {skill.escoCode}
                    </p>
                  </div>
                  <Badge variant="secondary">{skill.proficiencyLevel}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Opportunity Recommendations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Briefcase className="h-5 w-5" />
              Opportunity Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {skillPassport.opportunities.map((opp, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between rounded-lg border p-4"
                >
                  <div>
                    <p className="font-medium">{opp.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {opp.organization} - {opp.location}
                    </p>
                  </div>
                  <div className="flex items-center gap-3">
                    <Badge variant="outline">{opp.type}</Badge>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-primary">
                        {opp.matchScore}% Match
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Job Listings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Matching Job Listings
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Jobs currently on the market that match your Skill Passport
            </p>
          </CardHeader>
          <CardContent>
            {skillPassport.jobListings.length > 0 ? (
              <div className="space-y-4">
                {skillPassport.jobListings.map((job) => (
                  <div
                    key={job.id}
                    className="rounded-lg border p-4 transition-colors hover:bg-muted/50"
                  >
                    <div className="mb-3 flex items-start justify-between">
                      <div>
                        <h4 className="font-semibold">{job.title}</h4>
                        <p className="text-sm text-muted-foreground">
                          {job.company}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          className="bg-primary/10 text-primary border-primary/20"
                        >
                          {job.matchScore}% Match
                        </Badge>
                      </div>
                    </div>

                    <p className="mb-3 text-sm text-muted-foreground line-clamp-2">
                      {job.description}
                    </p>

                    <div className="mb-3 flex flex-wrap items-center gap-3 text-sm text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {job.isRemote ? "Remote" : job.location}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3.5 w-3.5" />
                        {job.postedDate}
                      </span>
                      <Badge variant="outline" className="text-xs">
                        {job.type}
                      </Badge>
                      {job.salary && (
                        <span className="text-xs font-medium text-foreground">
                          {job.salary}
                        </span>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex flex-wrap gap-1.5">
                        {job.matchedSkills.slice(0, 3).map((skill, idx) => (
                          <Badge
                            key={idx}
                            variant="secondary"
                            className="text-xs"
                          >
                            {skill}
                          </Badge>
                        ))}
                        {job.matchedSkills.length > 3 && (
                          <Badge variant="secondary" className="text-xs">
                            +{job.matchedSkills.length - 3} more
                          </Badge>
                        )}
                      </div>
                      <Button size="sm" variant="outline" className="gap-1.5">
                        View Details
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-muted-foreground">
                <Briefcase className="mx-auto mb-2 h-8 w-8 opacity-50" />
                <p>No matching job listings found at this time.</p>
                <p className="text-sm">Check back later for new opportunities.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* AI Readiness Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              AI Readiness Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {skillPassport.aiInsights.map((insight, index) => (
                <div key={index} className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <p className="font-medium">{insight.category}</p>
                    <Badge className={getRiskColor(insight.riskLevel)}>
                      {getRiskIcon(insight.riskLevel)}
                      <span className="ml-1">{insight.riskLevel} Risk</span>
                    </Badge>
                  </div>
                  <p className="mb-2 text-sm text-muted-foreground">
                    {insight.description}
                  </p>
                  <div className="rounded bg-muted/50 p-2">
                    <p className="text-sm">
                      <span className="font-medium">Recommendation:</span>{" "}
                      {insight.recommendation}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Reset Button */}
        <Button
          variant="outline"
          onClick={() => {
            setSkillPassport(null);
            setMessages([]);
            setCurrentStep("name");
            setProfile({});
            hasInitialized.current = false;
            setTimeout(() => {
              if (!hasInitialized.current) {
                hasInitialized.current = true;
                addBotMessage(CHAT_QUESTIONS.name);
              }
            }, 100);
          }}
        >
          Start New Assessment
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-12rem)] flex-col rounded-lg border bg-card">
      {/* Progress Header */}
      <div className="border-b p-4">
        <div className="mb-2 flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Onboarding Progress</span>
          <span className="font-medium">{Math.round(progressPercentage)}%</span>
        </div>
        <Progress value={progressPercentage} className="h-2" />
      </div>

      {/* Chat Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start gap-3 ${
                message.role === "user" ? "flex-row-reverse" : ""
              }`}
            >
              <div
                className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                  message.role === "bot"
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted"
                }`}
              >
                {message.role === "bot" ? (
                  <Bot className="h-4 w-4" />
                ) : (
                  <User className="h-4 w-4" />
                )}
              </div>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                  message.role === "bot"
                    ? "bg-muted text-foreground"
                    : "bg-primary text-primary-foreground"
                }`}
              >
                <p className="text-sm leading-relaxed">{message.content}</p>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="flex items-start gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                <Bot className="h-4 w-4" />
              </div>
              <div className="rounded-2xl bg-muted px-4 py-3">
                <div className="flex gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-foreground/40 [animation-delay:-0.3s]"></span>
                  <span className="h-2 w-2 animate-bounce rounded-full bg-foreground/40 [animation-delay:-0.15s]"></span>
                  <span className="h-2 w-2 animate-bounce rounded-full bg-foreground/40"></span>
                </div>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <Separator />

      {/* Input Area */}
      <div className="p-4">
        {currentStep === "complete" ? (
          <Button
            onClick={handleGeneratePassport}
            disabled={isGenerating}
            className="w-full"
            size="lg"
          >
            {isGenerating ? (
              <>
                <Sparkles className="mr-2 h-4 w-4 animate-spin" />
                Generating Skill Passport...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Generate Skill Passport
              </>
            )}
          </Button>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex gap-2"
          >
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your response..."
              className="flex-1"
              disabled={isTyping}
            />
            <Button type="submit" size="icon" disabled={!input.trim() || isTyping}>
              <Send className="h-4 w-4" />
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
