import pandas as pd
import numpy as np


def filter_log(df_, rule):
    # select cases that satisfy the treatment conditions
    mask = 1
    for i in range(len(rule[0][1])):
        mask = mask & ((df_[rule[0][1][i][0]] == rule[0][1][i][1][0]) | (df_[rule[0][1][i][0]] == rule[0][1][i][1][1]))

    df2 = df_[mask].copy()

    # assign treatment flag
    mask = np.ones(df2.shape[0], dtype=int)
    for i in range(len(rule[0][1])):
        # df2['Treatment'] = np.where((df2[rule[0][1][i][0]] == rule[0][1][i][1][1]), 1, 0)
        this_mask = np.where(df2[rule[0][1][i][0]].astype(str) == rule[0][1][i][1][1], 1, 0)
        mask = mask * this_mask
    df2['Treatment'] = mask.astype(str)

    return df2


def process_data(df_rule):
    num_cols = ['CreditScore', 'MonthlyCost', 'NumberOfOffers', 'NoOfTerms', 'FirstWithdrawalAmount',
                'Treatment', 'Selected']
    cat_cols = ['ApplicationType', 'LoanGoal']

    for col in df_rule.columns:
        if (col not in num_cols) and (col not in cat_cols):
            df_rule = df_rule.drop(col, axis=1)

    # one hot encoding of categorical data
    tmp = pd.DataFrame()
    for col in cat_cols:
        tmp = pd.concat([tmp, pd.get_dummies(df_rule[col])], axis=1)
        df_rule = df_rule.drop(col, axis=1)

    df3 = pd.concat([df_rule, tmp], axis=1)

    return df3
