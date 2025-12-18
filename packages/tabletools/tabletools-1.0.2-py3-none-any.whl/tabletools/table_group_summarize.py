#!/usr/bin/env python

"""
Groups the entries of the input table file, essentially a csv file, and
summarizes the requested columns. The output summary columns are named by
concatenating the column name with the function name and an "_" in between
e.g. score_mean.
"""

import sys
import argparse 
import pandas as pd


def get_input_file_object(filename):
    """
    Returns a file objects that reads from filename or from STDIN if filename
    is -
    """
    if filename == "-":
        return sys.stdin
    return open(filename, "r")


def parse_args(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-t", "--table", required=True, default='-',
                        help="Input csv file; STDIN if - (default: %(default)s)")
    parser.add_argument("-g", "--groupby", required=True, nargs='+',
                        help="Name of column/s to group entries by")
    parser.add_argument("-y", "--summarize", required=True, nargs='+',
                        help="Name of column to summarize")
    parser.add_argument("-f", "--func", required=True, nargs='+',
                        help="Pandas function/s to summarize columns e.g. mean")
    parser.add_argument("-s", "--sep", default='\t',
                        help="Column separator (default: <TAB>)")
    parser.add_argument("-n", "--nativecols", action='store_true',
                       help="Summarized column names will not change. Only valid when single functions are used")
    return parser.parse_args(args)


def group_summarize(df, groupby, functions, summarize_cols, nativecols=False):
    # Group and summarize the data.
    summarize_dict = {}
    for col in summarize_cols:
        summarize_dict[col] = functions
    grouped = df.groupby(groupby).agg(summarize_dict)
    newcols = []
    for col in summarize_cols:
        if nativecols == False:
            for f in functions:
                newcols.append(col+'_'+f)
        elif nativecols == True:
            if len(functions) > 1:
                raise ValueError("If more than one function is specified column names must be changed")
            else:
                newcols.append(col)
    grouped.columns = newcols
    grouped = grouped.reset_index()
    return(grouped)


def main():
    args = parse_args(sys.argv[1:])

    # Flatten the groupby and func options. They were lists of lists.
    groupby = args.groupby
    functions = args.func
    summarize_cols = args.summarize
    nativecols = args.nativecols

    # Read the data.
    table = get_input_file_object(args.table)
    df = pd.read_csv(table, sep=args.sep)

    # Group and summarize the data.
    grouped = group_summarize(df, groupby, functions, summarize_cols, 
                              nativecols=nativecols)

    # Output grouped dataset.
    grouped.to_csv(sys.stdout, sep=args.sep, index=False)

if __name__ == "__main__":
    main()
