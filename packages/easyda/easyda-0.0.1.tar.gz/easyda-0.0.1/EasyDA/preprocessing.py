import pandas as pd

def suggest_preprocessing(df, target):

    print("\n================ EASYDA : PREPROCESSING SUGGESTIONS ================\n")

    # ---------------- Target Check ----------------
    if target not in df.columns:
        print(f" Target column '{target}' not found")
        return

    target_dtype = df[target].dtype
    unique_target = df[target].nunique()

    print(" Target Analysis:")
    if target_dtype in ["int64", "float64"] and unique_target > 10:
        print(" Problem Type: Regression")
    else:
        print(" Problem Type: Classification")

    # ---------------- Drop Suggestions ----------------
    print("\n Columns to Consider Dropping:")
    drop_cols = []
    for col in df.columns:
        if "id" in col.lower():
            drop_cols.append(col)

    if drop_cols:
        print(" ID Columns:", drop_cols)
    else:
        print(" No obvious ID columns")

    # ---------------- Missing Values ----------------
    print("\n Missing Value Handling:")
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print(" No missing values")
    else:
        for col in missing.index:
            if df[col].dtype == "object":
                print(f" {col}: use MODE")
            else:
                print(f" {col}: use MEAN or MEDIAN")

    # ---------------- Duplicate Rows ----------------
    print("\n Duplicate Value Check:")

    dup_count = df.duplicated().sum()

    if dup_count > 0:
        print(f" Duplicate rows found: {dup_count}")
        print(" Suggested: remove using df.drop_duplicates()")
    else:
        print(" No duplicate rows found")

    # ---------------- Encoding ----------------
    print("\n Encoding Required For:")
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if cat_cols:
        print(" Categorical Columns:", cat_cols)
        print(" Suggested: Encoding Required")
    else:
        print(" No categorical columns")

    # ---------------- Scaling ----------------
    print("\n Feature Scaling:")
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    num_cols = [col for col in num_cols if col != target]

    if num_cols:
        print(" Numeric Columns:", num_cols)
        print(" Suggested: StandardScaler / MinMaxScaler")
    else:
        print(" No numeric features to scale")

    # ---------------- Outlier Warning ----------------
    print("\n Outlier Check (IQR Method):")

    outlier_cols = []

    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower) | (df[col] > upper)]

        if not outliers.empty:
            outlier_cols.append(col)
            print(f" {col}: {len(outliers)} potential outliers")

    if not outlier_cols:
        print(" No significant outliers detected")

        
    print("\n================ END OF SUGGESTIONS ==================\n")
