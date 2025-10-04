import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { Upload, Settings, BarChart2, Target } from "lucide-react";

export const HowItWorks = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const steps = [
    { icon: Upload, title: "Upload", description: "Drag & drop your Excel and PDF files" },
    { icon: Settings, title: "Process", description: "AI-powered ETL pipeline works its magic" },
    { icon: BarChart2, title: "Analyze", description: "Get instant insights and reports" },
    { icon: Target, title: "Act", description: "Make data-driven business decisions" },
  ];

  return (
    <section ref={ref} className="py-20 px-4 relative overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 bg-gradient-to-b from-background via-card to-background" />
      
      <div className="container max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            How It{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Works
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From upload to insights in four simple steps
          </p>
        </motion.div>

        <div className="relative">
          {/* Connection line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-primary/0 via-primary to-primary/0 -translate-y-1/2" />

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative">
            {steps.map((step, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={inView ? { opacity: 1, scale: 1 } : {}}
                transition={{ duration: 0.5, delay: index * 0.15 }}
                className="relative"
              >
                <div className="flex flex-col items-center text-center">
                  {/* Icon circle */}
                  <motion.div
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    className="relative mb-6"
                  >
                    <div className="w-20 h-20 rounded-full bg-gradient-accent flex items-center justify-center relative z-10 border-4 border-background">
                      <step.icon className="w-10 h-10 text-white" />
                    </div>
                    {/* Glow effect */}
                    <div className="absolute inset-0 rounded-full bg-primary blur-xl opacity-50 animate-pulse-glow" />
                  </motion.div>

                  {/* Step number */}
                  <div className="text-sm font-bold text-primary mb-2">STEP {index + 1}</div>

                  {/* Title */}
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>

                  {/* Description */}
                  <p className="text-sm text-muted-foreground max-w-xs">{step.description}</p>
                </div>

                {/* Arrow for mobile */}
                {index < steps.length - 1 && (
                  <div className="md:hidden flex justify-center my-4">
                    <div className="w-px h-8 bg-gradient-to-b from-primary to-primary/0" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
