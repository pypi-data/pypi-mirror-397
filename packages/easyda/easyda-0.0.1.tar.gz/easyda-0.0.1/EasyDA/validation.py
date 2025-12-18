def validate_csv(df):
    print("\n EASYDA : CSV VALIDATION\n")

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    if df.shape[0] < 10:
        print(" Very small dataset")

    if df.select_dtypes(include="number").empty:
        print(" No numeric columns detected")

    if df.isnull().mean().max() > 0.5:
        print(" High missing values in some columns")

    print("\n Validation complete\n")
