import numpy as np
import uuid
import re
from datetime import datetime as dt, timedelta
from pandas.tseries.holiday import USFederalHolidayCalendar


def generate_sales_data(
    n_rows: int,
    base_demand: int = 1000,
    day_range: int = 100,
    seed: int = 123456789
):
  # Create empty list to store records
  records = []
  np.random.seed(seed)

  # Generate dates
  date_offsets = np.random.uniform(1, day_range, n_rows)
  dates = [dt.now() - timedelta(days=int(offset)) for offset in date_offsets]
  dates.sort()
  holidays = USFederalHolidayCalendar().holidays(start=dates[0], end=dates[-1])

  # Generate features for each row
  for i in range(n_rows):
    date_val = dates[i]
    record = {
      'row_id': str(uuid.uuid4()),
      'date': date_val.date(),
      'average_temperature': round(np.random.uniform(0, 35), 1),
      'rainfall': round(np.random.exponential(5), 1),
      'weekend': date_val.weekday() >= 5,
      'holiday': str(date_val.date()) in holidays,
      'price_per_kg': round(np.random.uniform(0.5, 3), 2),
      'demand': round(np.random.uniform(1, base_demand), 1),
      'month': date_val.month,
    }
    record['total_spend'] = round(record['demand'] * record['price_per_kg'], 2)
    records.append(record)
  
  return records


def to_valid_table_name(
    raw: str, 
    max_length: int = 128
  ):
    if raw is None:
        raw = ''

    # Convert to lowercase and replace invalid chars with underscore (anything not a-z, 0-9, or _)
    name = raw.lower()
    name = re.sub(r'[^a-z0-9_]', '_', name)
    
    # Collapse multiple underscores
    name = re.sub(r'_+', '_', name)
    
    # Ensure non-empty
    if not name:
        name = 't'
      
    # Ensure it does not start with a digit
    if re.match(r'^[0-9]', name):
        name = 't_' + name
      
    # Enforce max length
    name = name[:max_length]
    
    # In case trimming leaves trailing underscore
    name = name.strip('_')
    
    # Ensure non-empty again
    if not name:
        name = 't'
      
    return name
