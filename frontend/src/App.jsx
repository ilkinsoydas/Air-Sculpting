import React, { useState, useRef, useEffect, Suspense } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Environment, useGLTF, Bounds, Center } from '@react-three/drei';
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

        const targetX = originalPositions.current[partName].x + (handPosition.x * explodeFactor * 10);
        const targetY = originalPositions.current[partName].y + (handPosition.y * explodeFactor * 10);
        part.position.x = THREE.MathUtils.lerp(part.position.x, targetX, delta * 2);
        part.position.y = THREE.MathUtils.lerp(part.position.y, targetY, delta * 2);
      }
    });

    if (outerGroup.current) {
      outerGroup.current.rotation.x = THREE.MathUtils.lerp(outerGroup.current.rotation.x, targetRotation.x, delta * 5);
      outerGroup.current.rotation.y = THREE.MathUtils.lerp(outerGroup.current.rotation.y, targetRotation.y, delta * 5);
    }
  });

  return (
    <group ref={outerGroup} scale={5}>
      <group ref={group} dispose={null} rotation={[Math.PI / 2, 0, 0]}>
        <Center>
          <primitive object={scene} />
        </Center>
      </group>
    </group>
  );
}

function App() {
  const [explodeFactor, setExplodeFactor] = useState(0);
  const [targetRotation, setTargetRotation] = useState({ x: 0, y: 0 });
  const [handPosition, setHandPosition] = useState({ x: 0, y: 0 });
  const lastHandPos = useRef({ x: null, y: null });
  const [activeGesture, setActiveGesture] = useState("Idle");

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws");

    ws.onopen = () => {
      console.log("Connected to AI");
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.gesture) {
        setActiveGesture(data.gesture);
      }

      if (data.gesture === "Extrude") {
        setExplodeFactor(data.pinch_distance);
        lastHandPos.current = { x: null, y: null };
      }
      if (data.gesture === "Rotate") {
        if (lastHandPos.current.x === null) {

          lastHandPos.current = { x: data.x, y: data.y };
        } else {

          //EMA: yumuşatma filtresi
          const smoothedX = (data.x * 0.2) + (lastHandPos.current.x * 0.8);
          const smoothedY = (data.y * 0.2) + (lastHandPos.current.y * 0.8);

          const deltaX = smoothedX - lastHandPos.current.x;
          const deltaY = smoothedY - lastHandPos.current.y;

          setTargetRotation(prev => ({
            x: prev.x + (deltaY * 10),
            y: prev.y + (deltaX * 10)
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
        position: 'absolute', top: 30, left: 30, zIndex: 10,
        background: 'rgba(10, 15, 30, 0.85)', padding: '25px', borderRadius: '15px',
        border: '1px solid rgba(0, 255, 255, 0.2)',
        boxShadow: '0 0 20px rgba(0, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        color: '#fff', fontFamily: 'monospace'
      }}>
        <h2 style={{ margin: '0 0 15px 0', letterSpacing: '2px', color: '#00ffff' }}>AIR SCULPTING</h2>

        <div style={{ display: 'flex', alignItems: 'center', gap: '15px', marginTop: '20px' }}>
          <span style={{ fontSize: '12px', opacity: 0.6, letterSpacing: '1px' }}>SYS.STATE:</span>
          <div style={{
            padding: '8px 16px', borderRadius: '20px', fontSize: '14px',
            background: activeGesture !== 'Idle' ? 'rgba(0, 255, 255, 0.15)' : 'rgba(255, 255, 255, 0.05)',
            color: activeGesture !== 'Idle' ? '#00ffff' : '#888',
            border: `1px solid ${activeGesture !== 'Idle' ? '#00ffff' : '#444'}`,
            boxShadow: activeGesture !== 'Idle' ? '0 0 15px rgba(0, 255, 255, 0.4)' : 'none',
            transition: 'all 0.3s ease', fontWeight: 'bold', letterSpacing: '2px', textTransform: 'uppercase'
          }}>
            {activeGesture}
          </div>
        </div>
        <div style={{ marginTop: '20px', fontSize: '12px', color: '#888' }}>
          CORE TEMP: {explodeFactor > 0.05 ? (explodeFactor * 100).toFixed(0) + '°C' : 'STABLE'}
        </div>
      </div>

      {/* 3D Canvas */}
      <Canvas camera={{ position: [0, 1, 4], fov: 50 }}>
        <color attach="background" args={['#1a1a1a']} />
        <ambientLight intensity={2.0} />
        <directionalLight position={[10, 10, 10]} intensity={2.5} />

        <Suspense fallback={null}>
          <Center scale={6}>
            <Motherboard explodeFactor={explodeFactor} targetRotation={targetRotation} handPosition={handPosition} />
          </Center>
          <Environment preset="city" />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default App;
