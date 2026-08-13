"use client";

import { useState } from "react";
import type { DailyPoint } from "./registry-types";

interface Props {
  days: DailyPoint[];
}

const PAGE_SIZE = 50;

/** Full accessible paginated data table of every valid paired day. Warmer/cooler
 * is encoded with both an arrow glyph and text ("warmer"/"cooler"), not color
 * alone, per this project's non-color-encoding requirement. */
export function DailyDataTable({ days }: Props) {
  const [page, setPage] = useState(0);
  const pageCount = Math.ceil(days.length / PAGE_SIZE);
  const start = page * PAGE_SIZE;
  const visible = days.slice(start, start + PAGE_SIZE);

  return (
    <div>
      <div className="table-scroll">
        <table>
          <caption>
            All {days.length.toLocaleString()} valid paired days, {days[0]?.date} to{" "}
            {days[days.length - 1]?.date}. Showing rows {start + 1}-{Math.min(start + PAGE_SIZE, days.length)}.
          </caption>
          <thead>
            <tr>
              <th scope="col">Date</th>
              <th scope="col">Westend (urban) TMK, &deg;C</th>
              <th scope="col">Frankfurt/Main (reference) TMK, &deg;C</th>
              <th scope="col">Gap, &deg;C</th>
              <th scope="col">Direction</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((day) => (
              <tr key={day.date}>
                <td>{day.date}</td>
                <td>{day.urban_tmk_c.toFixed(1)}</td>
                <td>{day.reference_tmk_c.toFixed(1)}</td>
                <td>{day.gap_c.toFixed(2)}</td>
                <td>
                  {day.gap_c > 0 ? (
                    <span className="warmer">&#9650; warmer</span>
                  ) : day.gap_c < 0 ? (
                    <span className="cooler">&#9660; cooler</span>
                  ) : (
                    <span>&#9679; equal</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="table-pager">
        <button
          type="button"
          onClick={() => setPage((p) => Math.max(0, p - 1))}
          disabled={page === 0}
        >
          Previous page
        </button>
        <span>
          Page {page + 1} of {pageCount}
        </span>
        <button
          type="button"
          onClick={() => setPage((p) => Math.min(pageCount - 1, p + 1))}
          disabled={page >= pageCount - 1}
        >
          Next page
        </button>
      </div>
    </div>
  );
}
