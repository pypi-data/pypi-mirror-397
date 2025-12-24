import pandas as pd


class NotexaData:
    """
    Core data analytics object for Notexa.
    """

    def __init__(self, dataframe: pd.DataFrame, source: str = "unknown"):
        self.df = dataframe
        self.source = source

    def summary(self) -> dict:
        """
        Returns a high-level summary of the dataset.
        """
        return {
            "source": self.source,
            "rows": len(self.df),
            "columns": len(self.df.columns),
            "column_names": list(self.df.columns),
            "missing_values": int(self.df.isnull().sum().sum()),
        }

    def trends(self) -> dict:
        """
        Detects basic numeric trends (growth / drop).
        """
        trends = {}
        numeric_cols = self.df.select_dtypes(include="number")

        for col in numeric_cols.columns:
            series = numeric_cols[col].dropna()
            if len(series) < 2:
                continue

            start = series.iloc[0]
            end = series.iloc[-1]

            change_pct = ((end - start) / abs(start)) * 100 if start != 0 else 0

            trends[col] = {
                "start": float(start),
                "end": float(end),
                "change_percent": round(change_pct, 2),
            }

        return trends

    def insights(self) -> list:
        """
        Generates human-readable insights.
        """
        insights = []

        summary = self.summary()
        insights.append(f"Dataset contains {summary['rows']} rows and {summary['columns']} columns.")

        if summary["missing_values"] > 0:
            insights.append(f"Detected {summary['missing_values']} missing values.")

        trends = self.trends()
        for col, data in trends.items():
            pct = data["change_percent"]
            if pct > 10:
                insights.append(f"{col} increased by {pct}%.")
            elif pct < -10:
                insights.append(f"{col} decreased by {abs(pct)}%.")

        if not insights:
            insights.append("No significant trends detected.")

        return insights

    def preview(self, rows: int = 5):
        """
        Returns a preview of the dataset.
        """
        return self.df.head(rows)


def load(path: str) -> NotexaData:
    """
    Loads a dataset into Notexa.
    Supports CSV and JSON.
    """
    if path.endswith(".csv"):
        df = pd.read_csv(path)
    elif path.endswith(".json"):
        df = pd.read_json(path)
    else:
        raise ValueError("Unsupported file type. Use CSV or JSON.")

    return NotexaData(df, source=path)
