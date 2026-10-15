# Delayed Discharges in Scotland: Power BI dashboard

An independent analysis of Public Health Scotland open data on people who are medically ready to leave hospital but are delayed, often while waiting for social care to be arranged. By Adeshina Ayodele.

**Source:** Public Health Scotland, *Delayed Discharges in NHSScotland*. Contains public sector information licensed under the Open Government Licence v3.0. This is independent work and is not endorsed by Public Health Scotland or the NHS.

## What's in this folder

| File | What it is |
| --- | --- |
| `data/fact_bed_days.csv` | Monthly bed days occupied by delayed discharges, by council area, age group and reason (Jul 2016 to Aug 2026) |
| `data/fact_census_delays.csv` | Number of people delayed on the monthly census day, by health board, age group and reason |
| `data/dim_date.csv` | One row per month, with year, financial year, days in month and a month index |
| `data/dim_council_area.csv` | Council area names, with their health and social care partnership and health board |
| `data/dim_health_board.csv` | Health board names |
| `data/dim_reason.csv` | The four reason groups, with plain-English descriptions |
| `data/dim_age_group.csv` | Age groups 18-74 and 75+ |
| `dax/measures.dax` | All the DAX measures, ready to copy into Power BI |
| `theme-engr-ayodele.json` | A navy and gold report theme matching the Engr Ayodele brand |

## How the data was prepared

* Downloaded from the Public Health Scotland open data portal (August 2026 release).
* Pre-calculated totals removed (the "All Delay Reasons", "18plus" and "Scotland" rows), so Power BI can never double-count. Totals are rebuilt with measures.
* Checked: the four reason groups add up exactly to the published totals, both age groups add up exactly to the 18+ total, and all council areas add up exactly to the published Scotland figure, for every month.
* Codes such as S12000038 replaced with names using the official PHS geography lookups. Bed days with no recorded council area are kept as "Not known", so the Scotland total stays correct.

## Build it in Power BI Desktop

### 1. Load the data
1. Open Power BI Desktop. **Home > Get data > Text/CSV**, and load each of the seven CSV files in `data/`.
2. In Power Query (**Transform data**), check the `Date` column in `fact_bed_days`, `fact_census_delays` and `dim_date` is type **Date**. Then **Close & Apply**.

### 2. Create the relationships (Model view)
Drag to connect these. All are many-to-one, single direction, from the fact table to the dimension:

| From | To |
| --- | --- |
| `fact_bed_days[Date]` | `dim_date[Date]` |
| `fact_bed_days[CouncilAreaCode]` | `dim_council_area[CouncilAreaCode]` |
| `fact_bed_days[ReasonGroup]` | `dim_reason[ReasonGroup]` |
| `fact_bed_days[AgeGroup]` | `dim_age_group[AgeGroup]` |
| `fact_census_delays[Date]` | `dim_date[Date]` |
| `fact_census_delays[HealthBoardCode]` | `dim_health_board[HealthBoardCode]` |
| `fact_census_delays[ReasonGroup]` | `dim_reason[ReasonGroup]` |
| `fact_census_delays[AgeGroup]` | `dim_age_group[AgeGroup]` |

Then tidy up:
* `dim_date[YearMonth]`: **Column tools > Sort by column > YearMonthSort**.
* `dim_reason[ReasonShort]`: sort by `SortOrder`.
* Hide the code columns and fact table keys from report view (right-click > Hide in report view).

### 3. Add the measures
**Home > Enter data**, name the table `_Measures`, click **Load**. Then add each measure from `dax/measures.dax` using **New measure**. Format: `Bed Days` as whole number with thousands separator; `Avg Daily Delayed Beds` with 0 decimals; the `%` measures as percentage with 1 decimal.

### 4. Apply the theme
**View > Themes > Browse for themes** and choose `theme-engr-ayodele.json`.

### 5. Build three pages

**Page 1: Scotland overview**
* Title: "Delayed discharges in Scotland", with a card showing `Latest Month Label`.
* Four KPI cards: `Avg Daily Delayed Beds (Latest Month)`, `Bed Days (Latest Month)`, `Bed Days YoY % (Latest Month)`, `Census Delays (Latest Month)`.
* Line chart: `dim_date[Date]` on the x-axis (continuous), `Bed Days` on the y-axis. Add text annotations for the April 2020 low (pandemic) and the October 2024 peak.
* Slicers: `dim_age_group[AgeGroup]`, `dim_reason[ReasonShort]`, `dim_date[FinancialYear]`.

**Page 2: Where**
* Clustered bar chart: `dim_council_area[CouncilArea]` with `Bed Days Rolling 12 Months`, sorted descending.
* Table: `dim_health_board[HealthBoard]` with `Census Delays (Latest Month)`.
* Slicer: `dim_council_area[HealthBoard]`, so users can focus on one area, such as NHS Greater Glasgow and Clyde.
* Note on the page: "Figures are counts, not rates. Larger areas will naturally have more delays."

**Page 3: Why**
* Donut or 100% bar: `dim_reason[ReasonShort]` with `Bed Days` for the latest month.
* Stacked area chart: `dim_date[Date]`, `Bed Days`, legend `dim_reason[ReasonShort]`, to show how the mix of reasons changes.
* Bar: `dim_age_group[AgeGroup]` with `Share of Bed Days by Age`.
* A tooltip or text box showing `dim_reason[Description]`, so viewers understand each reason.

On every page, add a small text box at the bottom with the `Source Note` measure (a card works).

### 6. Check your numbers
For August 2026 (all ages, all reasons), the dashboard should show:

| Measure | Expected |
| --- | --- |
| Bed Days (Latest Month) | 61,091 |
| Avg Daily Delayed Beds (Latest Month) | 1,971 |
| Bed Days YoY % (Latest Month) | +0.3% (August 2025: 60,888) |
| Census Delays (Latest Month) | 1,964 |

If these match, your model is correct.

## Key findings (August 2026 release)

* In August 2026, delayed discharges occupied **61,091 bed days**, an average of **1,971 hospital beds every day**, almost unchanged on August 2025 (+0.3%).
* **Health and social care reasons** account for **71%** of bed days. Adults with Incapacity cases (Code 9) account for a further **20%**.
* People aged **75 and over** account for **66%** of delayed bed days.
* Bed days fell sharply in **April 2020** (20,293) during the pandemic, then rose to a peak of **62,914 in October 2024**.

## Limitations

* Figures are raw counts. Comparing areas fairly needs population rates, for example bed days per 100,000 adults, using National Records of Scotland population estimates. This is a planned next step.
* Census figures are a snapshot on one day each month (the last Thursday) and cannot be added across months.
* Bed days are by council area of residence; census delays are by health board where the person was delayed. These are different bases, so don't compare them directly.
* Recent months may be revised by Public Health Scotland in later releases.
