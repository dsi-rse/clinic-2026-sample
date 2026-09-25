# Tutorial: Building and Extending Your Dashboard

This walkthrough takes you from zero to a live dashboard.
By the end you will have:

1. Started the dev server and seen charts on real Chicago 311 data
2. Understood how data flows from your pipeline to the browser
3. Changed an existing chart
4. Added a filter backed by the Zustand store
5. Added a new tab — framed as an agent task you hand to an LLM
6. Shipped the dashboard to a public Cloudflare Pages URL

File paths in this part are relative to `dashboard/` unless marked otherwise.

Before you start, make sure you've completed the
[computer setup guide](https://github.com/dsi-clinic/the-clinic/blob/main/tutorials/clinic-computer-setup.md)
and have **Make** plus **Docker** working on your machine.  (The dashboard
pathway is built and supported for projects generated with `docker=yes`.  If
your project was generated with `docker=no`, the `dashboard-*` Make targets
call `npm` directly instead — that path is best-effort and needs **Node 22+**
installed on your machine.)

---

## Step 1: Run It

From a terminal on your machine (not inside a Docker container), pull the
example datasets from Box, then start the dev server:

```bash
make dashboard-data
make dashboard-dev
```

Open http://localhost:5173.  You should see a dashboard with global controls
(a request-type picker and a year-range slider) and three tabs: **Trends**
(stat tiles plus trend and breakdown charts), **Map** (a choropleth of
requests per community area), and **SQL** (a live query console).  Everything
queries the parquet files that `make dashboard-data` just placed in
`public/data/`.

> **Troubleshooting.** If `make dashboard-dev` errors with "Docker not found",
> make sure Docker Desktop is running, then run
> `make dashboard-install && make dashboard-dev` once to install deps inside
> the container.  If it errors with `npm: not found`, your project was
> generated with `docker=no` — install Node 22+ (there is no container in that
> configuration).  See `dashboard/README.md` for the full command reference.

---

## Step 2: How Data Flows

```
pipeline → parquet → Box public static link
                              ↓
                      data.manifest.json
                              ↓
                      scripts/pull_data.py
                              ↓
                      public/data/*.parquet   (max 150 MB total)
                              ↓
                      DuckDB-wasm (in the browser)
                              ↓
                      useQuery() hook → PlotFigure / MapLibre
```

**The example datasets** come from Box via the manifest: `reqs_311` (a toy
sample of ~1.6M Chicago 311 service requests: `creation_date, status,
type_of_service_request, community_area, …`) and `community_areas` (Chicago's
77 community areas as GeoParquet, with a MapLibre-ready `geometry_geojson`
column).  Their full schemas live in `data/dictionary/`.

**For real project data**, the workflow is:

1. In your pipeline, call `export_dataset(df, "my_dataset")` from
   `src/<module>/dashboard_export.py` (project root, not `dashboard/src/`).
   This writes
   `dashboard/public/data/my_dataset.parquet` and a data dictionary to
   `dashboard/data/dictionary/my_dataset.{json,md}`.
2. Upload the parquet to Box and copy the **direct-download** static link.
3. Add an entry to `data.manifest.json`:
   ```json
   {"name": "my_dataset", "url": "https://uchicago.box.com/shared/static/..."}
   ```
4. Run `make dashboard-data` to pull the file into `public/data/`.

The data dictionary (committed JSON + Markdown) documents every column's type,
null count, unique-value count, and range (plus sample values if you export
with `include_samples=True` — off by default, since dictionaries are committed
to git).  Hand it to an LLM instead of pasting raw data — see Step 5.

**DuckDB views** — every manifest entry is registered at startup as a view
named after the file stem.  A query like `SELECT * FROM reqs_311 LIMIT 5` or
`SELECT * FROM my_dataset WHERE category = 'A'` just works.

---

## Step 3: Change a Chart

Open `src/pages/OverviewPage.tsx` and find the **Requests per month** card: the
`<PlotFigure options={{ ... }} />` whose `marks` array holds a `Plot.areaY`, a
`Plot.lineY`, and a `Plot.ruleY`.  The `options` prop is a plain
[Observable Plot](https://observablehq.com/plot/) spec — edit it, save, and the
browser hot-reloads.

Try two edits:

1. **Make it a step chart.**  Inside the `Plot.lineY(monthly, { ... })` options,
   add a line next to `strokeWidth: 2,`:

   ```tsx
   curve: 'step',
   ```

2. **Add a dot for each month.**  Marks draw in array order, so add this after
   the `Plot.lineY(...)` entry and before `Plot.ruleY([0])`:

   ```tsx
   Plot.dot(monthly, {
     x: (d: { month: string }) => new Date(d.month),
     y: 'n',
     fill: ACCENT,
   }),
   ```

`options` takes the plain spec object — `PlotFigure` calls `Plot.plot()` for
you.  `monthly` is the result of the `useQuery<...>(sql)` call near the top of
the file: an array of typed row objects, one per month.

> **Where do column names come from?** Read
> `data/dictionary/reqs_311.json` — it lists every column with its type and
> value ranges.  Never guess column names; always check the dictionary first.

---

## Step 4: Add a Filter

You will add a **Status** picker (Completed / Open) next to the existing
request-type picker, and make every chart respect it.  Filters that apply
across tabs live in the Zustand store at `src/store/filters.ts`; every chart
builds its SQL `WHERE` clause with the `filterSql()` helper in the same file.
That is the whole trick: add the filter to the store and to `filterSql`, and
every chart picks it up.

**1. Extend the store.**  In `src/store/filters.ts`, add two fields to the
`FiltersState` interface and two entries to the `create(...)` call, following
the pattern of `requestType` / `setRequestType`:

```ts
interface FiltersState {
  // ...existing fields...
  status: string
  setStatus: (status: string) => void
}

export const useFilters = create<FiltersState>((set) => ({
  // ...existing fields...
  status: 'All',
  setStatus: (status) => set({ status }),
}))
```

**2. Teach `filterSql` about it.**  Same file.  Add a `status` parameter after
`yearRange`, and a clause for it after the existing `requestType` clause:

```ts
export function filterSql(
  requestType: string,
  { start, end }: YearRange,
  status: string,
  prefix = '',
): string {
  // ...existing clauses...
  if (status !== 'All') {
    clauses.push(`${prefix}status = '${status.replaceAll("'", "''")}'`)
  }
  return clauses.join(' AND ')
}
```

Save, and TypeScript flags every caller of `filterSql` — there are four, in
`src/pages/OverviewPage.tsx` and `src/pages/MapPage.tsx`.  That is exactly the
list of places the new filter has to reach.

**3. Update the callers.**  In each of those two files, read `status` from the
store and pass it through:

```ts
// OverviewPage.tsx
const { requestType, yearRange, status } = useFilters()
const where = filterSql(requestType, yearRange, status)
const whereAllTypes = filterSql('All', yearRange, status)
```

```ts
// MapPage.tsx — `status` joins the existing useFilters() destructure, and both
// filterSql calls gain it before the 'r.' prefix:
filterSql(requestType, yearRange, status, 'r.')
```

**4. Add the picker.**  In `src/App.tsx`, read `status` and `setStatus` from
`useFilters()` alongside the existing fields, then query the options.  Options
always come from the data, never from a hardcoded list.  Vacant-building
reports have a `NULL` status (see `data/dictionary/reqs_311.json`), so leave
those out:

```tsx
const { data: statusRows } = useQuery<{ status: string }>(
  'SELECT DISTINCT status FROM reqs_311 WHERE status IS NOT NULL ORDER BY status',
)
const statuses = ['All', ...(statusRows ?? []).map((r) => r.status)]
```

Then add the picker right after the `<RangeSlider ... />`, inside the same
controls `<div>`:

```tsx
<Picker label="Status" selectedKey={status} onSelectionChange={(key) => setStatus(String(key))}>
  {statuses.map((s) => (
    <Item key={s}>{s}</Item>
  ))}
