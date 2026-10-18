"""Campaign response analysis for the skin clinic dataset."""
from pathlib import Path
import pandas as pd

DATA_PATH = Path(__file__).parent / "skin_clinic_campaign.csv"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Responded"] = (df["Response_to_Campaign"].str.strip().str.lower() == "yes").astype(int)
    df["Product_Usage"] = pd.cut(
        df["Unique_Products_Purchased"],
        bins=[0, 4, 8, float("inf")],
        labels=["1-4", "5-8", ">8"],
    )
    return df


def response_table(df: pd.DataFrame, col: str, order: list) -> pd.DataFrame:
    t = (
        df.groupby(col, observed=True)["Responded"]
        .agg(Customers="count", Responders="sum")
        .reindex(order)
    )
    t["Response Rate (%)"] = (t["Responders"] / t["Customers"] * 100).round(2)
    return t.reset_index()


def run_analysis() -> dict:
    df = load_data()
    return {
        "Gender vs Campaign Response": response_table(df, "Gender", ["Male", "Female"]),
        "Age Group vs Campaign Response": response_table(df, "AgeGroup", ["<30", "30-50", ">50"]),
        "Purchase in Last Quarter vs Campaign Response": response_table(df, "Purchase_Last_Quarter", ["Yes", "No"]),
        "Product Usage vs Campaign Response": response_table(df, "Product_Usage", ["1-4", "5-8", ">8"]),
        "_overall": round(df["Responded"].mean() * 100, 2),
        "_total": len(df),
    }


if __name__ == "__main__":
    res = run_analysis()
    print(f"Overall response rate: {res['_overall']}% of {res['_total']} customers\n")
    for name, table in res.items():
        if not name.startswith("_"):
            print(name)
            print(table.to_string(index=False), "\n")
