import { Hero } from "@/components/Hero";
import { ProblemStatement } from "@/components/ProblemStatement";
import { SolutionOverview } from "@/components/SolutionOverview";
import { HowItWorks } from "@/components/HowItWorks";
import { FeaturesGrid } from "@/components/FeaturesGrid";
import { Benefits } from "@/components/Benefits";
import { CTASection } from "@/components/CTASection";
import { Footer } from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Hero />
      <ProblemStatement />
      <SolutionOverview />
      <HowItWorks />
      <FeaturesGrid />
      <Benefits />
      <CTASection />
      <Footer />
    </div>
  );
};

export default Index;
