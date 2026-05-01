import os
from datetime import datetime
from uuid import uuid4
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


ALLOWED_EXTENSIONS = {"csv"}
DEFAULT_CATEGORY = "Other"

CATEGORY_KEYWORDS = {
    "Food": ["food", "grocery", "grocer", "restaurant", "coffee", "lunch", "dinner", "cafe", "meal"],
    "Transport": ["uber", "taxi", "cab", "bus", "train", "fuel", "gas", "metro", "transport", "parking"],
    "Shopping": ["amazon", "shopping", "store", "mall", "clothes", "apparel", "fashion", "retail"],
    "Travel": ["flight", "hotel", "travel", "airbnb", "trip", "vacation", "tour", "booking"],
    "Bills": ["bill", "electric", "water", "internet", "rent", "phone", "subscription", "insurance"],
    "Entertainment": ["movie", "game", "stream", "concert", "music", "theater", "netflix", "spotify"],
    "Health": ["doctor", "pharmacy", "medical", "hospital", "health", "clinic", "medicine"],
}


def allowed_file(filename: str) -> bool:
    """Check if uploaded file has an allowed extension.
    
    Args:
        filename: The name of the uploaded file.
    
    Returns:
        True if file extension is in ALLOWED_EXTENSIONS, False otherwise.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_expenses(csv_path: str, static_folder: str) -> Dict:
    """Analyze expense CSV file and generate comprehensive report.
    
    Processes CSV file, auto-categorizes transactions, generates charts,
    and returns insights about spending patterns.
    
    Args:
        csv_path: Path to the uploaded CSV file.
        static_folder: Path to static folder for storing generated charts.
    
    Returns:
        Dictionary containing analysis results including spending totals,
        category breakdowns, monthly trends, and insights.
    
    Raises:
        ValueError: If CSV is missing required columns or has no valid data.
        FileNotFoundError: If CSV file does not exist.
        Exception: If file processing fails.
    """
    frame = load_and_clean_data(csv_path)
    frame = auto_categorize(frame)

    total_spending = float(frame["amount"].sum())
    category_breakdown = (
        frame.groupby("category", dropna=False)["amount"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    monthly_trend = build_monthly_trend(frame)
    if not category_breakdown.empty:
        top_category_row = category_breakdown.iloc[0]
        top_category = {
            "name": str(top_category_row["category"]),
            "amount": float(top_category_row["amount"]),
        }
    else:
        top_category = {"name": DEFAULT_CATEGORY, "amount": 0.0}

    insights = generate_insights(frame, category_breakdown)
    wasteful = detect_wasteful_spending(frame)

    chart_dir = os.path.join(static_folder, "charts")
    os.makedirs(chart_dir, exist_ok=True)
    chart_token = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid4().hex[:8]}"
    category_chart = os.path.join(chart_dir, f"category_breakdown_{chart_token}.png")
    trend_chart = os.path.join(chart_dir, f"monthly_trend_{chart_token}.png")

    create_category_chart(category_breakdown, category_chart)
    create_monthly_chart(monthly_trend, trend_chart)

    return {
        "row_count": int(len(frame)),
        "total_spending": total_spending,
        "category_breakdown": category_breakdown.to_dict(orient="records"),
        "monthly_trend": monthly_trend.to_dict(orient="records"),
        "top_category": top_category,
        "insights": insights,
        "wasteful_spending": wasteful.to_dict(orient="records"),
        "category_chart": os.path.relpath(category_chart, static_folder).replace(os.sep, "/"),
        "trend_chart": os.path.relpath(trend_chart, static_folder).replace(os.sep, "/"),
    }


def load_and_clean_data(csv_path: str) -> pd.DataFrame:
    """Load and validate CSV data with data cleaning.
    
    Validates required columns, handles missing values, removes invalid entries,
    and ensures data types are correct.
    
    Args:
        csv_path: Path to the CSV file.
    
    Returns:
        Cleaned DataFrame with validated date, amount, description, and category columns.
    
    Raises:
        ValueError: If required columns are missing from CSV.
        FileNotFoundError: If CSV file does not exist.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    
    try:
        frame = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        raise ValueError("CSV file is empty")
    except Exception as exc:
        raise ValueError(f"Failed to read CSV file: {exc}")

    frame.columns = [column.strip().lower() for column in frame.columns]
    required_columns = {"date", "amount", "description"}
    missing_columns = required_columns - set(frame.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

    if "category" not in frame.columns:
        frame["category"] = ""

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["amount"] = pd.to_numeric(frame["amount"], errors="coerce")
    frame["description"] = frame["description"].fillna("").astype(str)
    frame["category"] = frame["category"].fillna("").astype(str)

    # Log rows with invalid dates or amounts
    invalid_rows = frame[frame["date"].isna() | frame["amount"].isna()]
    if not invalid_rows.empty:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"Dropping {len(invalid_rows)} rows with invalid date or amount")

    frame = frame.dropna(subset=["date", "amount"])
    frame = frame[frame["amount"] > 0].copy()
    frame["category"] = frame["category"].str.strip()
    frame["description"] = frame["description"].str.strip()

    if frame.empty:
        raise ValueError("No valid expense records found in CSV after validation")

    return frame


