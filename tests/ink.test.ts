import { describe, expect, it } from 'vitest';
import { inkPath, normalizedRect, strokeHitsPoint, strokeIntersectsRect, translateStroke } from '../src/lib/ink';
import type { InkStroke } from '../src/types';

const stroke: InkStroke = { id: 'stroke', color: 'black', width: 4, points: [{ x: 0, y: 0 }, { x: 10, y: 10 }, { x: 20, y: 0 }], createdAt: '', updatedAt: '' };

describe('whiteboard ink geometry', () => {
  it('builds a smooth SVG path and preserves dots', () => {
    expect(inkPath(stroke.points)).toContain('C 1.67 1.67 6.67 10 10 10');
    expect(inkPath(stroke.points)).toContain('C 13.33 10 18.33 1.67 20 0');
    expect(inkPath([{ x: 2, y: 3 }])).toContain('M 2 3');
  });
  it('hits a whole stroke using a zoom-adjusted tolerance', () => {
    expect(strokeHitsPoint(stroke, { x: 5, y: 6 }, 1)).toBe(true);
    expect(strokeHitsPoint(stroke, { x: 5, y: 20 }, 1)).toBe(false);
  });
  it('normalizes reverse marquees and finds crossing strokes', () => {
    const rect = normalizedRect({ x: 18, y: 8 }, { x: 8, y: 2 });
    expect(rect).toEqual({ x: 8, y: 2, width: 10, height: 6 });
    expect(strokeIntersectsRect(stroke, rect)).toBe(true);
    expect(strokeIntersectsRect(stroke, { x: 30, y: 30, width: 5, height: 5 })).toBe(false);
  });
  it('moves every point without mutating the stored stroke', () => {
    const moved = translateStroke(stroke, { x: 3, y: -2 });
    expect(moved.points[1]).toMatchObject({ x: 13, y: 8 });
    expect(stroke.points[1]).toMatchObject({ x: 10, y: 10 });
  });
});
