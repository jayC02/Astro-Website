// File: src/components/Globe.jsx
import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import GLOBE from 'vanta/dist/vanta.globe.min';

export default function Globe() {
  const vantaRef = useRef(null);

  useEffect(() => {
    let effect;
    if (!vantaRef.current) return;

    effect = GLOBE({
      el: vantaRef.current,
      THREE,
      mouseControls: true,
      touchControls: true,
      gyroControls: false,
      minHeight: 200.0,
      minWidth: 200.0,
      scale: 1.0,
      scaleMobile: 1.0,
      size: 0.9,
      color: 0x1d91df,
      color2: 0xffffff,
      backgroundColor: 0x05070c
    });


    return () => {
      if (effect) effect.destroy();
    };
  }, []);

  return (
    <div className="relative w-screen h-screen overflow-hidden">
      <div
        ref={vantaRef}
        className="absolute top-0 left-0 w-full h-full"
        style={{ zIndex: -10, width: '100%', height: '100%' }}
      />

      <div className="relative z-10 flex flex-col items-center justify-center h-full text-center text-white px-6">
        <h1 className="text-5xl md:text-6xl font-extrabold mb-6">Shape the Future</h1>
        <p className="text-lg md:text-2xl max-w-2xl text-white">
          Our architectural software brings your designs to life with real-time visual intelligence.
        </p>
      </div>
    </div>
  );
} 
