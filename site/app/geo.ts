/** Small geodesy helpers for the station map. No mapping library: every value
 * here is computed directly from the real station coordinates in
 * data/provenance.json using standard closed-form formulas (haversine great-circle
 * distance, initial bearing, and a local equirectangular tangent-plane projection
 * for placing markers). Nothing here is fitted, estimated, or approximated beyond
 * the formulas' own well-known accuracy at this scale (a few km). */

export interface LatLon {
  lat: number;
  lon: number;
}

/** Mean Earth radius in km (IUGG mean radius), used for the haversine formula. */
const EARTH_RADIUS_KM = 6371.0088;

/** Meters per degree of latitude, used for the local flat-plane projection.
 * Longitude degrees are additionally scaled by cos(latitude) to account for
 * meridian convergence -- see `project` below. */
const KM_PER_DEG_LAT = 111.32;

function toRad(degrees: number): number {
  return (degrees * Math.PI) / 180;
}

function toDeg(radians: number): number {
  return (radians * 180) / Math.PI;
}

/** Great-circle distance between two lat/lon points, in km, via the haversine
 * formula: a = sin²(Δlat/2) + cos(lat1)·cos(lat2)·sin²(Δlon/2),
 * distance = 2·R·atan2(√a, √(1-a)). */
export function haversineDistanceKm(a: LatLon, b: LatLon): number {
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const sinA = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
  const c = 2 * Math.atan2(Math.sqrt(sinA), Math.sqrt(1 - sinA));
  return EARTH_RADIUS_KM * c;
}

/** Initial compass bearing (0-360, 0 = north, clockwise) travelling from a to b. */
export function initialBearingDeg(a: LatLon, b: LatLon): number {
  const y = Math.sin(toRad(b.lon - a.lon)) * Math.cos(toRad(b.lat));
  const x =
    Math.cos(toRad(a.lat)) * Math.sin(toRad(b.lat)) -
    Math.sin(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.cos(toRad(b.lon - a.lon));
  const bearing = toDeg(Math.atan2(y, x));
  return (bearing + 360) % 360;
}

const COMPASS_POINTS = [
  "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
  "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
];

/** Nearest 16-point compass label for a bearing in degrees. */
export function compassLabel(bearingDegValue: number): string {
  const index = Math.round(bearingDegValue / 22.5) % 16;
  return COMPASS_POINTS[index];
}

/** Projects a lat/lon point onto a local flat tangent plane centered on `origin`,
 * returning east/north offsets in km. East is scaled by cos(origin.lat) so that
 * equal km in both axes render at true relative scale -- this is what keeps the
 * schematic's real bearing and distance ratio accurate, not just its two marker
 * positions. */
export function projectToLocalKm(point: LatLon, origin: LatLon): { eastKm: number; northKm: number } {
  const northKm = (point.lat - origin.lat) * KM_PER_DEG_LAT;
  const eastKm = (point.lon - origin.lon) * KM_PER_DEG_LAT * Math.cos(toRad(origin.lat));
  return { eastKm, northKm };
}