</Picker>
```

Save.  A Status picker appears; choose **Open** and the stat tiles, the trend
chart, and the map all update together.  (The **Completed** tile drops to 0%
— every request in view is open.)

The SQL tab is the one exception: it runs whatever you type, so the global
filters do not apply there.

---

## Step 5: Add a Tab (Agent Task)

Adding a full tab is a good task to hand to an LLM.  Prepare two files:

- `AGENTS.md` — the hard rules for this codebase (no backend, Spectrum-only
  components, query via `useQuery`, etc.)
- `data/dictionary/<name>.json` — the schema of the dataset you want to query

Then prompt your agent:

> Read `dashboard/AGENTS.md` and `dashboard/data/dictionary/reqs_311.json`.
> Create `dashboard/src/pages/StatusTab.tsx` that shows a line chart of monthly
> request counts broken down by `status`.  Add it as a new tab in
> `dashboard/src/App.tsx`.

The agent has everything it needs: the rules, the column types, the patterns
from `OverviewPage.tsx` and `MapPage.tsx`, and the `useQuery` / `PlotFigure`
primitives.

After the agent writes the files:

1. Check the dev server — the new tab should appear immediately.
2. Run `make dashboard-build` to make sure TypeScript compiles cleanly.

---

## Step 6: Ship

Push to `main`:

```bash
git add dashboard/
git commit -m "feat: update dashboard"
git push origin main
```

GitHub Actions runs automatically:

1. Pulls data from Box via `scripts/pull_data.py` (fails fast if total exceeds
   150 MB).
2. Runs `npm ci && npm run build`.
3. Runs the Playwright smoke tests (all three tabs render; the filter
   changes the numbers).
4. Deploys to Cloudflare Pages: `https://<slug>-dashboard.pages.dev`.