def auto_categorize(frame: pd.DataFrame) -> pd.DataFrame:
    """Auto-categorize transactions based on description keywords.
    
    Infers missing categories by matching transaction descriptions
    against predefined keyword lists. Uncategorized items default to 'Other'.
    
    Args:
        frame: DataFrame with transaction data.
    
    Returns:
        DataFrame with categorized transactions.
    """
    frame = frame.copy()

    def infer_category(row: pd.Series) -> str:
        current = str(row.get("category", "")).strip()
        if current:
            return current.title()
        text = f"{row.get('description', '')}".lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return category
        return DEFAULT_CATEGORY

    frame["category"] = frame.apply(infer_category, axis=1)
    return frame


def build_monthly_trend(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate spending by month for trend analysis.
    
    Args:
        frame: DataFrame with transaction data.
    
    Returns:
        DataFrame with monthly totals sorted by month.
    """
    trend = frame.copy()
    trend["month"] = trend["date"].dt.to_period("M").astype(str)
    return trend.groupby("month", as_index=False)["amount"].sum().sort_values("month")


def detect_wasteful_spending(frame: pd.DataFrame) -> pd.DataFrame:
    """Identify top spending categories above median threshold.
    
    Args:
        frame: DataFrame with categorized transaction data.
    
    Returns:
        DataFrame with top 3 categories above median threshold.
    """
    category_totals = frame.groupby("category", as_index=False)["amount"].sum()
    if category_totals.empty:
        return category_totals

    threshold = category_totals["amount"].median()
    wasteful = category_totals[category_totals["amount"] >= threshold].sort_values("amount", ascending=False)
    return wasteful.head(3)


def generate_insights(frame: pd.DataFrame, category_breakdown: pd.DataFrame) -> List[str]:
    """Generate actionable spending insights from expense data.
    
    Args:
        frame: Complete transaction DataFrame.
        category_breakdown: Category totals from analysis.
    
    Returns:
        List of up to 4 insight strings with spending recommendations.
    """
    insights: List[str] = []

    if category_breakdown.empty:
        return ["No valid spending rows were found in the file."]

    top_category = category_breakdown.iloc[0]
    total_spending = float(frame["amount"].sum())
    top_share = float(top_category["amount"]) / total_spending if total_spending else 0.0

    if top_share >= 0.35:
        insights.append(f"You are spending too much on {top_category['category'].lower()}.")
    else:
        insights.append(f"Your highest spending is in {top_category['category'].lower()}.")

    if len(category_breakdown) > 1:
        runner_up = category_breakdown.iloc[1]
        if float(top_category["amount"]) > float(runner_up["amount"]) * 1.4:
            insights.append(f"Reduce {top_category['category'].lower()} expenses by 20% to save more.")

    mean_amount = float(frame["amount"].mean())
    if mean_amount > 0 and frame["amount"].max() > mean_amount * 5:
        insights.append("There are a few unusually large transactions worth reviewing.")

    return insights[:4]


def create_category_chart(category_breakdown: pd.DataFrame, output_path: str) -> None:
    """Generate and save category spending bar chart.
    
    Args:
        category_breakdown: DataFrame with category totals.
        output_path: Path where chart PNG will be saved.
    """
    plt.figure(figsize=(9, 5))
    categories = category_breakdown["category"].astype(str).tolist()
    amounts = category_breakdown["amount"].astype(float).tolist()
    plt.bar(categories, amounts, color="#1f77b4")
    plt.title("Category-wise Spending")
    plt.xlabel("Category")
    plt.ylabel("Amount")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()


def create_monthly_chart(monthly_trend: pd.DataFrame, output_path: str) -> None:
    """Generate and save monthly spending trend line chart.
    
    Args:
        monthly_trend: DataFrame with monthly totals.
        output_path: Path where chart PNG will be saved.
    """
    plt.figure(figsize=(9, 5))
    months = monthly_trend["month"].astype(str).tolist()
    amounts = monthly_trend["amount"].astype(float).tolist()
    plt.plot(months, amounts, marker="o", color="#2ca02c", linewidth=2)
    plt.title("Monthly Spending Trend")
    plt.xlabel("Month")
    plt.ylabel("Amount")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()