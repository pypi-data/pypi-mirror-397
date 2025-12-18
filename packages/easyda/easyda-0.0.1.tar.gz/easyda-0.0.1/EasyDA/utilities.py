import pandas as pd

def load_csv(path):
    return pd.read_csv(path)


def head(df, n=5):
    
    print(f"\n First {n} rows:")
    print(df.head(n))


def tail(df, n=5):
    
    print(f"\n Last {n} rows:")
    print(df.tail(n))


def sample(df, n=5, random_state=42):
    print(f"\n Sample of {n} rows:")
    print(df.sample(n=n, random_state=random_state))


def columns(df):
    print("\n Columns names are:")
    print(df.columns.tolist())


def null_rows(df):
    null_rows = df[df.isnull().any(axis=1)]

    print("\n🔹 Rows Containing Null Values")

    if null_rows.empty:
        print(" No rows with null values found")
    else:
        print(f" Total rows with null values: {null_rows.shape[0]}")
        print(null_rows)

    return null_rows
