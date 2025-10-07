import { Navbar, Footer, FloatingScrollToTop } from "@/components/layout";
import { 
  Hero, 
  ProblemStatement, 
  SolutionOverview, 
  HowItWorks, 
  FeaturesGrid, 
  Benefits, 
  CTASection 
} from "@/components/landing";

const Index = () => {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <Navbar />
      <div>
        <Hero />
        <ProblemStatement />
        <SolutionOverview />
        <HowItWorks />
        <FeaturesGrid />
        <Benefits />
        <CTASection />
        <Footer />
      </div>
      <FloatingScrollToTop />
    </div>
  );
};

export default Index;
