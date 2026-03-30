// File: src/components/ModelViewer.jsx
import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF } from '@react-three/drei';

function HouseModel() {
  const { scene } = useGLTF('/models/house.glb'); // Place your .glb in public/models
  return <primitive object={scene} scale={1.5} />;
}

export default function ModelViewer() {
  return (
    <div className="w-full h-screen">
      <Canvas camera={{ position: [3, 2, 5], fov: 50 }} shadows>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} castShadow />
        <Suspense fallback={null}>
          <HouseModel />
          <Environment preset="sunset" background={false} />
        </Suspense>
        <OrbitControls enablePan enableZoom enableRotate />
      </Canvas>
    </div>
  );
}

// And place a file named 'house.glb' inside /public/models/
