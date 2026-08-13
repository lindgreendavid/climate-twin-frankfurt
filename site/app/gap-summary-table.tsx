import type { GapSummary } from "./registry-types";

const SEASON_LABELS: Record<string, string> = {
  DJF: "Winter (Dec-Feb)",
  MAM: "Spring (Mar-May)",
  JJA: "Summer (Jun-Aug)",
  SON: "Autumn (Sep-Nov)",
};

interface Props {
  fullPeriod: GapSummary;
  bySeason: Record<string, GapSummary>;
}

export function GapSummaryTable({ fullPeriod, bySeason }: Props) {
  const rows = [
    { key: "full", label: "Full period", summary: fullPeriod },
    ...Object.entries(bySeason).map(([key, summary]) => ({
      key,
      label: SEASON_LABELS[key] ?? key,
      summary,
    })),
  ];

  return (
    <div className="table-scroll">
      <table>
        <caption>Mean daily urban-reference gap, full period and by meteorological season</caption>
        <thead>
          <tr>
            <th scope="col">Period</th>
            <th scope="col">Valid days</th>
            <th scope="col">Mean gap, &deg;C</th>
            <th scope="col">95% CI</th>
            <th scope="col">Excludes zero?</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.key}>
              <td>{row.label}</td>
              <td>{row.summary.n_days.toLocaleString()}</td>
              <td>
                {row.summary.mean_gap_c !== null ? `+${row.summary.mean_gap_c.toFixed(3)}` : "n/a"}
              </td>
              <td>
                {row.summary.ci_95_low !== null && row.summary.ci_95_high !== null
                  ? `[+${row.summary.ci_95_low.toFixed(3)}, +${row.summary.ci_95_high.toFixed(3)}]`
                  : "n/a"}
              </td>
              <td>
                {row.summary.gap_excludes_zero ? (
                  <span className="result-tag result-tag--significant">Yes</span>
                ) : (
                  <span className="result-tag result-tag--not-significant">No</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
