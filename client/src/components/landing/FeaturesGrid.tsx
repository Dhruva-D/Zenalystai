import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { GitCompare, TrendingUp, Clock, DollarSign, FileSpreadsheet, Shield, Mail, Layers } from "lucide-react";

export const FeaturesGrid = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const features = [
    {
      icon: GitCompare,
      title: "3-Way Match Analysis",
      description: "Automatically verify purchase orders, receipts, and invoices with instant mismatch detection",
      size: "large",
      gradient: "from-primary to-accent",
    },
    {
      icon: TrendingUp,
      title: "Profitability Dashboard",
      description: "Track margins by vendor, category, and product with real-time calculations",
      size: "large",
      gradient: "from-accent to-primary",
    },
    {
      icon: Clock,
      title: "Inventory Ageing",
      description: "Identify slow-moving stock and optimize inventory turnover",
      size: "medium",
      gradient: "from-primary to-purple-500",
    },
    {
      icon: DollarSign,
      title: "FIFO Valuation",
      description: "Accurate cost calculations using first-in-first-out methodology",
      size: "medium",
      gradient: "from-purple-500 to-primary",
    },
    {
      icon: Layers,
      title: "Cost Analysis",
      description: "Deep dive into product costs and pricing strategies",
      size: "medium",
      gradient: "from-accent to-cyan-500",
    },
    {
      icon: FileSpreadsheet,
      title: "Excel Export",
      description: "One-click export of all reports in Excel format",
      size: "small",
      gradient: "from-primary to-blue-600",
    },
    {
      icon: Shield,
      title: "Role-based Access",
      description: "Secure data with granular permissions",
      size: "small",
      gradient: "from-cyan-500 to-accent",
    },
    {
      icon: Mail,
      title: "Smart Alerts",
      description: "Email notifications for mismatches and insights",
      size: "small",
      gradient: "from-purple-500 to-primary",
    },
  ];

  return (
    <section ref={ref} className="py-20 px-4 relative">
      <div className="container max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            Powerful Features,{" "}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Simple to Use
            </span>
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to manage your bookstore data efficiently
          </p>
        </motion.div>

        {/* Bento grid layout */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const colSpan =
              feature.size === "large"
                ? "lg:col-span-2"
                : feature.size === "medium"
                ? "lg:col-span-1"
                : "lg:col-span-1";
            
            const rowSpan = feature.size === "large" ? "lg:row-span-2" : "";

            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 30 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                whileHover={{ y: -5 }}
                className={`${colSpan} ${rowSpan} group`}
              >
                <div className="h-full p-6 rounded-2xl bg-gradient-card border border-white/10 backdrop-blur-sm hover:border-primary/50 transition-all duration-300 relative overflow-hidden">
                  {/* Hover gradient effect */}
                  <div className="absolute inset-0 bg-gradient-to-br from-primary/0 to-accent/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  
                  <div className="relative h-full flex flex-col">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-4 group-hover:scale-110 group-hover:rotate-3 transition-all`}>
                      <feature.icon className="w-6 h-6 text-white" />
                    </div>
                    
                    <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground flex-grow">{feature.description}</p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
