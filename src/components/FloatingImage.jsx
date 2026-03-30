import { motion } from 'framer-motion';

export default function FloatingImage({ src, alt, className }) {
  return (
    <motion.img
      src={src}
      alt={alt}
      className={`w-full max-w-md ${className}`}
      animate={{ y: [0, -10, 0] }}
      transition={{
        duration: 6,
        repeat: Infinity,
        ease: 'easeInOut'
      }}
    />
  );
}
