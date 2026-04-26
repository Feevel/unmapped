import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <main className="flex flex-col items-center gap-8 px-6 py-16 text-center">
        <div className="flex flex-col items-center gap-4">
          <h1 className="text-6xl font-bold tracking-tight sm:text-7xl md:text-8xl">
            UNMAPPED
          </h1>
          <p className="max-w-lg text-lg text-muted-foreground text-balance">
            A configurable job-economy infrastructure layer connecting seekers
            with institutions to build pathways for opportunity.
          </p>
        </div>

        <div className="flex flex-col gap-4 sm:flex-row">
          <Button asChild size="lg" className="min-w-[140px]">
            <Link href="/seeker">Seeker</Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="min-w-[140px]">
            <Link href="/institution">Institution</Link>
          </Button>
        </div>
      </main>
    </div>
  );
}
