(() => {
    const canvas = document.createElement('canvas');
    canvas.className = 'particle-wallpaper';
    canvas.setAttribute('aria-hidden', 'true');
    document.body.insertBefore(canvas, document.body.firstChild);

    const context = canvas.getContext('2d', { alpha: true });
    if (!context) return;

    let width = 0;
    let height = 0;
    let dots = [];
    let lastFrame = 0;

    function resize() {
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = Math.round(width * ratio);
        canvas.height = Math.round(height * ratio);
        context.setTransform(ratio, 0, 0, ratio, 0, 0);

        const count = Math.round(Math.max(22, Math.min(56, width / 24)));
        dots = Array.from({ length: count }, () => {
            const large = Math.random() < 0.2;
            return {
                x: width * (0.52 + Math.random() * 0.46),
                y: height * (0.1 + Math.random() * 0.82),
                radius: large ? 3.5 + Math.random() * 5 : 0.8 + Math.random() * 1.8,
                opacity: 0.5 + Math.random() * 0.45,
                vx: (Math.random() - 0.5) * (large ? 0.36 : 0.24),
                vy: (Math.random() - 0.5) * (large ? 0.3 : 0.18),
                phase: Math.random() * Math.PI * 2,
            };
        });
    }

    function draw(time) {
        const step = lastFrame ? Math.min((time - lastFrame) / 16.67, 2) : 1;
        lastFrame = time;
        context.clearRect(0, 0, width, height);
        for (const dot of dots) {
            dot.x += dot.vx * step;
            dot.y += dot.vy * step;
            dot.phase += 0.018 * step;
            if (dot.x < width * 0.5 || dot.x > width * 0.99) dot.vx *= -1;
            if (dot.y < height * 0.08 || dot.y > height * 0.94) dot.vy *= -1;
            const pulse = 0.84 + (Math.sin(dot.phase) + 1) * 0.08;
            context.beginPath();
            context.arc(dot.x, dot.y, dot.radius * pulse, 0, Math.PI * 2);
            context.fillStyle = `rgba(31, 30, 29, ${dot.opacity})`;
            context.fill();
        }
        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize, { passive: true });
    resize();
    requestAnimationFrame(draw);
})();
