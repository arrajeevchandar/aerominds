"use client";

import React, { useRef, useMemo } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";

function Scene({ imageUrl, depthUrl }) {
  const meshRef = useRef();

  // Load textures
  const [texture, depthMap] = useLoader(THREE.TextureLoader, [imageUrl, depthUrl]);

  // Fix: Prevent textures from being flipped upside down
  React.useEffect(() => {
    if (texture) {
      texture.flipY = false;
      texture.needsUpdate = true;
    }
    if (depthMap) {
      depthMap.flipY = false;
      depthMap.needsUpdate = true;
    }
  }, [texture, depthMap]);

  const geometry = useMemo(() => {
    // High resolution mesh for smooth displacement
    const geo = new THREE.PlaneGeometry(10, 10, 512, 512);
    
    // Compute vertex normals for proper lighting
    geo.computeVertexNormals();
    
    return geo;
  }, []);

  const material = useMemo(() => {
    return new THREE.MeshStandardMaterial({
      map: texture,
      displacementMap: depthMap,
      displacementScale: 2.5,  // Adjusted for better depth effect
      displacementBias: -0.5,  // Center the displacement
      side: THREE.DoubleSide,
      roughness: 0.8,  // More matte for terrain-like appearance
      metalness: 0.1,
      flatShading: false,  // Smooth shading for better appearance
    });
  }, [texture, depthMap]);

  // Rotate animation can be added here if needed
  React.useEffect(() => {
    if (meshRef.current) {
      // Ensure normals are updated after displacement
      meshRef.current.geometry.computeVertexNormals();
    }
  }, [depthMap]);

  return (
    <mesh ref={meshRef} geometry={geometry} material={material} rotation={[-Math.PI / 2, Math.PI, 0]} />
  );
}

export default function Viewer3D({ imageUrl, depthUrl }) {
  if (!imageUrl || !depthUrl) return null;

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative' }} className="bg-gray-900 rounded-lg overflow-hidden">
      <Canvas shadows style={{ width: '100%', height: '100%' }}>
        <PerspectiveCamera makeDefault position={[0, 12, 12]} fov={50} />
        <OrbitControls 
          enableDamping={true}
          dampingFactor={0.05}
          minDistance={5}
          maxDistance={30}
        />

        {/* Enhanced Lighting Setup */}
        <ambientLight intensity={0.4} />
        
        {/* Hemisphere light for natural outdoor feel */}
        <hemisphereLight 
          skyColor="#ffffff" 
          groundColor="#444444" 
          intensity={0.6} 
        />
        
        {/* Main directional light from above-front */}
        <directionalLight 
          position={[5, 15, 5]} 
          intensity={1.2}
          castShadow
        />
        
        {/* Fill light from the side */}
        <directionalLight 
          position={[-5, 10, -5]} 
          intensity={0.3}
        />

        <Scene imageUrl={imageUrl} depthUrl={depthUrl} />
      </Canvas>
    </div>
  );
}
