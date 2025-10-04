import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { Target, Zap, BarChart } from "lucide-react";

export const SolutionOverview = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const features = [
    {
      icon: Target,
      title: "Intelligent Data Processing",
      points: ["AI-powered data extraction", "Multi-format support", "Automated cleaning"],
    },
    {
      icon: Zap,
      title: "Advanced Analytics Engine",
      points: ["Pattern recognition", "Trend analysis", "Real-time processing"],
    },
    {
      icon: BarChart,
      title: "Actionable Insights",
      points: ["Interactive dashboards", "Predictive analytics", "Smart recommendations"],
    },
  ];

  return (
    <section ref={ref} className="py-20 px-4 relative">
      <div className="container max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Your Complete{" "}
            <span className="bg-gradient-to-r from-accent via-primary to-accent bg-clip-text text-transparent bg-[length:200%_auto] animate-gradient-shift">
              Data Analytics
            </span>{" "}
            Platform
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Transform raw data into actionable business intelligence with AI-powered analytics
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: index * 0.15 }}
              whileHover={{ rotateY: 5, scale: 1.05 }}
              style={{ perspective: 1000 }}
              className="group relative"
            >
              <div className="h-full p-8 rounded-2xl bg-gradient-card border border-white/10 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 relative overflow-hidden">
                {/* Hover gradient effect */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/5 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                
                <div className="relative">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-accent flex items-center justify-center mb-6 group-hover:scale-110 group-hover:rotate-3 transition-all duration-300">
                    <feature.icon className="w-8 h-8 text-white" />
                  </div>
                  
                  <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                  
                  <ul className="space-y-3">
                    {feature.points.map((point, i) => (
                      <li key={i} className="flex items-start gap-2 text-muted-foreground">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent mt-2 flex-shrink-0" />
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
