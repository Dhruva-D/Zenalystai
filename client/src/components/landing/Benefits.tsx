import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { Zap, DollarSign, Target, TrendingUp } from "lucide-react";

export const Benefits = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const benefits = [
    {
      icon: Zap,
      stat: "95%",
      label: "Time Saved",
      description: "Automate hours of manual reconciliation work",
    },
    {
      icon: DollarSign,
      stat: "30%+",
      label: "Profit Increase",
      description: "Identify loss-making products instantly",
    },
    {
      icon: Target,
      stat: "99.9%",
      label: "Accuracy",
      description: "Eliminate human errors in data matching",
    },
    {
      icon: TrendingUp,
      stat: "Real-time",
      label: "Insights",
      description: "Make data-driven decisions faster",
    },
  ];

  return (
    <section ref={ref} className="py-20 px-4 relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-b from-card via-background to-card" />
      
      <div className="container max-w-6xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Why Choose{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              ABC Analytics
            </span>
            ?
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Transform your bookstore operations with measurable results
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {benefits.map((benefit, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={inView ? { opacity: 1, scale: 1 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="group"
            >
              <div className="relative h-full">
                {/* Card */}
                <div className="h-full p-8 rounded-2xl bg-gradient-card border border-white/10 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 relative overflow-hidden">
                  {/* Animated gradient background on hover */}
                  <motion.div
                    className="absolute inset-0 bg-gradient-to-br from-primary/10 via-accent/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                  />
                  
                  <div className="relative">
                    {/* Icon */}
                    <div className="w-14 h-14 rounded-xl bg-gradient-accent flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                      <benefit.icon className="w-7 h-7 text-white" />
                    </div>

                    {/* Stat */}
                    <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent mb-2">
                      {benefit.stat}
                    </div>

                    {/* Label */}
                    <div className="text-xl font-semibold mb-3">{benefit.label}</div>

                    {/* Description */}
                    <p className="text-sm text-muted-foreground">{benefit.description}</p>
                  </div>
                </div>

                {/* Glow effect */}
                <div className="absolute inset-0 bg-gradient-to-t from-primary/20 to-transparent blur-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 -z-10" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
