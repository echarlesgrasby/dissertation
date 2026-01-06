# AUTHOR:
#       Eric C. Grasby
# DATE:
#       2025-10-29
# PURPOSE:
#       This script is part of my dissertation work (specifically chapter 3).
#       This script reads Likert-scale questions from the responses database and calculates an ultimate consensus score (and prints the results out in a cross-tab)
# INVOCATION:
#       Call this script directly from the command line, and ensure that the results database exists in the same directory as this script

import pandas as pd
import sqlite3 as sql

database_file = "delphi-study-post-process-egrasby.db"

def calc_consensus_label(iqr):
    """
    Calculates a consensus label based on the IQR score and applies this back to the summary dataframe
    """
    if iqr <= 1:
        return "High"
    elif iqr == 2:
        return "Moderate"
    else:
        return "Low"
    

# Fetch input data!     
likert_question_query = """
SELECT 
	 case when q.question_id = '30' then 'MC11'
          when q.question_id = '31' then 'MC12'
          when q.question_id = '32' then 'MC13'
          when q.question_id = '33' then 'MC14'
          when q.question_id = '34' then 'MC15'
      end as question_id
	 ,r.response_text 
FROM QUESTIONS q
INNER JOIN RESPONSES r
ON q.question_id = r.question_id
WHERE r.question_id in ('30','31','32','33','34')
"""

likert_df = pd.read_sql(likert_question_query, sql.connect(database_file))
likert_df.columns = ["QUESTION_ID", "RESPONSE"]
likert_df["RESPONSE"] = likert_df["RESPONSE"].astype("Int64")


# Calculate normal five-number summary
std_5_num_summary = likert_df\
.groupby("QUESTION_ID")\
["RESPONSE"]\
.agg([
    'median'
    ,'mean'
    ,'std'
    ,'min'
    ,'max'
]).round(2)

# Calculate the interquartile range
std_5_num_summary["IQR"] = (
    likert_df.groupby("QUESTION_ID")["RESPONSE"].quantile(0.75) -
    likert_df.groupby("QUESTION_ID")["RESPONSE"].quantile(0.25)
)

# Apply consensus label
std_5_num_summary["Gen Consensus"] = std_5_num_summary["IQR"].apply(calc_consensus_label)


print(std_5_num_summary)


"""
$ python process_likert_responses_round_2.py
             median  mean   std  min  max  IQR Gen Consensus
QUESTION_ID
MC11            4.0  3.91   1.3    1    5  2.0      Moderate
MC12            4.0  3.73  0.65    3    5  1.0          High
MC13            4.0  4.09  0.94    2    5  1.0          High
MC14            4.0  3.91  0.94    2    5  1.0          High
MC15            4.0  4.27   0.9    2    5  1.0          High

"""
