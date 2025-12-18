import pandas as pd

def na_summary(df):
    total = df.isnull().sum()
    percent = (total / len(df)) * 100

    summary = pd.DataFrame({
        "missing_count": total,
        "missing_percent": percent
    })

    summary = summary[summary.missing_count > 0].sort_values(
        by="missing_percent", ascending=False
    )

    print("\n Missing Value Summary :")
    print(summary)
    return summary