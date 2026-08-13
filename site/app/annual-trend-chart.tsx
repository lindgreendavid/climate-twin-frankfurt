import { buildPath, linearScale } from "./chart-scale";
import type { TrendSummary } from "./registry-types";

interface Props {
  annualMeans: Record<string, number>;
  trend: TrendSummary;
}

const WIDTH = 900;
const HEIGHT = 340;
const PADDING = 44;

/** Accessible SVG chart: one point per year's mean urban-reference gap, plus the
 * preregistered OLS trend line (dashed, distinct from the solid data line so the
 * "actual data" vs. "fitted trend" distinction does not rely on color alone). */
export function AnnualTrendChart({ annualMeans, trend }: Props) {
  const years = Object.keys(annualMeans)
    .map(Number)
    .sort((a, b) => a - b);
  const values = years.map((year) => annualMeans[String(year)]);

  const xDomain: [number, number] = [years[0], years[years.length - 1]];
  const yMin = Math.min(...values, 0);
  const yMax = Math.max(...values);
  const yPad = (yMax - yMin) * 0.15 || 0.1;
  const yDomain: [number, number] = [yMin - yPad, yMax + yPad];

  const scaleX = linearScale(xDomain, [PADDING, WIDTH - PADDING]);
  const scaleY = linearScale(yDomain, [HEIGHT - PADDING, PADDING]);

  const dataPoints = years.map((year) => ({ x: scaleX(year), y: scaleY(annualMeans[String(year)]) }));
  const dataPath = buildPath(dataPoints);

  const fitPath =
    trend.slope_c_per_year !== null && trend.intercept_c !== null
      ? buildPath(
          xDomain.map((year) => ({
            x: scaleX(year),
            y: scaleY(trend.intercept_c! + trend.slope_c_per_year! * year),
          })),
        )
      : "";

  const zeroY = scaleY(0);
  const gridYValues = Array.from({ length: 5 }, (_, i) => yDomain[0] + ((yDomain[1] - yDomain[0]) * i) / 4);

  return (
    <figure>
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-labelledby="annual-trend-title annual-trend-desc"
      >
        <title id="annual-trend-title">Annual mean urban-reference temperature gap, 1986-2025</title>
        <desc id="annual-trend-desc">
          Line chart of each year&apos;s mean daily temperature gap (Frankfurt/Main-Westend minus
          Frankfurt/Main) from {years[0]} to {years[years.length - 1]}, with the preregistered linear
          trend line overlaid. The trend line is nearly flat and its confidence interval crosses
          zero slope; see the accessible data table below for exact year-by-year values.
        </desc>
        {gridYValues.map((value) => (
          <g key={value}>
            <line
              className="chart-grid"
              x1={PADDING}
              x2={WIDTH - PADDING}
              y1={scaleY(value)}
              y2={scaleY(value)}
            />
            <text x={4} y={scaleY(value) + 3}>
              {value.toFixed(2)}
            </text>
          </g>
        ))}
        <line
          className="chart-grid"
          x1={PADDING}
          x2={WIDTH - PADDING}
          y1={zeroY}
          y2={zeroY}
          strokeDasharray="2 3"
        />
        <text x={WIDTH - PADDING - 60} y={zeroY - 6}>
          zero gap
        </text>
        {years
          .filter((year) => year % 5 === 0)
          .map((year) => (
            <text key={year} x={scaleX(year)} y={HEIGHT - PADDING + 18} textAnchor="middle">
              {year}
            </text>
          ))}
        <path className="trend-line trend-line--gap" d={dataPath} />
        {fitPath && <path className="trend-line trend-line--fit" d={fitPath} />}
      </svg>
      <figcaption className="chart-legend">
        <span>
          <i className="legend-swatch--gap" aria-hidden="true" /> Observed annual mean gap (solid
          line)
        </span>
        <span>
          <i className="legend-swatch--fit" aria-hidden="true" /> Preregistered OLS linear trend
          (dashed line)
        </span>
      </figcaption>
    </figure>
  );
}
