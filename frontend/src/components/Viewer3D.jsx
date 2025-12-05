"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";

function Scene({ imageUrl, depthUrl }) {
  const meshRef = useRef();

  // Load textures
  const [texture, depthMap] = useLoader(THREE.TextureLoader, [imageUrl, depthUrl]);

  const geometry = useMemo(() => {
    // Keep the high resolution mesh (1 Million vertices) for detail
    return new THREE.PlaneGeometry(10, 10, 1024, 1024);
  }, []);

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      map: texture,
      displacementMap: depthMap,
      displacementScale: 3,
      side: THREE.DoubleSide,
      // Revert to standard material properties
      roughness: 0.5,
      metalness: 0.0,
    });
  }, [texture, depthMap]);

  return (
    <mesh ref={meshRef} geometry={geometry} material={material} rotation={[-Math.PI / 2, 0, 0]} />
  );
}

export default function Viewer3D({ imageUrl, depthUrl }) {
  if (!imageUrl || !depthUrl) return null;

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }} className="bg-gray-900 rounded-lg overflow-hidden">
      <Canvas shadows style={{ width: '100%', height: '100%' }}>
        <PerspectiveCamera makeDefault position={[0, 10, 10]} />
        <OrbitControls />

        {/* Standard, Stable Lighting */}
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />

        <Scene imageUrl={imageUrl} depthUrl={depthUrl} />
      </Canvas>
    </div>
  );
}
