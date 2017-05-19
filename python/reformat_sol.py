import os
from datetime import datetime
from glob import glob
from shutil import copyfile
import csv
import codecs
import pandas as pd


def list_files(path, ext):
    """Find files recursively."""
    files = [y for x in os.walk(path) for y in glob(os.path.join(x[0], ext))]
    for f in files:
        if not 'reformatted' in f:
            reformat(f)

def reformat(infile):
    fp, ex = os.path.splitext(infile)
    usefile = fp + '-temp' + ex
    with open(infile, 'r') as f:
        data = f.read().splitlines(True)
        df = pd.DataFrame(list(csv.reader(data[2:])))
        
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    length = len(df['Type'].unique())
    index = [None] * length

    uni_type = list(df['Type'].unique())
    i = 0
    for ty in uni_type:
        uni_df = df.loc[(df.Type == ty)]
        index[i] = uni_df['Label'].iloc[0]
        i += 1

    elements = list(df['Element'].unique())
    sd = ['SD'] * len(elements)
    columns = [None] * (len(elements)+len(sd))
    columns[::2] = elements
    columns[1::2] = sd

    df2 = pd.DataFrame(index=index, columns=columns)
    df2.fillna('None')

    uni_type = list(df['Type'].unique())

    i = 0
    for uni in uni_type:
        uni_df = df.loc[(df.Type == uni)]
        conc = list(uni_df['Corr Conc'])
        sd = list(uni_df['SD'])
        results = [None] * (len(conc) + len(sd))
        results[::2] = conc
        results[1::2] = sd
        df2.iloc[i] = results
        i += 1

    now = datetime.now().strftime('%H%M-%d%m%y')
    filepath, ext = os.path.splitext(infile)
    filename = filepath + '-reformatted-' + now + ext
    df2.to_csv(filename)

list_files('./', '*.csv')
