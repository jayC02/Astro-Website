import React from 'react';
import { motion } from 'framer-motion';

export default function AnimatedHero() {
  return (
    <section className="flex flex-col items-center justify-center min-h-screen text-center px-4">
      <motion.h1
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-4xl md:text-6xl font-bold mb-6"
      >
        Welcome to my Astro Site
      </motion.h1>
      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.8 }}
        className="text-lg md:text-2xl text-gray-700"
      >
        This page uses React and Framer Motion for animations.
      </motion.p>
    </section>
  );
}