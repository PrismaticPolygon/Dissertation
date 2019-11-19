# What is this repo?

This repo supports my main dissertation repo. It is intended to output my machine learning data
in several CSVs.

## `download.py`

Peter Hicks has thoughtfully been archiving TRUST messages since 2017-03-03. `download.py` retrieves
these files between 2018-4-1 and 2019-4-1 (the UK financial year). This period was chosen because:
* The ORR publishes station usage data in this range
* NR publishes historic delay attribution data in this range

Each file contains a day's worth of TRUST messages. TRUST broadcasts either every 5 seconds or when there are
32 messages to be distributed. Each file is a compressed JSON in which every line is an array of these messages, and
is at maximum 16KB.

## `extract.py`

This decompresses the files and puts them into a sensible structure in `extracted`. Each day contains at maximum 1440 files:
one for each minute. Each minute is at maximum 350KB of data; each day is about half a GB. This takes a great deal of time.

## `merge.py`

This combines the files by message key into monolithic CSVs in `data`. This is the final output
that my model will be trained on. This, again, is a time-consuming process, roughly 30s per file.

## Errors

An error occurs on extracting 2018-08-03.tbz2: `Compressed file ended before the end-of-stream marker was reached`