import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft } from "lucide-react";
import { SeekerChat } from "@/components/seeker-chat";

export default function SeekerDashboard() {
  return (
    <div className="min-h-screen p-4 md:p-6">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6">
          <Button asChild variant="ghost" size="sm">
            <Link href="/" className="flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Home
            </Link>
          </Button>
        </div>

        <header className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight md:text-4xl">
            Job Seeker Onboarding
          </h1>
          <p className="mt-2 text-muted-foreground">
            Tell us about your skills and experience to create your Skill Passport
          </p>
        </header>

        <SeekerChat />
      </div>
    </div>
  );
}
