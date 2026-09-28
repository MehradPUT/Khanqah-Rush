export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  size: number;
  life: number;
  maxLife: number;
  gravity: number;
}

export class ParticleSystem {
  private particles: Particle[] = [];
  private shakeAmount: number = 0;
  private shakeDecay: number = 0.9;

  public addSplinters(x: number, y: number, direction: 'LEFT' | 'RIGHT', isYoung: boolean) {
    const dirMult = direction === 'LEFT' ? 1 : -1;
    const count = isYoung ? 24 : 14;

    for (let i = 0; i < count; i++) {
      const angle = (Math.PI / 4) + (Math.random() * Math.PI / 2);
      const speed = (isYoung ? 8 : 5) + Math.random() * 8;
      const vx = dirMult * Math.cos(angle) * speed;
      const vy = -Math.sin(angle) * speed;

      let color = '#8d5524';
      if (isYoung) {
        // Fire embers in young phase
        const colors = ['#f39c12', '#e74c3c', '#ffdd59', '#e67e22'];
        color = colors[Math.floor(Math.random() * colors.length)];
      } else {
        const colors = ['#5c3e26', '#8d5524', '#f5b041', '#3e2a1a'];
        color = colors[Math.floor(Math.random() * colors.length)];
      }

      this.particles.push({
        x: x + (Math.random() * 20 - 10),
        y: y + (Math.random() * 20 - 10),
        vx,
        vy,
        color,
        size: 2 + Math.random() * (isYoung ? 5 : 3.5),
        life: 1.0,
        maxLife: 0.35 + Math.random() * 0.3,
        gravity: 18
      });
    }
  }

  public addRejuvenationBurst(x: number, y: number) {
    const count = 45;
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 4 + Math.random() * 10;
      const colors = ['#e74c3c', '#f1c40f', '#1abc9c', '#ffffff', '#3498db'];

      this.particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 3 + Math.random() * 4,
        life: 1.0,
        maxLife: 0.6 + Math.random() * 0.4,
        gravity: 4
      });
    }
  }

  public triggerShake(intensity: number = 8) {
    this.shakeAmount = intensity;
  }

  public update(dt: number) {
    // Update shake
    this.shakeAmount *= Math.pow(this.shakeDecay, dt * 60);
    if (this.shakeAmount < 0.1) this.shakeAmount = 0;

    // Update particles
    for (let i = this.particles.length - 1; i >= 0; i--) {
      const p = this.particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += p.gravity * dt;
      p.life -= dt / p.maxLife;

      if (p.life <= 0) {
        this.particles.splice(i, 1);
      }
    }
  }

  public applyShake(ctx: CanvasRenderingContext2D) {
    if (this.shakeAmount > 0) {
      const dx = (Math.random() * 2 - 1) * this.shakeAmount;
      const dy = (Math.random() * 2 - 1) * this.shakeAmount;
      ctx.translate(dx, dy);
    }
  }

  public draw(ctx: CanvasRenderingContext2D) {
    ctx.save();
    for (const p of this.particles) {
      ctx.globalAlpha = Math.max(0, p.life);
      ctx.fillStyle = p.color;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.restore();
  }
}
