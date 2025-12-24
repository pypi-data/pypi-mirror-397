# data-generator-utils

Utility functions for generating synthetic retail sales data and creating valid table names for use in databases and analytics tools.

## Installation

`pip install data-generator-utils`


## Requirements

- Python 3.9+
- numpy
- pandas (for the holiday calendar utilities)

These are installed automatically when you install the package.

## Usage

### 1. Generate synthetic sales data

The `generate_sales_data` function returns a list of dictionaries, each representing a row of simulated sales data.

```
from data_generator import generate_sales_data

records = generate_sales_data(
n_rows=10_000, # number of rows to generate
base_demand=1000, # upper bound for demand
day_range=100, # how many days back from now to sample
seed=123456789 # RNG seed for reproducibility
)
```


#### Output schema

Each record has the following fields:

- `row_id`: Random UUID string.
- `date`: Calendar date (Python `date`) within the last `day_range` days.
- `average_temperature`: Random float between 0 and 35 (degrees, arbitrary units).
- `rainfall`: Random float from an exponential distribution with mean ≈ 5.
- `weekend`: Boolean flag indicating whether `date` falls on Saturday or Sunday.
- `holiday`: Boolean flag indicating whether `date` is a US federal holiday (via `USFederalHolidayCalendar`).
- `price_per_kg`: Random float between 0.5 and 3.0.
- `demand`: Random float between 1 and `base_demand`.
- `month`: Integer month extracted from `date`.
- `total_spend`: `demand * price_per_kg`, rounded to 2 decimal places.

### 2. Generate valid table names

The `to_valid_table_name` function converts an arbitrary string into a safe, normalized table name.

```
from data_generator import to_valid_table_name

raw = "2024 Sales Report (US-West)"
safe = to_valid_table_name(raw)

print(safe) # e.g. "t_2024_sales_report_us_west"
```


#### Rules applied

- Converts the input to lowercase.
- Replaces any character not in `a–z`, `0–9`, or `_` with `_`.
- Collapses multiple underscores into a single underscore.
- Ensures the name is non-empty; falls back to `"t"` if needed.
- Ensures the name does **not** start with a digit; prefixes with `"t_"` if it does.
- Truncates to `max_length` characters (default `128`).
- Strips leading/trailing underscores; if stripping empties the name, falls back to `"t"` again.


## Development

- Format code with your preferred formatter (e.g., `black`).
- Run tests (if added) before publishing a new version.
- When updating behavior of public functions, bump the package version accordingly.