The deploy step is skipped on pull requests — PRs only build and test.

> **One-time setup required** before the first deploy.  Ask your mentor to
> follow the Cloudflare and Box setup steps in the project-root `PROJECT_SETUP.md`.

---

## Quick Reference

### Commands

| Command | What it does |
|---|---|
| `make dashboard-install` | Install Node dependencies |
| `make dashboard-dev` | Dev server at localhost:5173 |
| `make dashboard-build` | Production build to `dist/` |
| `make dashboard-data` | Pull parquet files from Box |
| `npm run test:e2e` | Playwright smoke tests (needs Node + one-time `npx playwright install --with-deps chromium`; in docker=yes projects, CI runs these for you) |

### Where things live

| Path | Purpose |
|---|---|
| `src/pages/` | One file per tab |
| `src/store/filters.ts` | Cross-tab filter state (Zustand) + `filterSql()` |
| `src/lib/duckdb.ts` | DuckDB-wasm singleton and query helper |
| `src/lib/useQuery.ts` | React hook wrapping the query helper |
| `src/components/PlotFigure.tsx` | Observable Plot → React wrapper |
| `data/dictionary/` | Per-dataset schema JSON + Markdown |
| `data.manifest.json` | Box URLs for remote datasets |
| `public/data/` | Local parquet files (git-ignored; pulled from Box) |

### Useful links

- [Observable Plot docs](https://observablehq.com/plot/)
- [React Spectrum components](https://react-spectrum.adobe.com/react-spectrum/)
- [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
- [DuckDB-wasm](https://duckdb.org/docs/api/wasm/overview)
- [Clinic coding standards](https://github.com/dsi-clinic/the-clinic/blob/main/coding-standards/coding-standards.md)

---

## What to Do Next

- **Explore the 311 data.** Use the **SQL** tab to run queries live against
  the parquet views — it is the fastest way to prototype the SQL for a new
  chart before writing any code.
- **Export your first real dataset.** Run `dashboard_export.py` on a DataFrame
  from your pipeline and add it to the manifest.
- **Hand a tab to an LLM.** Follow Step 5 with your real data dictionary and
  see how quickly a new visualization comes together.
- **Ask your mentor** if you need help with the one-time Cloudflare or Box
  setup, or if the CI deploy step fails.
