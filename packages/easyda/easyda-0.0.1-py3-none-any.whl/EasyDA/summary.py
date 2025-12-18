def basic_info(df):

    print("\n Shape:")
    print(df.shape)

    print("\n Columns:")
    print(df.columns.tolist())

    print("\n Data Types:")
    print(df.dtypes)

    print("\n Missing Values:")
    print(df.isnull().sum())

    print("\n Duplicate Values:")
    print(df.duplicated().sum())

    print("\n Statistical Summary:")
    print(df.describe(include="all"))


