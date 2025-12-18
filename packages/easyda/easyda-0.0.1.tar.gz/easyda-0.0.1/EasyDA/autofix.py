import pandas as pd

def auto_fix(df, verbose=True):
    

    df = df.copy()   # ❗ original df is NOT modified
    report = []

    def log(msg):
        report.append(msg)
        if verbose:
            print(msg)

    if verbose:
        print("\n EASYDA : AUTO FIX MODE (MINIMAL)\n")


    for col in df.columns:
        missing = df[col].isnull().sum()
        if missing == 0:
            continue

        # Numeric → MEDIAN
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
            log(f" Filled {missing} missing values in '{col}' using MEDIAN")

        # Non-numeric → MODE
        else:
            mode = df[col].mode()
            fill_value = mode.iloc[0] if not mode.empty else "Unknown"
            df[col] = df[col].fillna(fill_value)
            log(f"Filled {missing} missing values in '{col}' using MODE")

    if verbose:
        print("\n AUTO FIX COMPLETE\n")

    return df, report
