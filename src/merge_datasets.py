"""
Merges multiple CSV datasets using pandas.
"""

import pandas as pd
from pathlib import Path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Merge datasets.")

    parser.add_argument(
        "--input_csvs",
        type=Path,
        help="Input CSVs.",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--suffixes",
        type=str,
        help="List of suffixes appended to the column names of each dataframe. "
        "Should have len(input_csvs).",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--on",
        type=str,
        help="Column to merge on.",
        required=True,
        nargs="+",
    )
    parser.add_argument(
        "--output_path",
        type=Path,
        help="Output path.",
        required=True,
    )
    parser.add_argument(
        "--keep_from_first",
        type=str,
        nargs="+",
        help="Keeps the values for this column only from the first dataframe",
    )
    parser.add_argument(
        "--reorder_columns",
        type=str,
        nargs="+",
        help="Reorders the columns according to the specified identifiers. All others remain identical.",
    )

    args = parser.parse_args()

    keep_from_first = (
        args.keep_from_first if args.keep_from_first is not None else []
    )

    dfs = []
    keep_col_name = args.on + keep_from_first
    assert len(args.input_csvs) == len(args.suffixes)
    for i, (input_csv, suffix) in enumerate(
        zip(args.input_csvs, args.suffixes)
    ):
        df = pd.read_csv(input_csv).reset_index()
        # drop index
        if "index" in df.columns:
            df = df.drop(columns=["index"])
        if keep_from_first is not None and i > 0:
            df = df.drop(columns=keep_from_first)
        df.columns = [
            col if col in keep_col_name else col + "." + suffix
            for col in df.columns
        ]
        dfs.append(df)

    out_df = dfs[0]
    for df in dfs[1:]:
        out_df = pd.merge(out_df, df, on=args.on, how="outer").sort_values(
            by=args.on
        )
    if args.reorder_columns is not None:
        all_columns = out_df.columns
        reordered_columns = args.reorder_columns + [
            col for col in all_columns if col not in args.reorder_columns
        ]
        out_df = out_df[reordered_columns]
    out_df.to_csv(args.output_path, index=False)
