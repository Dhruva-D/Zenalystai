import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ArrowRight, Shield, Calendar, XCircle } from "lucide-react";

export const CTASection = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  return (
    <section ref={ref} className="py-20 px-4 relative overflow-hidden">
      <div className="container max-w-5xl mx-auto relative z-10">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="relative"
        >
          {/* Glow effect */}
          <div className="absolute inset-0 bg-gradient-to-t from-primary/30 to-transparent blur-3xl -z-10" />
        </motion.div>
      </div>
    </section>
  );
};
