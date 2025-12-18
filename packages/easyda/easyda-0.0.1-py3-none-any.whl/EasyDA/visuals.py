import seaborn as sns
import matplotlib.pyplot as plt

def heatmap(df):

    corr = df.corr(numeric_only=True)

    plt.figure(figsize=(10, 6))
    sns.heatmap(
        corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        linewidths=0.5
    )
    plt.title("Correlation Heatmap")
    plt.show()

def pairplot(df):
    
    numeric_df = df.select_dtypes(include="number")

    if numeric_df.shape[1] == 0:
        print(" No numeric columns available for pairplot")
        return

    sns.pairplot(numeric_df)
    plt.show()