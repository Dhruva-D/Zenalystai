import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
import { 
  Zap, 
  Shield, 
  Users, 
  Award, 
  TrendingUp, 
  Globe, 
  Heart,
  Lightbulb,
  Target,
  Star
} from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Navbar } from "@/components/layout";
import { FloatingScrollToTop } from "@/components/layout";

export const About = () => {
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.1 });

  const stats = [
    { value: "50K+", label: "Records Processed", icon: TrendingUp },
    { value: "99.9%", label: "Accuracy Rate", icon: Target },
    { value: "100+", label: "Happy Clients", icon: Users },
    { value: "24/7", label: "Support", icon: Shield }
  ];

  const values = [
    {
      icon: Lightbulb,
      title: "Innovation",
      description: "Constantly pushing the boundaries of what's possible with AI and data analytics"
    },
    {
      icon: Shield,
      title: "Reliability",
      description: "Building trust through consistent, accurate, and secure data processing"
    },
    {
      icon: Heart,
      title: "Customer Focus",
      description: "Putting our customers' success at the center of everything we do"
    },
    {
      icon: Globe,
      title: "Accessibility",
      description: "Making advanced analytics accessible to businesses of all sizes"
    }
  ];

  const team = [
    {
      name: "Alex Chen",
      role: "CEO & Founder",
      description: "AI researcher with 10+ years in data analytics",
      gradient: "from-blue-500 to-cyan-500"
    },
    {
      name: "Sarah Johnson",
      role: "CTO",
      description: "Full-stack engineer and machine learning expert",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      name: "Michael Rodriguez",
      role: "Lead Data Scientist",
      description: "PhD in Statistics with expertise in predictive modeling",
      gradient: "from-green-500 to-emerald-500"
    },
    {
      name: "Emma Thompson",
      role: "Head of Product",
      description: "Product strategist focused on user experience",
      gradient: "from-orange-500 to-red-500"
    }
  ];

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-indigo-50 pt-24 pb-12">
        <div className="container max-w-7xl mx-auto px-4">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-16"
        >
          <Badge variant="secondary" className="mb-4 px-4 py-2">
            <Star className="w-4 h-4 mr-2" />
            About ZenalystAI
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold mb-6">
            Transforming Data Into{" "}
            <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Actionable Insights
            </span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
            We're on a mission to democratize data analytics, making it accessible, 
            accurate, and actionable for businesses worldwide through cutting-edge AI technology.
          </p>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          ref={ref}
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16"
        >
          {stats.map((stat, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
              className="text-center"
            >
              <Card className="bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300">
                <CardContent className="p-6">
                  <div className="w-12 h-12 mx-auto mb-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center">
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="text-3xl font-bold text-gray-900 mb-2">{stat.value}</div>
                  <div className="text-muted-foreground text-sm">{stat.label}</div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>

        {/* Story Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="max-w-4xl mx-auto mb-16"
        >
          {/* <Card className="bg-gradient-to-br from-white to-blue-50/50 backdrop-blur-sm shadow-xl">
            <CardContent className="p-12">
              <h2 className="text-3xl font-bold mb-6 text-center">Our Story</h2>
              <div className="prose prose-lg max-w-none text-muted-foreground leading-relaxed space-y-4">
                <p>
                  Founded in 2023, ZenalystAI emerged from a simple observation: businesses were drowning in data 
                  but starving for insights. Our founders, having worked with companies struggling to make sense of 
                  their Excel files, PDFs, and scattered data sources, knew there had to be a better way.
                </p>
                <p>
                  We built ZenalystAI to bridge the gap between raw data and actionable business intelligence. 
                  Our platform combines advanced AI algorithms with intuitive design, making sophisticated 
                  analytics accessible to everyone—not just data scientists.
                </p>
                <p>
                  Today, we're proud to serve businesses of all sizes, helping them unlock the hidden potential 
                  in their data and make informed decisions that drive growth and success.
                </p>
              </div>
            </CardContent>
          </Card> */}
        </motion.div>

        {/* Values Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.5 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold text-center mb-12">Our Values</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.6 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="text-center"
              >
                <Card className="h-full bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300">
                  <CardContent className="p-8">
                    <div className="w-16 h-16 mx-auto mb-6 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full flex items-center justify-center">
                      <value.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-3">{value.title}</h3>
                    <p className="text-muted-foreground text-sm leading-relaxed">{value.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Team Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mb-16"
        >
        {/* <h2 className="text-3xl font-bold text-center mb-12">Meet Our Team</h2> */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* {team.map((member, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.6, delay: 0.8 + index * 0.1 }}
                whileHover={{ scale: 1.05 }}
                className="text-center"
              >
                <Card className="bg-white/80 backdrop-blur-sm shadow-lg hover:shadow-xl transition-all duration-300">
                  <CardContent className="p-8">
                    <div className={`w-20 h-20 mx-auto mb-4 bg-gradient-to-r ${member.gradient} rounded-full flex items-center justify-center text-white text-2xl font-bold`}>
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <h3 className="text-xl font-semibold mb-1">{member.name}</h3>
                    <p className="text-blue-600 font-medium mb-3">{member.role}</p>
                    <p className="text-muted-foreground text-sm">{member.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))} */}
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6, delay: 0.9 }}
          className="text-center"
        >
          <Card className="bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-2xl">
            <CardContent className="p-12">
              <h2 className="text-3xl font-bold mb-4">Ready to Transform Your Data?</h2>
              <p className="text-xl mb-8 opacity-90">
                Join thousands of businesses already using ZenalystAI to unlock their data's potential
              </p>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold text-lg shadow-lg hover:shadow-xl transition-all duration-300"
              >
                Get Started Today
              </motion.button>
            </CardContent>
          </Card>
        </motion.div>
        </div>
      </div>
      <FloatingScrollToTop />
    </>
  );
};