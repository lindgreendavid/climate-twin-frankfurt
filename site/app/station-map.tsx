"use client";

import { useId, useState } from "react";
import { compassLabel, haversineDistanceKm, initialBearingDeg, projectToLocalKm } from "./geo";

/** Real, verified DWD station coordinates -- copied from data/provenance.json,
 * not re-derived or approximated. Do not edit these without updating that file
 * first; this component intentionally hardcodes them so the map cannot drift
 * from the provenance record. */
const STATIONS = [
  {
    key: "urban" as const,
    name: "Frankfurt/Main-Westend",
    role: "Urban station",
    dwdId: "01424",
    lat: 50.1269,
    lon: 8.6694,
    elevationM: 120.78,
  },
  {
    key: "reference" as const,
    name: "Frankfurt/Main",
    role: "Reference (“counterpart”) station — physically Frankfurt Airport",
    dwdId: "01420",
    lat: 50.0259,
    lon: 8.5213,
    elevationM: 99.7,
  },
];

const [URBAN, REFERENCE] = STATIONS;

const distanceKm = haversineDistanceKm(URBAN, REFERENCE);
const bearingFromReference = initialBearingDeg(REFERENCE, URBAN);
const elevationDiffM = URBAN.elevationM - REFERENCE.elevationM;

// Local tangent-plane projection, centered on the midpoint of the two stations,
// so both markers sit inside the drawing area with equal margin.
const ORIGIN = { lat: (URBAN.lat + REFERENCE.lat) / 2, lon: (URBAN.lon + REFERENCE.lon) / 2 };

// Matches the wide, flat aspect ratio the site's other figures use (annual-trend-chart
// is 900x340, ~2.6:1) so the map doesn't dominate the page relative to its neighbors.
const WIDTH = 900;
const HEIGHT = 360;
const MARGIN = 80;

const projected = STATIONS.map((station) => ({
  ...station,
  ...projectToLocalKm(station, ORIGIN),
}));

const eastExtent = Math.max(...projected.map((p) => Math.abs(p.eastKm)), 0.1);
const northExtent = Math.max(...projected.map((p) => Math.abs(p.northKm)), 0.1);
// A single shared km-per-pixel scale on both axes, so the drawing does not distort
// real distances -- the same scale is reused for the on-map scale bar.
const kmPerPixel = Math.max(
  (eastExtent * 2) / (WIDTH - MARGIN * 2),
  (northExtent * 2) / (HEIGHT - MARGIN * 2),
);

function toPixel(eastKm: number, northKm: number): { x: number; y: number } {
  return {
    x: WIDTH / 2 + eastKm / kmPerPixel,
    y: HEIGHT / 2 - northKm / kmPerPixel, // screen y grows downward; north is up
  };
}

const points = projected.map((p) => ({ ...p, ...toPixel(p.eastKm, p.northKm) }));

// A round-number scale bar length (km) sized to roughly a third of the drawing width.
const scaleBarKm = (() => {
  const targetKm = (kmPerPixel * (WIDTH - MARGIN * 2)) / 3;
  const steps = [1, 2, 5, 10, 20];
  return steps.reduce((closest, step) => (Math.abs(step - targetKm) < Math.abs(closest - targetKm) ? step : closest), steps[0]);
})();
const scaleBarPx = scaleBarKm / kmPerPixel;

/** Interactive schematic map: a self-contained SVG (no basemap imagery, no mapping
 * library) drawn from the real station coordinates via a local equirectangular
 * projection, with true relative bearing and distance preserved. Each station is a
 * real HTML <button> positioned over the SVG so it is natively focusable, hoverable,
 * and clickable; the always-visible table beneath is the non-interactive equivalent
 * of everything the map conveys, per this project's chart+table pairing pattern. */
