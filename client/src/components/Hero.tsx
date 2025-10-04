import { motion } from "framer-motion";
import { ArrowRight, Play, TrendingUp, Zap, Shield, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-dashboard.png";

export const Hero = () => {
  return (
    <section className="relative min-h-[100vh] lg:min-h-[120vh] flex items-center justify-center overflow-hidden px-4 py-20 bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Gradient mesh background */}
      <div className="absolute inset-0 bg-gradient-mesh opacity-40" />
      
      {/* Animated gradient orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-20 right-20 w-96 h-96 bg-gradient-to-r from-blue-400 to-indigo-400 rounded-full blur-3xl"
      />
      
      <motion.div
        animate={{
          scale: [1, 1.3, 1],
          opacity: [0.2, 0.4, 0.2],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 1,
        }}
        className="absolute bottom-20 left-20 w-96 h-96 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full blur-3xl"
      />

      <div className="container max-w-[1400px] mx-auto relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-8 lg:gap-12 items-center">
          {/* Left side - Content */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8 lg:col-span-2"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-accent rounded-full text-white text-sm font-medium shadow-lg">
              <Zap className="w-4 h-4" />
              <span>AI-Powered Data Analytics</span>
            </div>

            <h1 className="text-5xl md:text-6xl lg:text-7xl font-bold leading-tight">
              Transform Your{" "}
              <span className="bg-gradient-to-r from-primary via-accent to-indigo-600 bg-clip-text text-transparent">
                Business Data
              </span>{" "}
              Into Insights
            </h1>

            <p className="text-xl text-muted-foreground leading-relaxed">
              Advanced AI-powered analytics platform that processes your data files, 
              performs intelligent analysis, and delivers actionable business 
              intelligence with unprecedented accuracy and speed.
            </p>

            {/* Features list */}
            <div className="space-y-3">
              {[
                { icon: TrendingUp, text: "99.9% Analysis Accuracy" },
                { icon: Zap, text: "Process 10K+ Records in <1 Minute" },
                { icon: Shield, text: "Enterprise-Grade Security" },
              ].map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-accent flex items-center justify-center shadow-md">
                    <feature.icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-lg font-medium">{feature.text}</span>
                </motion.div>
              ))}
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4 pt-4">
              <Button 
                size="lg" 
                className="bg-gradient-cta text-white shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-105"
                onClick={() => window.location.href = '/upload'}
              >
                Upload Your Data
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
              
              <Button 
                size="lg" 
                variant="outline"
                className="border-2 border-primary hover:bg-primary/5"
                onClick={() => window.location.href = '/analyze'}
              >
                <BarChart3 className="mr-2 w-5 h-5" />
                Start Analysis
              </Button>
            </div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.5 }}
              className="grid grid-cols-3 gap-6 pt-8 border-t border-border"
            >
              {[
                { value: "10K+", label: "Records/Min" },
                { value: "99.9%", label: "Accuracy" },
                { value: "<1min", label: "Processing" },
              ].map((stat, index) => (
                <div key={index} className="text-center">
                  <div className="text-3xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-sm text-muted-foreground mt-1">
                    {stat.label}
                  </div>
                </div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right side - Image */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative lg:col-span-3 scale-105 md:scale-110 lg:scale-125 xl:scale-150 2xl:scale-175"
          >
            <div className="relative rounded-2xl overflow-hidden shadow-2xl">
              <img 
                src={heroImage} 
                alt="Analytics Dashboard Preview" 
                className="w-full h-auto max-w-none min-h-[350px] md:min-h-[450px] lg:min-h-[600px] xl:min-h-[700px] object-cover"
              />
              
              {/* Floating badge */}
              <motion.div
                animate={{
                  y: [0, -10, 0],
                }}
                transition={{
                  duration: 3,
                  repeat: Infinity,
                  ease: "easeInOut",
                }}
                className="absolute top-8 right-8 bg-white/90 backdrop-blur-sm rounded-xl px-4 py-3 shadow-xl border border-primary/20"
              >
                <div className="text-xs text-muted-foreground">Live Analytics</div>
                <div className="text-2xl font-bold bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent">
                  98.7%
                </div>
              </motion.div>

              {/* Decorative elements */}
              <div className="absolute inset-0 ring-1 ring-inset ring-primary/10 rounded-2xl" />
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};
