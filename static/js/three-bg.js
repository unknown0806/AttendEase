/**
 * AttendX — Elegant Academic 3D Background (Three.js)
 * Clean, subtle, low-opacity geometric nodes & constellation particles
 * designed specifically to harmonize with the academic blue palette.
 */

(function () {
    'use strict';

    // Respect reduced motion preference
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const canvas = document.getElementById('three-bg-canvas');
    if (!canvas || typeof THREE === 'undefined') {
        return;
    }

    let scene, camera, renderer;
    let particleSystem, lineSegments;
    let width = window.innerWidth;
    let height = window.innerHeight;
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;
    let animationFrameId = null;
    let isMobile = width < 768;

    const NODE_COUNT = isMobile ? 35 : 70;
    const MAX_DISTANCE = 16;
    const nodePositions = [];
    const nodeVelocities = [];

    function init() {
        // 1. Scene setup
        scene = new THREE.Scene();

        // 2. Camera setup
        camera = new THREE.PerspectiveCamera(55, width / height, 0.1, 1000);
        camera.position.z = 40;

        // 3. Renderer setup
        renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: !isMobile,
            powerPreference: 'high-performance'
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0);

        // 4. Initialize Node Positions and Velocities
        const particleGeo = new THREE.BufferGeometry();
        const posArray = new Float32Array(NODE_COUNT * 3);

        for (let i = 0; i < NODE_COUNT; i++) {
            const x = (Math.random() - 0.5) * 60;
            const y = (Math.random() - 0.5) * 45;
            const z = (Math.random() - 0.5) * 20 - 5;

            posArray[i * 3] = x;
            posArray[i * 3 + 1] = y;
            posArray[i * 3 + 2] = z;

            nodePositions.push(new THREE.Vector3(x, y, z));
            nodeVelocities.push(new THREE.Vector3(
                (Math.random() - 0.5) * 0.03,
                (Math.random() - 0.5) * 0.03,
                (Math.random() - 0.5) * 0.02
            ));
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

        // Subtle Academic Slate / Blue Point Material
        const particleMat = new THREE.PointsMaterial({
            color: 0x3b82f6,
            size: isMobile ? 2.0 : 2.6,
            transparent: true,
            opacity: 0.28,
            sizeAttenuation: true
        });

        particleSystem = new THREE.Points(particleGeo, particleMat);
        scene.add(particleSystem);

        // Connecting Line Segments Geometry
        const lineGeo = new THREE.BufferGeometry();
        const maxLines = (NODE_COUNT * (NODE_COUNT - 1)) / 2;
        const linePositions = new Float32Array(maxLines * 6);
        lineGeo.setAttribute('position', new THREE.BufferAttribute(linePositions, 3).setUsage(THREE.DynamicDrawUsage));

        const lineMat = new THREE.LineBasicMaterial({
            color: 0x94a3b8,
            transparent: true,
            opacity: 0.12,
            blending: THREE.NormalBlending
        });

        lineSegments = new THREE.LineSegments(lineGeo, lineMat);
        scene.add(lineSegments);

        // 5. Event listeners
        window.addEventListener('resize', onWindowResize, { passive: true });
        if (!isMobile) {
            window.addEventListener('mousemove', onMouseMove, { passive: true });
        }

        // 6. Animation loop
        if (prefersReducedMotion) {
            updatePositions();
            renderer.render(scene, camera);
        } else {
            animate();
        }
    }

    function onMouseMove(event) {
        mouseX = (event.clientX - width / 2) * 0.01;
        mouseY = (event.clientY - height / 2) * 0.01;
    }

    function onWindowResize() {
        width = window.innerWidth;
        height = window.innerHeight;
        isMobile = width < 768;

        if (camera && renderer) {
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        }
    }

    function updatePositions() {
        const positions = particleSystem.geometry.attributes.position.array;
        const linePos = lineSegments.geometry.attributes.position.array;
        let lineIdx = 0;

        for (let i = 0; i < NODE_COUNT; i++) {
            const pos = nodePositions[i];
            const vel = nodeVelocities[i];

            pos.add(vel);

            // Bounce gently on boundaries
            if (pos.x < -35 || pos.x > 35) vel.x *= -1;
            if (pos.y < -28 || pos.y > 28) vel.y *= -1;
            if (pos.z < -20 || pos.z > 5) vel.z *= -1;

            positions[i * 3] = pos.x;
            positions[i * 3 + 1] = pos.y;
            positions[i * 3 + 2] = pos.z;

            // Connect nearby nodes
            for (let j = i + 1; j < NODE_COUNT; j++) {
                const posB = nodePositions[j];
                const dist = pos.distanceTo(posB);

                if (dist < MAX_DISTANCE) {
                    linePos[lineIdx++] = pos.x;
                    linePos[lineIdx++] = pos.y;
                    linePos[lineIdx++] = pos.z;
                    linePos[lineIdx++] = posB.x;
                    linePos[lineIdx++] = posB.y;
                    linePos[lineIdx++] = posB.z;
                }
            }
        }

        particleSystem.geometry.attributes.position.needsUpdate = true;
        lineSegments.geometry.setDrawRange(0, lineIdx / 3);
        lineSegments.geometry.attributes.position.needsUpdate = true;
    }

    function animate() {
        animationFrameId = requestAnimationFrame(animate);

        // Smooth camera parallax
        targetX += (mouseX - targetX) * 0.03;
        targetY += (mouseY - targetY) * 0.03;

        camera.position.x = targetX * 1.5;
        camera.position.y = -targetY * 1.5;
        camera.lookAt(scene.position);

        updatePositions();

        renderer.render(scene, camera);
    }

    // Export clean dispose helper
    window.AttendXThree = {
        dispose: function () {
            if (animationFrameId) {
                cancelAnimationFrame(animationFrameId);
            }
            window.removeEventListener('resize', onWindowResize);
            window.removeEventListener('mousemove', onMouseMove);
            if (renderer) {
                renderer.dispose();
            }
        }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