export function StationMap() {
  const [activeKey, setActiveKey] = useState<(typeof STATIONS)[number]["key"]>("urban");
  const panelId = useId();
  const active = STATIONS.find((s) => s.key === activeKey) ?? URBAN;

  return (
    <div className="map-card">
      <div className="map-figure">
        <svg
          className="map-schematic"
          viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
          role="img"
          aria-labelledby="station-map-title station-map-desc"
        >
          <title id="station-map-title">
            Schematic map of the two DWD stations near Frankfurt am Main
          </title>
          <desc id="station-map-desc">
            A north-up schematic, not basemap imagery, showing Frankfurt/Main-Westend
            (urban) {compassLabel(bearingFromReference)} of Frankfurt/Main (reference), at
            their true relative bearing and distance of {distanceKm.toFixed(1)} kilometers,
            computed from the real station coordinates. The accessible table below lists
            exact coordinates, elevation, and this computed distance for both stations.
          </desc>
          <line
            className="map-link-line"
            x1={points[1].x}
            y1={points[1].y}
            x2={points[0].x}
            y2={points[0].y}
          />
          <text
            className="map-link-label"
            x={(points[0].x + points[1].x) / 2}
            y={(points[0].y + points[1].y) / 2 - 10}
            textAnchor="middle"
          >
            {distanceKm.toFixed(1)} km
          </text>

          {/* North arrow: this projection is north-up by construction. */}
          <g className="map-compass" transform={`translate(${WIDTH - 54}, 46)`}>
            <line x1="0" y1="18" x2="0" y2="-18" />
            <path d="M 0 -18 L -6 -6 L 6 -6 Z" />
            <text x="0" y="32" textAnchor="middle">N</text>
          </g>

          {/* Scale bar, drawn at the same km-per-pixel scale as the marker positions. */}
          <g className="map-scale-bar" transform={`translate(${MARGIN}, ${HEIGHT - 34})`}>
            <line x1="0" y1="0" x2={scaleBarPx} y2="0" />
            <line x1="0" y1="-5" x2="0" y2="5" />
            <line x1={scaleBarPx} y1="-5" x2={scaleBarPx} y2="5" />
            <text x={scaleBarPx / 2} y="-8" textAnchor="middle">
              {scaleBarKm} km
            </text>
          </g>

          {points.map((point) => (
            <circle
              key={`${point.key}-marker-shadow`}
              className={`map-marker-dot map-marker-dot--${point.key}`}
              cx={point.x}
              cy={point.y}
              r={activeKey === point.key ? 10 : 8}
            />
          ))}
        </svg>

        <div className="map-markers">
          {points.map((point) => (
            <button
              key={point.key}
              type="button"
              className={`map-marker map-marker--${point.key}`}
              style={{ left: `${(point.x / WIDTH) * 100}%`, top: `${(point.y / HEIGHT) * 100}%` }}
              onMouseEnter={() => setActiveKey(point.key)}
              onFocus={() => setActiveKey(point.key)}
              onClick={() => setActiveKey(point.key)}
              aria-pressed={activeKey === point.key}
              aria-describedby={panelId}
            >
              <span className="map-marker__label">{point.name}</span>
            </button>
          ))}
        </div>

        <div className="map-legend">
          <span>
            <i className="map-legend-swatch map-legend-swatch--urban" aria-hidden="true" /> Urban
            station
          </span>
          <span>
            <i className="map-legend-swatch map-legend-swatch--reference" aria-hidden="true" />{" "}
            Reference station
          </span>
          <span className="map-legend-note">
            Schematic, north-up, drawn to scale from real coordinates &mdash; not basemap
            imagery.
          </span>
        </div>
      </div>

      <div id={panelId} className="map-detail" role="status">
        <span className="map-detail__role">{active.role}</span>
        <h4>{active.name}</h4>
        <dl>
          <div>
            <dt>DWD station ID</dt>
            <dd>{active.dwdId}</dd>
          </div>
          <div>
            <dt>Coordinates</dt>
            <dd>
              {active.lat.toFixed(4)}&deg; N, {active.lon.toFixed(4)}&deg; E
            </dd>
          </div>
          <div>
            <dt>Elevation</dt>
            <dd>{active.elevationM.toFixed(2)} m</dd>
          </div>
        </dl>
      </div>

      <details className="map-calc">
        <summary>How the {distanceKm.toFixed(2)} km distance and {Math.abs(elevationDiffM).toFixed(2)} m elevation difference were computed</summary>
        <p>
          Straight-line (great-circle) distance via the haversine formula, from each
          station&apos;s real coordinates in <code>data/provenance.json</code>:
        </p>
        <code className="map-calc__formula">
          a = sin&sup2;(&Delta;lat/2) + cos(lat&#8321;)&middot;cos(lat&#8322;)&middot;sin&sup2;(&Delta;lon/2)
          <br />
          distance = 2&middot;R&middot;atan2(&radic;a, &radic;(1&minus;a)), R = 6371.0088 km
        </code>
        <p>
          lat&#8321;={URBAN.lat}, lon&#8321;={URBAN.lon} (Westend, urban) &middot; lat&#8322;=
          {REFERENCE.lat}, lon&#8322;={REFERENCE.lon} (Frankfurt/Main, reference)
          &rarr; <strong>{distanceKm.toFixed(3)} km</strong>, initial bearing from the
          reference station <strong>{bearingFromReference.toFixed(1)}&deg;</strong> (
          {compassLabel(bearingFromReference)}).
        </p>
        <p>
          Elevation difference: {URBAN.elevationM} m &minus; {REFERENCE.elevationM} m ={" "}
          <strong>{elevationDiffM.toFixed(2)} m</strong> &mdash; Westend sits higher.
        </p>
      </details>

      <div className="table-scroll">
        <table>
          <caption>Station locations, elevation, and the computed distance between them</caption>
          <thead>
            <tr>
              <th scope="col">Station</th>
              <th scope="col">Role</th>
              <th scope="col">DWD ID</th>
              <th scope="col">Latitude</th>
              <th scope="col">Longitude</th>
              <th scope="col">Elevation, m</th>
            </tr>
          </thead>
          <tbody>
            {STATIONS.map((station) => (
              <tr key={station.key}>
                <td>{station.name}</td>
                <td>{station.role}</td>
                <td>{station.dwdId}</td>
                <td>{station.lat.toFixed(4)}&deg; N</td>
                <td>{station.lon.toFixed(4)}&deg; E</td>
                <td>{station.elevationM.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={6}>
                Straight-line distance between the two stations: <strong>{distanceKm.toFixed(2)} km</strong>{" "}
                (bearing {bearingFromReference.toFixed(1)}&deg; / {compassLabel(bearingFromReference)}{" "}
                from the reference station to the urban station). Elevation difference:{" "}
                <strong>{elevationDiffM.toFixed(2)} m</strong> (Westend higher). Both computed
                from the coordinates above via the haversine formula &mdash; see the
                calculation above the table.
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
