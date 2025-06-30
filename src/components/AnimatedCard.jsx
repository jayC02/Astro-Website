import React from 'react';
import { motion } from 'framer-motion';

export default function AnimatedCard({ children }) {
  return (
    <motion.div
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className="bg-white rounded-xl shadow-lg p-6 mx-auto max-w-md"
    >
      {children}
    </motion.div>
  );
}