# Personal Expense Intelligence Analyzer

Lightweight Flask app that uploads an expense CSV and returns spending summaries, category analysis, monthly trends, charts, and simple savings suggestions.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Start the app with `python app.py`.
4. Upload a CSV with `date`, `amount`, and `description`, plus optional `category`.

## CSV format

The analyzer expects these columns:

- `date`
- `amount`
- `description`
- `category` optional

## Notes

- Missing categories are inferred from the transaction description.
- Charts are rendered with matplotlib and saved under `static/charts`.