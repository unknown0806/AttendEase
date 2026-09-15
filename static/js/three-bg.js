/**
 * AttendX — Interactive 3D Background Engine (Three.js)
 * High-performance, lightweight, non-intrusive floating geometric meshes & particles.
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
    let particleSystem, meshGroup;
    let width = window.innerWidth;
    let height = window.innerHeight;
    let mouseX = 0, mouseY = 0;
    let targetX = 0, targetY = 0;
    let animationFrameId = null;
    let isMobile = width < 768;

    function init() {
        // 1. Scene setup
        scene = new THREE.Scene();

        // 2. Camera setup
        camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 1000);
        camera.position.z = 45;

        // 3. Renderer setup with alpha transparency
        renderer = new THREE.WebGLRenderer({
            canvas: canvas,
            alpha: true,
            antialias: !isMobile,
            powerPreference: 'high-performance'
        });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, isMobile ? 1.5 : 2));
        renderer.setSize(width, height);
        renderer.setClearColor(0x000000, 0); // Completely transparent

        // 4. Lights
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambientLight);

        const pointLight1 = new THREE.PointLight(0x38bdf8, 1.2, 100);
        pointLight1.position.set(20, 20, 20);
        scene.add(pointLight1);

        const pointLight2 = new THREE.PointLight(0x184e96, 1.5, 100);
        pointLight2.position.set(-20, -20, 15);
        scene.add(pointLight2);

        // 5. Create Subtle Floating Geometric Shapes
        meshGroup = new THREE.Group();
        const geometries = [
            new THREE.IcosahedronGeometry(1.6, 0),
            new THREE.OctahedronGeometry(1.4, 0),
            new THREE.TetrahedronGeometry(1.8, 0),
            new THREE.DodecahedronGeometry(1.5, 0),
            new THREE.TorusGeometry(1.2, 0.35, 8, 16)
        ];

        const meshMaterials = [
            new THREE.MeshStandardMaterial({
                color: 0x184e96,
                roughness: 0.3,
                metalness: 0.2,
                transparent: true,
                opacity: 0.22,
                wireframe: false
            }),
            new THREE.MeshStandardMaterial({
                color: 0x0284c7,
                roughness: 0.2,
                metalness: 0.3,
                transparent: true,
                opacity: 0.18,
                wireframe: true
            }),
            new THREE.MeshStandardMaterial({
                color: 0x38bdf8,
                roughness: 0.4,
                metalness: 0.1,
                transparent: true,
                opacity: 0.16,
                wireframe: false
            })
        ];

        const numMeshes = isMobile ? 8 : 18;
        for (let i = 0; i < numMeshes; i++) {
            const geom = geometries[i % geometries.length];
            const mat = meshMaterials[i % meshMaterials.length];
            const mesh = new THREE.Mesh(geom, mat);

            // Spread out in 3D space
            mesh.position.x = (Math.random() - 0.5) * 70;
            mesh.position.y = (Math.random() - 0.5) * 50;
            mesh.position.z = (Math.random() - 0.5) * 30 - 5;

            // Random initial rotation & scale
            mesh.rotation.x = Math.random() * Math.PI;
            mesh.rotation.y = Math.random() * Math.PI;
            const scale = 0.6 + Math.random() * 0.7;
            mesh.scale.set(scale, scale, scale);

            // Custom speeds for floating motion
            mesh.userData = {
                rotSpeedX: (Math.random() - 0.5) * 0.006,
                rotSpeedY: (Math.random() - 0.5) * 0.008,
                floatSpeed: 0.001 + Math.random() * 0.0015,
                floatOffset: Math.random() * Math.PI * 2,
                initialY: mesh.position.y
            };

            meshGroup.add(mesh);
        }
        scene.add(meshGroup);

        // 6. Create Subtle Ambient Star/Node Particles
        const particleCount = isMobile ? 60 : 160;
        const particleGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);

        const colorPalette = [
            new THREE.Color(0x38bdf8), // Sky Blue
            new THREE.Color(0x184e96), // Academic Deep Blue
            new THREE.Color(0x818cf8), // Soft Indigo
            new THREE.Color(0x06b6d4)  // Soft Cyan
        ];

        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            positions[i3] = (Math.random() - 0.5) * 90;
            positions[i3 + 1] = (Math.random() - 0.5) * 70;
            positions[i3 + 2] = (Math.random() - 0.5) * 40 - 10;

            const c = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors[i3] = c.r;
            colors[i3 + 1] = c.g;
            colors[i3 + 2] = c.b;
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const particleMat = new THREE.PointsMaterial({
            size: isMobile ? 1.8 : 2.4,
            vertexColors: true,
            transparent: true,
            opacity: 0.35,
            sizeAttenuation: true
        });

        particleSystem = new THREE.Points(particleGeo, particleMat);
        scene.add(particleSystem);

        // 7. Event listeners
        window.addEventListener('resize', onWindowResize, { passive: true });
        if (!isMobile) {
            window.addEventListener('mousemove', onMouseMove, { passive: true });
        }

        // 8. Start loop or single render
        if (prefersReducedMotion) {
            renderer.render(scene, camera);
        } else {
            animate();
        }
    }

    function onMouseMove(event) {
        mouseX = (event.clientX - width / 2) * 0.015;
        mouseY = (event.clientY - height / 2) * 0.015;
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

    function animate(timestamp) {
        animationFrameId = requestAnimationFrame(animate);

        const time = (timestamp || 0) * 0.001;

        // Smooth mouse parallax lerp
        targetX += (mouseX - targetX) * 0.04;
        targetY += (mouseY - targetY) * 0.04;

        if (meshGroup) {
            meshGroup.position.x = targetX * 1.5;
            meshGroup.position.y = -targetY * 1.5;

            meshGroup.children.forEach((mesh) => {
                mesh.rotation.x += mesh.userData.rotSpeedX;
                mesh.rotation.y += mesh.userData.rotSpeedY;
                mesh.position.y = mesh.userData.initialY + Math.sin(time * 0.8 + mesh.userData.floatOffset) * 1.2;
            });
        }

        if (particleSystem) {
            particleSystem.rotation.y = time * 0.02;
            particleSystem.rotation.x = Math.sin(time * 0.01) * 0.05;
            particleSystem.position.x = targetX * 0.6;
            particleSystem.position.y = -targetY * 0.6;
        }

        renderer.render(scene, camera);
    }

    // Cleanup helper
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

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
