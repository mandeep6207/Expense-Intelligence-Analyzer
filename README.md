# Personal Expense Intelligence Analyzer

A lightweight Flask web application that analyzes personal expense data from CSV files and provides spending summaries, category breakdowns, monthly trends, interactive charts, and practical savings suggestions.

## Features

- 📊 **Smart Analytics**: Automatic spending analysis and pattern detection
- 🏷️ **Auto-Categorization**: Intelligently categorizes transactions based on descriptions
- 📈 **Visual Charts**: Beautiful matplotlib-generated category and trend charts
- 💡 **Actionable Insights**: AI-powered spending analysis and recommendations
- 🚀 **Fast Processing**: Efficient pandas-based data processing
- 🔒 **Secure**: File validation and safe file handling

## Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mandeep6207/Expense-Intelligence-Analyzer.git
   cd Expense-Intelligence-Analyzer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. Start the Flask application:
   ```bash
   python app.py
   ```

6. Open your browser and visit: `http://localhost:5000`

## CSV Format

The analyzer expects a CSV file with the following columns:

| Column | Required | Description |
|--------|----------|-------------|
| `date` | ✅ | Transaction date (e.g., 2024-01-15) |
| `amount` | ✅ | Transaction amount (numeric) |
| `description` | ✅ | Transaction description |
| `category` | ❌ | Transaction category (auto-inferred if missing) |

### Example CSV

```csv
date,amount,description,category
2024-01-01,25.50,Coffee Shop,
2024-01-02,150.00,Grocery Shopping,Food
2024-01-03,50.00,Uber Ride,
2024-01-04,1200.00,Monthly Rent,Bills
```

## Auto-Categorization

The app automatically categorizes transactions if the `category` column is empty. Categories are inferred using keywords:

- **Food**: grocery, restaurant, coffee, lunch, dinner, etc.
- **Transport**: uber, taxi, fuel, bus, train, etc.
- **Shopping**: amazon, store, mall, clothes, etc.
- **Travel**: flight, hotel, airbnb, vacation, etc.
- **Bills**: rent, electricity, water, internet, insurance, etc.
- **Entertainment**: movie, game, netflix, spotify, concert, etc.
- **Health**: doctor, pharmacy, hospital, medical, etc.

## Features Explained

### Category Breakdown
Visualizes total spending per category with an interactive bar chart and detailed table.

### Monthly Trend
Shows spending patterns over time with a line chart and monthly totals.

### Smart Insights
AI-generated recommendations including:
- Spending concentration alerts
- Cost reduction suggestions
- Anomaly detection for large transactions

### Wasteful Spending Detection
Identifies top spending categories above the median threshold for targeted savings.

## Project Structure

```
.
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── README.md             # This file
├── static/
│   ├── css/
│   │   └── style.css     # Application styling
│   └── charts/           # Generated chart images (auto-created)
├── templates/
│   ├── base.html         # Base HTML template
│   └── index.html        # Main application page
├── uploads/              # Uploaded CSV files (auto-created)
└── utils/
    ├── __init__.py
    └── analysis.py       # Core expense analysis logic
```

## Configuration

Environment variables can be set in `.env` file:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=False
MAX_UPLOAD_SIZE_MB=16
LOG_LEVEL=INFO
```

## Logging

The application includes comprehensive logging for debugging:
- File upload validation
- Analysis progress
- Error tracking

Logs appear in the console output when running the app.

## Troubleshooting

### "Only CSV files are supported"
Ensure your file has a `.csv` extension and is a valid CSV format.

### "Missing required columns"
Your CSV must have `date`, `amount`, and `description` columns.

### "Unable to analyze the file"
Check the file format and ensure all date values are valid.

## Technologies Used

- **Flask**: Web framework
- **Pandas**: Data processing and analysis
- **Matplotlib**: Chart generation
- **NumPy**: Numerical computations

## License

This project is open source and available under the MIT License.

## Support

For issues or suggestions, please open an issue on GitHub.

---

**Happy Expense Tracking!** 💰📊