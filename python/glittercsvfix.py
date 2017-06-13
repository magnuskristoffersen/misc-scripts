""" Reformat Glitter data"""

import os
import time
from glob import glob
import csv
import linecache
import pandas as pd


def list_files(path, ext):
    """Find files recursively."""
    files = [y for x in os.walk(path) for y in glob(os.path.join(x[0], ext))]
    for f in files:
        if 'fixed' not in f:
            glittercsvfix(f)


def glittercsvfix(infile):

    comblist_mdl = list()
    comblist_nomdl = list()
    lines = list()

    filepath, ext = os.path.splitext(infile)
    outfile_mdl = filepath + '_mdl-filtered' + '-fixed' + ext
    outfile_nomdl = filepath + '_not-mdl-filtered' + '-fixed' + ext
    outfile_detlim = filepath + '_min-det-lim-99%' + '-fixed' + ext
    outfile_chondrite = filepath + '_chondrite' + '-fixed' + ext

    if linecache.getline(infile, 8) == ('GLITTER!: Trace Element '
                                        'Concentrations MDL filtered.\n'):
        FIRST_SPLIT_TEXT = ('GLITTER!: Trace Element Concentrations MDL '
                            'filtered.\n')
        SECOND_SPLIT_TEXT = ('GLITTER!: Trace Element Concentrations, Not '
                             'filtered for MDL.\n')
        THIRD_SPLIT_TEXT = ('GLITTER!: 1 sigma error.' + '\n')
        FOURTH_SPLIT_TEXT = ('GLITTER!: Minimum detection limits '
                             '(99% confidence).\n')
        FIFTH_SPLIT_TEXT = ('GLITTER!: Trace element concentrations '
                            'normalised to chondrite.\n')
        SIXTH_SPLIT_TEXT = ('GLITTER!: Mean Raw CPS background NOT '
                            'subtracted.\n')
    else:
        print 'Error: %s is an unsupported file type' % (infile)
        return 0

    with open(infile, 'rU') as f:
        lines = list(f)

    firstend = 0
    secondend = 0
    thirdstart = 0
    thirdend = 0
    linecounter = 0

    for line in lines:
        if line == FIRST_SPLIT_TEXT:
            firstend = linecounter + 1
        if line == SECOND_SPLIT_TEXT:
            secondend = linecounter - 2
            thirdstart = linecounter + 1
        if line == THIRD_SPLIT_TEXT:
            thirdend = linecounter - 2
            fourthstart = linecounter + 1
        if line == FOURTH_SPLIT_TEXT:
            fourthend = linecounter - 2
            fifthstart = linecounter + 1
        if line == FIFTH_SPLIT_TEXT:
            fifthend = linecounter - 2
            sixthstart = linecounter + 1
        if line == SIXTH_SPLIT_TEXT:
            sixthend = linecounter - 2

        linecounter += 1
    secondpart = lines[8:secondend]
    thirdpart = lines[thirdstart:thirdend]
    fourthpart = lines[fourthstart:fourthend]
    fifthpart = lines[fifthstart:fifthend]
    sixthpart = lines[sixthstart:sixthend]

    secondpart = list(csv.reader(secondpart))
    thirdpart = list(csv.reader(thirdpart))
    fourthpart = list(csv.reader(fourthpart))
    fifthpart = list(csv.reader(fifthpart))
    sixthpart = list(csv.reader(sixthpart))

    fourthpart = zip(*fourthpart)
    fourthpart[0] = ['Element'] + ['1sigma'] * (len(fourthpart[0]) - 1)
    fourthpart = zip(*fourthpart)
    for i in range(0, len(secondpart)):
        comblist_mdl.append(secondpart[i])
        comblist_mdl.append(fourthpart[i])
        comblist_nomdl.append(thirdpart[i])
        comblist_nomdl.append(fourthpart[i])

    comblist_mdl = zip(*comblist_mdl[1:])
    comblist_nomdl = zip(*comblist_nomdl[1:])

    df_mdl = pd.DataFrame(comblist_mdl)
    df_nomdl = pd.DataFrame(comblist_nomdl)
    df_detlim = pd.DataFrame(zip(*fifthpart))
    df_chondrite = pd.DataFrame(zip(*sixthpart))
    df_mdl.to_csv(outfile_mdl, index=False, header=False)
    df_nomdl.to_csv(outfile_nomdl, index=False, header=False)
    df_detlim.to_csv(outfile_detlim, index=False, header=False)
    df_chondrite.to_csv(outfile_chondrite, index=False, header=False)

    print time.strftime('%Y-%d-%m %H:%M:%S'), ': Fixed', outfile_mdl
    print time.strftime('%Y-%d-%m %H:%M:%S'), ': Fixed', outfile_nomdl
    print time.strftime('%Y-%d-%m %H:%M:%S'), ': Fixed', outfile_detlim
    print time.strftime('%Y-%d-%m %H:%M:%S'), ': Fixed', outfile_chondrite


list_files('./', '*.csv')
