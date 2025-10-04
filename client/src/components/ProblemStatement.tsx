import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { FileText, Clock, DollarSign, BarChart3 } from "lucide-react";

export const ProblemStatement = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const problems = [
    {
      icon: FileText,
      title: "Manual Data Entry",
      description: "Hours wasted on error-prone manual reconciliation",
    },
    {
      icon: Clock,
      title: "Time-Consuming",
      description: "Days to process what should take minutes",
    },
    {
      icon: DollarSign,
      title: "Hidden Costs",
      description: "Inventory discrepancies eating into profits",
    },
    {
      icon: BarChart3,
      title: "No Real-Time Insights",
      description: "Making decisions based on outdated data",
    },
  ];

  return (
    <section ref={ref} className="py-20 px-4 relative overflow-hidden">
      <div className="container max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            The Challenge{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Bookstores Face
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Traditional data management holds your business back
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {problems.map((problem, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              className="group"
            >
              <div className="h-full p-6 rounded-2xl bg-gradient-card border border-white/10 backdrop-blur-sm hover:border-primary/50 transition-all duration-300">
                <div className="w-12 h-12 rounded-xl bg-gradient-accent flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <problem.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{problem.title}</h3>
                <p className="text-sm text-muted-foreground">{problem.description}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
