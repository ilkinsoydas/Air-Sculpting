import React, { useState, useRef, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Bounds } from '@react-three/drei';
import * as THREE from 'three';

const EXPLODE_PARTS = [
  'CPU', 'RAM', 'RAM1', 'RAM2', 'RAM3', 'M2',
  'pCube476_I_O_Cover_0',
  'pCube315_BoardChipsetM_0',
  'pCube305_BoardM2CoverM_0',
  'pCube304_BoardM2Cover1M_0'
];
const EXPLODE_DISTANCE = 3.0;

function Motherboard({ explodeFactor, targetRotation, handPosition }) {
  const { scene } = useGLTF('/scene_converted.gltf');
  const group = useRef();
  const outerGroup = useRef();

  const originalPositions = useRef({});

  useEffect(() => {
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
        part.position.z = THREE.MathUtils.lerp(part.position.z, targetZ, delta * 2);
      }
    });

    if (outerGroup.current) {
      outerGroup.current.position.x = THREE.MathUtils.lerp(outerGroup.current.position.x, handPosition.x, delta * 2);
      outerGroup.current.position.y = THREE.MathUtils.lerp(outerGroup.current.position.y, handPosition.y, delta * 2);

      outerGroup.current.rotation.x = THREE.MathUtils.lerp(outerGroup.current.rotation.x, targetRotation.x, delta * 5);
      outerGroup.current.rotation.y = THREE.MathUtils.lerp(outerGroup.current.rotation.y, targetRotation.y, delta * 5);
    }
  });

  return (
    <group ref={outerGroup}>
      <group ref={group} dispose={null} rotation={[Math.PI / 2, 0, 0]}>
        <primitive object={scene} />
      </group>
    </group>
  );
}

function App() {
  const [explodeFactor, setExplodeFactor] = useState(0);
  const [targetRotation, setTargetRotation] = useState({ x: 0, y: 0 });
  const [handPosition, setHandPosition] = useState({ x: 0, y: 0 });
  const lastHandPos = useRef({ x: null, y: null });

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
      console.log("Connected to AI");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.gesture === "Extrude") {
        setExplodeFactor(data.pinch_distance);
      }
      else if (data.gesture === "Rotate") {
        if (lastHandPos.current.x === null) {

          lastHandPos.current = { x: data.x, y: data.y };
        } else {

          //EMA: yumuşatma filtresi
          const smoothedX = (data.x * 0.2) + (lastHandPos.current.x * 0.8);
          const smoothedY = (data.y * 0.2) + (lastHandPos.current.y * 0.8);

          const deltaX = smoothedX - lastHandPos.current.x;
          const deltaY = smoothedY - lastHandPos.current.y;

          setTargetRotation(prev => ({
            x: prev.x + (deltaY * 5),
            y: prev.y + (deltaX * 5)
          }));

          lastHandPos.current = { x: smoothedX, y: smoothedY };
        }
      }
      else if (data.gesture === "Fist") {
        lastHandPos.current = { x: null, y: null };

        const clamp = (val, min, max) => Math.min(Math.max(val, min), max);
        setHandPosition({
          x: clamp((data.x - 0.5) * 0.8, -0.08, 0.08),
          y: clamp(-(data.y - 0.5) * 0.8, -0.08, 0.08)
        });
      }
      else if (data.gesture === "Pinch") {
        setExplodeFactor(0);
        setHandPosition({ x: 0, y: 0 });
        setTargetRotation({ x: 0, y: 0 });
        lastHandPos.current = { x: null, y: null };
      }
      else if (data.gesture === "Idle") {
        setExplodeFactor(0);
        lastHandPos.current = { x: null, y: null };
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

        <Suspense fallback={null}>
          <Bounds fit clip observe margin={1.2}>
            <Motherboard explodeFactor={explodeFactor} targetRotation={targetRotation} handPosition={handPosition} />
          </Bounds>
          <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default App;
