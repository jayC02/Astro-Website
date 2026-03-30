// File: src/components/HeroSection.jsx
import { motion } from 'framer-motion';

export default function HeroSection() {
  return (
    <section className="relative flex flex-col items-center justify-center min-h-screen text-center overflow-hidden px-6">
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-slate-700 opacity-90 -z-10" />
      <motion.h1
        initial={{ opacity: 0, y: -50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
        className="text-white text-5xl md:text-7xl font-extrabold tracking-tight drop-shadow-md"
      >
        Design Without Limits
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, duration: 1 }}
        className="text-gray-300 text-lg md:text-2xl max-w-xl mt-6"
      >
        Elevate your architectural workflow with smooth tools and stunning output.
      </motion.p>
      <motion.a
        href="#features"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 0.8, duration: 0.5 }}
        className="mt-8 px-6 py-3 bg-white text-black font-semibold rounded-xl shadow-md hover:scale-105 transition-transform"
      >
        Explore Features
      </motion.a>
    </section>
  );
}
