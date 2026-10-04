import React, { useState, useRef, useEffect, Suspense, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Bounds } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const EXPLODE_PARTS = [
  'CPU', 'RAM', 'RAM1', 'RAM2', 'RAM3', 'M2',
  'pCube476_I_O_Cover_0',
  'pCube315_BoardChipsetM_0',
  'pCube305_BoardM2CoverM_0',
  'pCube304_BoardM2Cover1M_0'
];
const EXPLODE_DISTANCE = 3.0;

function Motherboard({ explodeFactor }) {
  const { scene } = useGLTF('/scene_converted.gltf');
  const group = useRef();

  // Parçaların orijinal pozisyonlarını saklamak için
  const originalPositions = useRef({});

  useEffect(() => {

    console.log("=== MODELDEKI TUM PARCALAR ===");
    scene.traverse((child) => {
      if (child.isMesh || child.isGroup) {
        console.log("Parça adı:", child.name);
      }
    });
    console.log("=============================");

    //orijinal pozisyonları kaydet
    EXPLODE_PARTS.forEach((partName) => {
      const part = scene.getObjectByName(partName);
      if (part && !originalPositions.current[partName]) {
        originalPositions.current[partName] = part.position.clone();
      }
    });
  }, [scene]);

  useFrame((state, delta) => {

    EXPLODE_PARTS.forEach((partName) => {
      const part = scene.getObjectByName(partName);
      if (part && originalPositions.current[partName]) {

        const targetZ = originalPositions.current[partName].z + (EXPLODE_DISTANCE * explodeFactor * 2);

        part.position.z = THREE.MathUtils.lerp(part.position.z, targetZ, delta * 5);
      }
    });
  });

  return (
    <group ref={group} dispose={null} rotation={[Math.PI / 2, 0, 0]}>
      <primitive object={scene} />
    </group>
  );
}

function App() {
  const [explodeFactor, setExplodeFactor] = useState(0);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");


    ws.onopen = () => {
      console.log("Connected to AI")
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      console.log("Received gesture:", data.gesture, " | Distance: ", data.pinch_distance);

      if (data.gesture === "Extrude") {
        setExplodeFactor(data.pinch_distance);
      }
      else if (data.gesture === "Idle" || data.gesture === "Rotate" || data.gesture === "Pinch") {
        setExplodeFactor(0)
      }
    };
    return () => ws.close();
  }, []);

  return (
    <div style={{ width: '100vw', height: '100vh', position: 'relative' }}>
      {/* UI Overlay */}
      <div style={{
        position: 'absolute', top: 20, left: 20, zIndex: 10,
        background: 'rgba(0,0,0,0.7)', padding: '20px', borderRadius: '10px'
      }}>
        <h2>Air Sculpting</h2>
        <p>Press <b>Space</b> to Explode/Collapse.</p>
        <p>Status: {explodeFactor > 0.2 ? "Exploding..." : "Assembled"}</p>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
        <color attach="background" args={['#1a1a1a']} />
        <ambientLight intensity={2.0} />
        <directionalLight position={[10, 10, 10]} intensity={2.5} />

        {/* We'll load the model here */}
        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.2}>
            <Motherboard explodeFactor={explodeFactor} />
          </Bounds>
          <Environment preset="city" />
        </Suspense>

        <OrbitControls makeDefault />
      </Canvas>
    </div>
  );
}

export default App;
