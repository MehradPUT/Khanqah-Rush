export type BranchSide = 'NONE' | 'LEFT' | 'RIGHT';

export interface FlyingBlock {
  x: number;
  y: number;
  vx: number;
  vy: number;
  rotation: number;
  vRot: number;
  side: 'LEFT' | 'RIGHT';
  branch: BranchSide;
  life: number;
}

export class Pillar {
  public segments: BranchSide[] = [];
  public readonly visibleSegments: number = 8;
  public readonly segmentHeight: number = 100;
  public flyingBlocks: FlyingBlock[] = [];
  private lastSide: BranchSide = 'NONE';

  constructor() {
    this.reset();
  }

  public reset() {
    this.segments = [];
    this.flyingBlocks = [];
    this.lastSide = 'NONE';

    // The first 3 segments are always safe (NONE)
    for (let i = 0; i < 3; i++) {
      this.segments.push('NONE');
    }

    // Fill the rest of the initial trunk
    for (let i = 3; i < this.visibleSegments + 2; i++) {
      this.addSegment();
    }
  }

  /**
   * Generates a new segment at the top with natural branch distribution
   */
  public addSegment() {
    let side: BranchSide = 'NONE';

    // 55% chance of spawning a branch
    if (Math.random() < 0.55) {
      if (this.lastSide === 'NONE') {
        side = Math.random() < 0.5 ? 'LEFT' : 'RIGHT';
      } else if (this.lastSide === 'LEFT') {
        // Can repeat same side (35%) or go NONE (65%), avoids immediate trap switch
        side = Math.random() < 0.35 ? 'LEFT' : 'NONE';
      } else if (this.lastSide === 'RIGHT') {
        side = Math.random() < 0.35 ? 'RIGHT' : 'NONE';
      }
    }

    this.segments.push(side);
    this.lastSide = side;
  }

  /**
   * Player chops the bottom-most segment
   * Returns the chopped branch side
   */
  public chop(playerSide: 'LEFT' | 'RIGHT', trunkCenterX: number, trunkBaseY: number): BranchSide {
    if (this.segments.length === 0) return 'NONE';

    const choppedBranch = this.segments.shift() || 'NONE';

    // Add flying block effect in the direction of the chop force
    const flyDirection = playerSide === 'LEFT' ? 1 : -1;
    this.flyingBlocks.push({
      x: trunkCenterX,
      y: trunkBaseY,
      vx: flyDirection * (12 + Math.random() * 8),
      vy: -(8 + Math.random() * 6),
      rotation: 0,
      vRot: flyDirection * (0.15 + Math.random() * 0.2),
      side: playerSide,
      branch: choppedBranch,
      life: 1.0
    });

    // Replenish trunk at top
    this.addSegment();

    return choppedBranch;
  }

  public update(dt: number) {
    // Update flying wood blocks
    for (let i = this.flyingBlocks.length - 1; i >= 0; i--) {
      const b = this.flyingBlocks[i];
      b.x += b.vx;
      b.y += b.vy;
      b.vy += 22 * dt; // Gravity
      b.rotation += b.vRot;
      b.life -= dt * 1.5;

      if (b.life <= 0 || b.y > 1000) {
        this.flyingBlocks.splice(i, 1);
      }
    }
  }

  public draw(
    ctx: CanvasRenderingContext2D,
    trunkX: number,
    baseY: number,
    trunkWidth: number,
    isYoungPhase: boolean
  ) {
    // Draw remaining segments from bottom up
    for (let i = 0; i < this.visibleSegments; i++) {
      const segY = baseY - (i + 1) * this.segmentHeight;
      const branch = this.segments[i] || 'NONE';

      this.drawTrunkSegment(ctx, trunkX, segY, trunkWidth, this.segmentHeight, isYoungPhase);

      if (branch === 'LEFT') {
        this.drawBranch(ctx, trunkX, segY, trunkWidth, 'LEFT', isYoungPhase);
      } else if (branch === 'RIGHT') {
        this.drawBranch(ctx, trunkX, segY, trunkWidth, 'RIGHT', isYoungPhase);
      }
    }

    // Draw flying blocks
    for (const b of this.flyingBlocks) {
      ctx.save();
      ctx.translate(b.x, b.y);
      ctx.rotate(b.rotation);
      ctx.globalAlpha = Math.max(0, b.life);

      this.drawTrunkSegment(ctx, -trunkWidth / 2, -this.segmentHeight / 2, trunkWidth, this.segmentHeight, false);
      if (b.branch !== 'NONE') {
        this.drawBranch(ctx, -trunkWidth / 2, -this.segmentHeight / 2, trunkWidth, b.branch, false);
      }

      ctx.restore();
    }
  }

