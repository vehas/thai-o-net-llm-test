def main():
    import pandas as pd
    try:
        df = pd.read_parquet("external/snapshot.parquet")
        print("First 5 rows of the dataset:")
        print(df.head(5))
    except Exception as e:
        print(f"Error reading the parquet file: {e}")


if __name__ == "__main__":
    main()
