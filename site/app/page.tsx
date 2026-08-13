import registryJson from "./data/registry.json";
import type { Registry } from "./registry-types";
import { AnnualTrendChart } from "./annual-trend-chart";
import { GapSummaryTable } from "./gap-summary-table";
import { DailyDataTable } from "./daily-data-table";
import { StationMap } from "./station-map";

const registry = registryJson as unknown as Registry;
const { period, gap, trend, annual_means, daily_series, stations, year_coverage } = registry;

function fmt(value: number | null, digits = 3): string {
  if (value === null) return "n/a";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(digits)}`;
}

export default function Home() {
  return (
    <>
      <a href="#main" className="skip-link">
        Skip to main content
      </a>
      <header className="nav">
        <div className="brand">
          <span className="brand__mark" aria-hidden="true">
            ~
          </span>
          <span>Climate Twin Frankfurt</span>
        </div>
        <nav className="nav__links" aria-label="Primary">
          <a href="#map">The stations</a>
          <a href="#gap">The gap</a>
          <a href="#trend">The trend</a>
          <a href="#decision">Findings</a>
          <a href="#method">Method</a>
          <a href="#sources">Data &amp; citations</a>
        </nav>
      </header>

      <main id="main">
        <section className="hero">
          <div className="eyebrow">
            <span>DWD daily-KL reanalysis</span>
            <span>v0.1.0 · preregistered · frozen registry</span>
          </div>
          <h1>
            Is Frankfurt <em>actually</em> warmer?
          </h1>
          <p className="hero__lead">
            Frankfurt/Main-Westend, an inner-city DWD climate station, is compared against
            Frankfurt/Main — DWD&apos;s own designated &quot;counterpart&quot; reference station,
            physically located at the airport — using every day both stations recorded a valid
            daily mean temperature between 1985 and 2025. The gap and its uncertainty are
            reported before any &quot;warmer&quot; or &quot;trending&quot; conclusion.
          </p>
          <div className="hero__actions">
            <a className="button button--primary" href="#gap">
              See the measured gap
            </a>
            <a
              className="button button--ghost"
              href="https://github.com/lindgreendavid/climate-twin-frankfurt/blob/main/docs/research-report.md"
            >
              Read the full report
            </a>
          </div>
          <div className="hero__principles">
            <span>Preregistered protocol</span>
            <span>Real public DWD data</span>
            <span>Frozen result registry</span>
            <span>Uncertainty stated first</span>
          </div>
        </section>

        <section className="findings" aria-labelledby="sample-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">01</span>
              <p>Sample</p>
            </div>
            <h2 id="sample-heading">{period.n_valid_paired_days.toLocaleString()} valid paired days</h2>
          </div>
          <div className="stat-row">
            <article>
              <span>Record span</span>
              <strong style={{ fontSize: 18 }}>
                {period.start_date} &rarr; {period.end_date}
              </strong>
              <small>real DWD daily-KL &quot;historical&quot; archives</small>
            </article>
            <article>
              <span>Urban station</span>
              <strong style={{ fontSize: 18 }}>{stations.urban.name}</strong>
              <small>DWD station {stations.urban.id}</small>
            </article>
            <article>
              <span>Reference station</span>
              <strong style={{ fontSize: 18 }}>{stations.reference.name}</strong>
              <small>DWD station {stations.reference.id} (airport site)</small>
            </article>
            <article>
              <span>Years in trend regression</span>
              <strong>{year_coverage.included_years.length}</strong>
              <small>
                of {year_coverage.included_years.length + year_coverage.excluded_years.length}{" "}
                touched years ({year_coverage.excluded_years.join(", ")} excluded: &lt;300 valid
                days)
              </small>
            </article>
          </div>

          <div className="limitations-first">
            <h3>Read this before any &quot;warmer&quot; or &quot;trending&quot; conclusion below</h3>
            <ul>
              <li>
                The reference station is DWD&apos;s own designated &quot;counterpart&quot; for
                Westend — but it is Frankfurt Airport, an open, semi-paved site, not a verified
                pristine rural baseline.
              </li>
              <li>
                This measures the <strong>daily mean</strong> temperature gap only, not daily
                minimum (overnight) temperature, which is the variable most often associated with
                larger reported urban heat island effects.
              </li>
              <li>
                Two stations, one pairing: elevation, distance, and instrument history differ
                between them in ways this comparison cannot separate from any urban-canopy
                effect.
              </li>
              <li>
                This project does not claim to measure &quot;the&quot; Frankfurt urban heat
                island in general, and does not build an independent land-use model.
              </li>
            </ul>
            <p>Full disclosure: docs/research-protocol.md and docs/research-report.md.</p>
          </div>
        </section>

        <section id="map" className="compare" aria-labelledby="map-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">02</span>
              <p>Where</p>
            </div>
            <h2 id="map-heading">Where the two stations actually are</h2>
          </div>

          <p className="uncertainty-note" style={{ marginBottom: 24 }}>
            A north-up schematic drawn to real scale from the coordinates in{" "}
            <code>data/provenance.json</code> &mdash; not basemap imagery and not a live map
            service. Hover, click, or tab to a marker for that station&apos;s details; the table
            below carries the same information as accessible text.
          </p>

          <StationMap />
        </section>

        <section id="gap" className="compare" aria-labelledby="gap-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">03</span>
              <p>Uncertainty first</p>
            </div>
            <h2 id="gap-heading">The measured gap</h2>
          </div>

          <p className="uncertainty-note" style={{ marginBottom: 24 }}>
            Mean daily gap (urban minus reference), with a 95% confidence interval from a 30-day
            block bootstrap (10,000 resamples) — chosen over a naive resample because consecutive
            days&apos; temperatures are strongly autocorrelated. Read the confidence interval
            before the point estimate.
          </p>

          <div className="chart-card">
            <h3>
              Full-period mean gap: {fmt(gap.full_period.mean_gap_c, 3)} &deg;C{" "}
              {gap.full_period.gap_excludes_zero ? (
                <span className="result-tag result-tag--significant">CI excludes zero</span>
              ) : (
                <span className="result-tag result-tag--not-significant">CI includes zero</span>
              )}
            </h3>
            <p>
              95% CI [{fmt(gap.full_period.ci_95_low, 3)}, {fmt(gap.full_period.ci_95_high, 3)}] &deg;C
              over {gap.full_period.n_days.toLocaleString()} valid paired days. The interval
              excludes zero, so Westend is measurably warmer on average than the reference
              station over this record — but the magnitude is modest, well under one full degree
              Celsius.
            </p>
            <GapSummaryTable fullPeriod={gap.full_period} bySeason={gap.by_season} />
          </div>
        </section>

        <section id="trend" className="report" aria-labelledby="trend-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">04</span>
              <p>Uncertainty first</p>
            </div>
            <h2 id="trend-heading">Has the gap trended?</h2>
          </div>

          <p className="uncertainty-note" style={{ marginBottom: 24 }}>
            Ordinary least squares trend of each included year&apos;s mean gap against year, with a
            classical 95% confidence interval on the slope. Read the confidence interval and
            p-value before any &quot;widening&quot; or &quot;narrowing&quot; conclusion.
          </p>

          <div className="chart-card">
            <h3>
              Trend: {fmt(trend.slope_c_per_year, 4)} &deg;C/year{" "}
              {trend.significant ? (
                <span className="result-tag result-tag--significant">significant</span>
              ) : (
                <span className="result-tag result-tag--not-significant">not significant</span>
              )}
            </h3>
            <p>
              95% CI [{fmt(trend.ci_95_low, 4)}, {fmt(trend.ci_95_high, 4)}] &deg;C/year, p ={" "}
              {trend.p_value !== null ? trend.p_value.toFixed(3) : "n/a"}, R&sup2; ={" "}
              {trend.r_squared !== null ? trend.r_squared.toFixed(3) : "n/a"}, n ={" "}
              {trend.n_years} years. <strong>The confidence interval crosses zero and the
              p-value does not clear this project&apos;s preregistered &alpha; = 0.05
              threshold: no statistically detectable trend in the urban-reference gap over this
              ~40-year record.</strong>
            </p>
            <AnnualTrendChart annualMeans={annual_means} trend={trend} />
            <div className="stat-footer">
              <div>
                <span>Slope</span>
                <strong>{fmt(trend.slope_c_per_year, 4)} &deg;C/yr</strong>
              </div>
              <div>
                <span>p-value</span>
                <strong>{trend.p_value !== null ? trend.p_value.toFixed(3) : "n/a"}</strong>
              </div>
              <div>
                <span>R&sup2;</span>
                <strong>{trend.r_squared !== null ? trend.r_squared.toFixed(3) : "n/a"}</strong>
              </div>
              <div>
                <span>Years used</span>
                <strong>{trend.n_years}</strong>
              </div>
            </div>
            <details className="data-alternative">
              <summary>Read the complete daily data table ({daily_series.length.toLocaleString()} rows)</summary>
              <DailyDataTable days={daily_series} />
            </details>
          </div>
        </section>

        <section id="decision" className="decision" aria-labelledby="decision-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">05</span>
              <p>Findings</p>
            </div>
            <h2 id="decision-heading">What this does and does not conclude</h2>
          </div>
          <div className="decision-reading">
            <article>
              <span>Confirmed</span>
              <h3>Westend runs measurably warmer</h3>
              <p>
                The full-period 95% CI on the mean gap excludes zero, and so does every season&apos;s
                CI. This project states that plainly, because the data support it.
              </p>
            </article>
            <article>
              <span>Not detected</span>
              <h3>No significant trend over ~40 years</h3>
              <p>
                The preregistered OLS trend test found a CI that includes zero and p = 0.118.
                Reported as &quot;not detected at this record length,&quot; not reworded to imply
                a trend either way.
              </p>
            </article>
            <article>
              <span>Not claimed</span>
              <h3>Not &quot;the&quot; Frankfurt UHI</h3>
              <p>
                This is one urban station vs. DWD&apos;s own airport-based reference. A different
                reference, a different variable (daily minimum), or a different district would
                very plausibly show a different number.
              </p>
            </article>
          </div>
        </section>

        <section id="method" className="method" aria-labelledby="method-heading">
          <div className="section-heading section-heading--light">
            <div>
              <span className="section-index">06</span>
              <p>Scientific method</p>
            </div>
            <h2 id="method-heading">How this was measured</h2>
          </div>
          <div className="method-grid">
            <article>
              <span>Pairing</span>
              <h3>Inner join on calendar date</h3>
              <p>
                Only days where both stations report a non-missing TMK (DWD&apos;s daily mean
                temperature column) are included. DWD&apos;s missing-value sentinel (-999) is
                dropped, never imputed.
              </p>
            </article>
            <article>
              <span>Uncertainty</span>
              <h3>Block bootstrap, not i.i.d.</h3>
              <p>
                30-day contiguous blocks, resampled with replacement, 10,000 resamples, seeded
                (20260813) for exact reproducibility — because consecutive daily temperatures are
                strongly autocorrelated.
              </p>
            </article>
            <article>
              <span>Trend</span>
              <h3>OLS on annual means, years with &ge;300 valid days</h3>
              <p>
                A simple, preregistered linear model — not a search over more flexible curves
                after seeing the result. Classical t-distribution CI on the slope.
              </p>
            </article>
          </div>
          <div className="equation-card">
            <span>Primary quantity</span>
            <code>gap = TMK(Westend, 01424) &minus; TMK(Frankfurt/Main, 01420)</code>
            <code>trend: annual_mean(gap) ~ &beta;&#8320; + &beta;&#8321; &middot; year</code>
          </div>
          <p style={{ color: "#d8c6ab", maxWidth: 720, fontSize: 13, lineHeight: 1.6 }}>
            Full method, exclusion criteria, and station-selection rationale:{" "}
            <a
              style={{ textDecoration: "underline" }}
              href="https://github.com/lindgreendavid/climate-twin-frankfurt/blob/main/docs/research-protocol.md"
            >
              docs/research-protocol.md
            </a>
            .
          </p>
        </section>

        <section id="sources" className="evidence" aria-labelledby="sources-heading">
          <div className="section-heading">
            <div>
              <span className="section-index">07</span>
              <p>Data &amp; citations</p>
            </div>
            <h2 id="sources-heading">Provenance</h2>
          </div>
          <div className="source-list">
            <a href="https://opendata.dwd.de/climate_environment/CDC/observations_germany/climate/daily/kl/historical/">
              <span>Data</span>
              <div>
                <strong>DWD CDC Open Data — daily climate summary (Tageswerte KL)</strong>
                <p>Deutscher Wetterdienst Climate Data Center, historical/ archives for stations 01424 and 01420.</p>
              </div>
              <p>Accessed 2026-08-13. Pinned snapshot, not a live feed — see the protocol.</p>
              <span aria-hidden="true">&rarr;</span>
            </a>
            <a href="https://www.dwd.de/EN/climate_environment/climateresearch/climate_impact/urbanism/urban_climate_stations/urban_climate_stations_node.html">
              <span>Pairing</span>
              <div>
                <strong>DWD Urban and Regional Climatology — station pairing table</strong>
                <p>DWD&apos;s own designated urban/rural pair for Frankfurt: 01424 (Westend) &amp; 01420 (Frankfurt/Main).</p>
              </div>
              <p>Verified by fetching raw HTML directly, not only an AI summary.</p>
              <span aria-hidden="true">&rarr;</span>
            </a>
            <a href="https://opendata.dwd.de/climate_environment/CDC/Terms_of_use.pdf">
              <span>License</span>
              <div>
                <strong>CC BY 4.0 — DWD CDC-OpenData Terms of Use</strong>
                <p>&quot;The Creative Commons BY 4.0 - Licence &apos;CC BY 4.0&apos; apply.&quot; (status: Mai 2024)</p>
              </div>
              <p>Quoted directly from the fetched PDF.</p>
              <span aria-hidden="true">&rarr;</span>
            </a>
            <a href="https://github.com/lindgreendavid/climate-twin-frankfurt/blob/main/data/provenance.json">
              <span>Provenance record</span>
              <div>
                <strong>data/provenance.json</strong>
                <p>Full station metadata, source URLs, license text, and access date.</p>
              </div>
              <p>Committed to the repository.</p>
              <span aria-hidden="true">&rarr;</span>
            </a>
          </div>
        </section>
      </main>

      <footer>
        <div>
          <span className="brand__mark" aria-hidden="true">
            ~
          </span>
          <p>
            Climate Twin Frankfurt v0.1.0 &middot; MIT-licensed code, CC BY 4.0 DWD data &middot;{" "}
            <a href="https://github.com/lindgreendavid/climate-twin-frankfurt/blob/main/ACCESSIBILITY.md">
              Accessibility statement
            </a>
          </p>
        </div>
        <a href="https://github.com/lindgreendavid/climate-twin-frankfurt">View source on GitHub</a>
      </footer>
    </>
  );
}
