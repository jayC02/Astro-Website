// File: src/components/FloorPlan.jsx
import { useState, useEffect } from 'react';
import { motion, AnimatePresence, useAnimation } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export default function FloorPlan() {
  const [hoveredRoom, setHoveredRoom] = useState(null);
  const [selectedRoom, setSelectedRoom] = useState(null);
  const controls = useAnimation();
  const [ref, inView] = useInView({ triggerOnce: true, threshold: 0.2 });

  const rooms = [
    { name: 'Living Room', path: 'M40 40 H100 V70 H40 Z', labelX: 70, labelY: 55 },
    { name: 'Kitchen', path: 'M110 40 H170 V70 H110 Z', labelX: 140, labelY: 55 },
    { name: 'Bedroom', path: 'M40 80 H90 V110 H40 Z', labelX: 65, labelY: 95 },
    { name: 'Bathroom', path: 'M100 80 H150 V110 H100 Z', labelX: 125, labelY: 95 },
    { name: 'Office', path: 'M160 80 H210 V110 H160 Z', labelX: 185, labelY: 95 },
  ];

  useEffect(() => {
    if (inView) {
      controls.start(i => ({
        opacity: 1,
        y: 0,
        transition: { delay: i * 0.45, duration: 1.5 }
      }));
    }
  }, [controls, inView]);

  return (
    <div ref={ref} className="relative flex justify-center items-center p-6 bg-neutral-900 min-h-screen">
      <AnimatePresence>
        {selectedRoom && (
          <motion.div
            className="absolute top-4 left-4 bg-white text-black shadow-lg rounded p-4 border z-10"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
          >
            <h2 className="text-xl font-semibold mb-2">{selectedRoom}</h2>
            <p>Info about the {selectedRoom.toLowerCase()} goes here. Add images or more text if needed.</p>
            <button onClick={() => setSelectedRoom(null)} className="mt-2 text-sm text-blue-500 underline">Close</button>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 w-full max-w-6xl">
        {rooms.map((room, idx) => (
          <motion.div
            key={idx}
            className="relative rounded overflow-hidden cursor-pointer bg-neutral-800 hover:shadow-xl border border-neutral-700"
            custom={idx}
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? controls : {}}
            onMouseEnter={() => setHoveredRoom(room.name)}
            onMouseLeave={() => setHoveredRoom(null)}
            onClick={() => setSelectedRoom(room.name)}
          >
            <div className="p-6 text-white">
              <h3 className="text-lg font-bold mb-2">{room.name}</h3>
              <p className="text-sm text-neutral-400">Click to explore details</p>
            </div>
            {hoveredRoom === room.name && (
              <motion.div
                className="absolute inset-0 bg-white/5 backdrop-blur-sm"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
              />
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
