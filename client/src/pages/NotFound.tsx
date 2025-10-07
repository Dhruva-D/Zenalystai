import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Navbar } from "@/components/layout";
import { Button } from "@/components/ui/button";
import { Home } from "lucide-react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error("404 Error: User attempted to access non-existent route:", location.pathname);
  }, [location.pathname]);

  return (
    <>
      <Navbar />
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-slate-50 via-white to-blue-50 pt-16">
        <div className="text-center max-w-2xl mx-auto px-4">
          <h1 className="mb-4 text-6xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">404</h1>
          <h2 className="mb-4 text-3xl font-semibold">Page Not Found</h2>
          <p className="mb-8 text-xl text-muted-foreground">The page you're looking for doesn't exist or has been moved.</p>
          <Button 
            size="lg"
            className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
            onClick={() => window.location.href = '/'}
          >
            <Home className="mr-2 w-5 h-5" />
            Return to Home
          </Button>
        </div>
      </div>
    </>
  );
};

export default NotFound;
