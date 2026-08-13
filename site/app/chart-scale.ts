/** Small scaling helpers for the accessible SVG annual-trend chart. */

export interface ScaledPoint {
  x: number;
  y: number;
}

export function linearScale(domain: [number, number], range: [number, number]) {
  const [d0, d1] = domain;
  const [r0, r1] = range;
  return (value: number): number => {
    if (d1 === d0) return r0;
    return r0 + ((value - d0) / (d1 - d0)) * (r1 - r0);
  };
}

export function buildPath(points: ScaledPoint[]): string {
  if (points.length === 0) return "";
  return points
    .map((point, index) => `${index === 0 ? "M" : "L"}${point.x.toFixed(2)},${point.y.toFixed(2)}`)
    .join(" ");
}
