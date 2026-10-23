import type { InkPoint, InkStroke, Point, Quad } from '../types';

export function inkPath(points: readonly InkPoint[]): string {
  if (!points.length) return '';
  if (points.length === 1) return `M ${points[0].x} ${points[0].y} l 0.01 0`;
  if (points.length === 2) return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  let path = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length - 1; i++) {
    const next = points[i + 1];
    path += ` Q ${points[i].x} ${points[i].y} ${(points[i].x + next.x) / 2} ${(points[i].y + next.y) / 2}`;
  }
  const last = points[points.length - 1];
  return `${path} L ${last.x} ${last.y}`;
}

export function normalizedRect(a: Point, b: Point): Quad {
  return { x: Math.min(a.x, b.x), y: Math.min(a.y, b.y), width: Math.abs(a.x - b.x), height: Math.abs(a.y - b.y) };
}

function distanceToSegment(point: Point, a: Point, b: Point): number {
  const dx = b.x - a.x; const dy = b.y - a.y;
  if (!dx && !dy) return Math.hypot(point.x - a.x, point.y - a.y);
  const t = Math.max(0, Math.min(1, ((point.x - a.x) * dx + (point.y - a.y) * dy) / (dx * dx + dy * dy)));
  return Math.hypot(point.x - (a.x + t * dx), point.y - (a.y + t * dy));
}

export function strokeHitsPoint(stroke: InkStroke, point: Point, tolerance: number): boolean {
  const radius = tolerance + stroke.width / 2;
  if (stroke.points.length === 1) return Math.hypot(point.x - stroke.points[0].x, point.y - stroke.points[0].y) <= radius;
  for (let i = 1; i < stroke.points.length; i++) if (distanceToSegment(point, stroke.points[i - 1], stroke.points[i]) <= radius) return true;
  return false;
}

function inside(point: Point, rect: Quad, padding = 0) {
  return point.x >= rect.x - padding && point.x <= rect.x + rect.width + padding && point.y >= rect.y - padding && point.y <= rect.y + rect.height + padding;
}

function orientation(a: Point, b: Point, c: Point) { return (b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y); }
function onSegment(a: Point, b: Point, point: Point) {
  return point.x >= Math.min(a.x, b.x) && point.x <= Math.max(a.x, b.x) && point.y >= Math.min(a.y, b.y) && point.y <= Math.max(a.y, b.y);
}
function segmentIntersects(a: Point, b: Point, c: Point, d: Point) {
  const o1 = orientation(a, b, c); const o2 = orientation(a, b, d); const o3 = orientation(c, d, a); const o4 = orientation(c, d, b);
  if (Math.sign(o1) !== Math.sign(o2) && Math.sign(o3) !== Math.sign(o4)) return true;
  return (o1 === 0 && onSegment(a, b, c)) || (o2 === 0 && onSegment(a, b, d)) || (o3 === 0 && onSegment(c, d, a)) || (o4 === 0 && onSegment(c, d, b));
}

export function strokeIntersectsRect(stroke: InkStroke, rect: Quad): boolean {
  const padding = stroke.width / 2;
  if (stroke.points.some(point => inside(point, rect, padding))) return true;
  const left = rect.x - padding; const top = rect.y - padding; const right = rect.x + rect.width + padding; const bottom = rect.y + rect.height + padding;
  const sides: [Point, Point][] = [
    [{ x: left, y: top }, { x: right, y: top }], [{ x: right, y: top }, { x: right, y: bottom }],
    [{ x: right, y: bottom }, { x: left, y: bottom }], [{ x: left, y: bottom }, { x: left, y: top }],
  ];
  for (let i = 1; i < stroke.points.length; i++) if (sides.some(([a, b]) => segmentIntersects(stroke.points[i - 1], stroke.points[i], a, b))) return true;
  return false;
}

export function translateStroke(stroke: InkStroke, delta: Point): InkStroke {
  return { ...stroke, points: stroke.points.map(point => ({ ...point, x: point.x + delta.x, y: point.y + delta.y })) };
}