  private drawTrunkSegment(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    isYoungPhase: boolean
  ) {
    // Ancient Cypress Trunk styling (carved, rich wood grain with Persian talisman inlays)
    const grad = ctx.createLinearGradient(x, 0, x + width, 0);
    if (isYoungPhase) {
      // Rejuvenated glowing amber wood
      grad.addColorStop(0, '#3d1d11');
      grad.addColorStop(0.2, '#6e3922');
      grad.addColorStop(0.5, '#b86036');
      grad.addColorStop(0.8, '#6e3922');
      grad.addColorStop(1, '#3d1d11');
    } else {
      // Deep sacred dark cypress wood
      grad.addColorStop(0, '#1c130c');
      grad.addColorStop(0.2, '#3e2a1a');
      grad.addColorStop(0.5, '#5c3e26');
      grad.addColorStop(0.8, '#3e2a1a');
      grad.addColorStop(1, '#1c130c');
    }

    ctx.fillStyle = grad;
    ctx.fillRect(x, y, width, height);

    // Decorative Islamic/Persian carved geometric groove
    ctx.strokeStyle = isYoungPhase ? 'rgba(243, 156, 18, 0.4)' : 'rgba(245, 176, 65, 0.2)';
    ctx.lineWidth = 2;
    ctx.strokeRect(x + 6, y + 4, width - 12, height - 8);

    // Wood rings / bark notch lines
    ctx.beginPath();
    ctx.strokeStyle = 'rgba(0, 0, 0, 0.4)';
    ctx.lineWidth = 3;
    ctx.moveTo(x + 12, y + height * 0.4);
    ctx.lineTo(x + width - 12, y + height * 0.4);
    ctx.moveTo(x + 18, y + height * 0.75);
    ctx.lineTo(x + width - 18, y + height * 0.75);
    ctx.stroke();

    // Central mystical diamond talisman
    ctx.fillStyle = isYoungPhase ? '#e74c3c' : '#1abc9c';
    ctx.beginPath();
    const cx = x + width / 2;
    const cy = y + height / 2;
    ctx.moveTo(cx, cy - 8);
    ctx.lineTo(cx + 8, cy);
    ctx.lineTo(cx, cy + 8);
    ctx.lineTo(cx - 8, cy);
    ctx.closePath();
    ctx.fill();
  }

  private drawBranch(
    ctx: CanvasRenderingContext2D,
    trunkX: number,
    trunkY: number,
    trunkWidth: number,
    side: 'LEFT' | 'RIGHT',
    isYoungPhase: boolean
  ) {
    const branchLength = 115;
    const branchThickness = 34;
    const branchY = trunkY + this.segmentHeight * 0.28;

    ctx.save();

    if (side === 'LEFT') {
      const startX = trunkX;
      // Branch beam extending left
      const grad = ctx.createLinearGradient(startX - branchLength, 0, startX, 0);
      grad.addColorStop(0, '#2d180d');
      grad.addColorStop(1, '#5c3e26');
      ctx.fillStyle = grad;

      ctx.beginPath();
      ctx.roundRect(startX - branchLength, branchY, branchLength, branchThickness, [10, 0, 0, 10]);
      ctx.fill();

      // Hanging Persian brass lantern on the branch
      this.drawLantern(ctx, startX - branchLength + 20, branchY + branchThickness, isYoungPhase);
    } else {
      const startX = trunkX + trunkWidth;
      // Branch beam extending right
      const grad = ctx.createLinearGradient(startX, 0, startX + branchLength, 0);
      grad.addColorStop(0, '#5c3e26');
      grad.addColorStop(1, '#2d180d');
      ctx.fillStyle = grad;

      ctx.beginPath();
      ctx.roundRect(startX, branchY, branchLength, branchThickness, [0, 10, 10, 0]);
      ctx.fill();

      // Hanging Persian brass lantern on the branch
      this.drawLantern(ctx, startX + branchLength - 20, branchY + branchThickness, isYoungPhase);
    }

    ctx.restore();
  }

  private drawLantern(ctx: CanvasRenderingContext2D, x: number, y: number, isYoungPhase: boolean) {
    // Hanging cord
    ctx.strokeStyle = '#d4af37';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(x, y + 10);
    ctx.stroke();

    // Lantern body
    const lanternY = y + 10;
    ctx.fillStyle = '#b8860b';
    ctx.fillRect(x - 6, lanternY, 12, 16);

    // Glowing core
    ctx.fillStyle = isYoungPhase ? '#ffdd59' : '#1abc9c';
    ctx.beginPath();
    ctx.arc(x, lanternY + 8, 4, 0, Math.PI * 2);
    ctx.fill();

    // Lantern Glow
    ctx.fillStyle = isYoungPhase ? 'rgba(255, 221, 89, 0.25)' : 'rgba(26, 188, 156, 0.25)';
    ctx.beginPath();
    ctx.arc(x, lanternY + 8, 12, 0, Math.PI * 2);
    ctx.fill();
  }
}
