import pandas as pd
import numpy as np

pd.set_option('display.max_columns', None)
from datetime import datetime
from dateutil.parser import parse


def read_prep_data(file):
    df = pd.read_csv(r"../data/%s" % file, sep=';')
    # missining selected
    df = df[df['Selected'] != 'missing']  # make sure that we have data for selected attribute

    # CreditScore handeling
    df.CreditScore.replace(0.0, np.nan, inplace=True)
    df['CreditScore'].fillna((df['CreditScore'].median()), inplace=True)

    # MonthlyCost handeling
    df.MonthlyCost.replace(0.0, np.nan, inplace=True)
    df['MonthlyCost'].fillna((df['MonthlyCost'].median()), inplace=True)

    # NumberOfTerms handeling
    df.NumberOfTerms.replace(0.0, np.nan, inplace=True)
    df['NumberOfTerms'].fillna((df['NumberOfTerms'].median()), inplace=True)

    # FirstWithdrawalAmount handeling
    df.FirstWithdrawalAmount.replace(0.0, np.nan, inplace=True)
    df['FirstWithdrawalAmount'].fillna((df['FirstWithdrawalAmount'].median()), inplace=True)

    # map Selected to 1(signed), and 0(not signed)
    df['Selected'] = df['Selected'].map({'True': 1, 'False': 0})

    # for FrequencyOfIncompleteness
    #     df2 = df[df['Activity']=='A_Incomplete']
    #     df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    #     df_new.columns = ['Case ID', 'FrequencyOfIncompleteness']
    #     df_new = pd.DataFrame(df_new.groupby('Case ID')['FrequencyOfIncompleteness'].sum()).reset_index()
    #     df = pd.merge(df_new, df, on='Case ID')

    # For NumberOfOffers
    df2 = df[df['Activity'] == "O_Created"]  # to count offers
    df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    df_new.columns = ['Case ID', 'NumberOfOffers']
    df = pd.merge(df_new, df, on='Case ID')

    # For matchRequested
    df['MatchedRequest'] = np.where((df.RequestedAmount <= df.OfferedAmount), 'True', 'False')

    df = df.groupby('Case ID').apply(get_duration)
    df = df.reset_index(drop=True)

    # O_Sent (mail and online)
    #     df2 = df[df['Activity'] == 'O_Sent (mail and online)'] # to count offers
    #     df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    #     df_new.columns = ['Case ID', 'O_sent_mail_online_frequency']
    #     df = pd.merge(df_new, df, on='Case ID')

    # O_Sent (online only)
    #     df2 = df[df['Activity'] == 'O_Sent (online only)'] # to count offers
    #     df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    #     df_new.columns = ['Case ID', 'O_sent_online_only_frequency']
    #     df = pd.merge(df_new, df, on='Case ID')

    # binning columns
    #    df['new_duration'] = pd.cut(df['durationDays'], [0,8,15,30,31,168],
    #                                include_lowest=True, right=False, labels=['0-7','8-14','15-29','30','31+'])
    #    df['new_duration'] = df['new_duration'].astype(str)
    #    df['new_FrequencyOfIncompleteness'] = pd.cut(df['FrequencyOfIncompleteness'], 15)
    #    df['new_FrequencyOfIncompleteness'] = df['new_FrequencyOfIncompleteness'].astype(str)xs

    df['binned_RequestedAmount'] = pd.qcut(df['RequestedAmount'], 5, labels=['0-5000', '5001-10000',
                                                                             '10001-15000', '15001-25000', '25000+'])
    df['binned_RequestedAmount'] = df['binned_RequestedAmount'].astype(str)

    df['binned_duration'] = pd.qcut(df['durationDays'], 5, labels=['0-8', '9-13', '14-22', '23-30', '30+'])
    df['binned_duration'] = df['binned_duration'].astype(str)

    df['binned_NoOfTerms'] = pd.qcut(df['NumberOfTerms'], 5, labels=['6-48', '49-60', '61-96', '97-120', '120+'])
    df['binned_NoOfTerms'] = df['binned_NoOfTerms'].astype(str)

    df['binned_CreditScore'] = pd.qcut(df['CreditScore'], 2, labels=['low', 'high'])
    df['binned_CreditScore'] = df['binned_CreditScore'].astype(str)

    df['binned_MonthlyCost'] = pd.qcut(df['MonthlyCost'], 5, labels=['40-148', '149-200', '201-270',
                                                                     '271-388', '388+'])
    df['binned_MonthlyCost'] = df['binned_MonthlyCost'].astype(str)

    df['binned_FirstWithdrawalAmount'] = pd.qcut(df['FirstWithdrawalAmount'], 3,
                                                 labels=['0-7499', '7500-9895', '9896-75000'])
    df['binned_FirstWithdrawalAmount'] = df['binned_FirstWithdrawalAmount'].astype(str)

    df['binned_NumberOfOffers'] = pd.cut(df['NumberOfOffers'], [1, 2, 3, 11],
                                         include_lowest=True, right=False, labels=['1', '2', '3+'])
    df['binned_NumberOfOffers'] = df['binned_NumberOfOffers'].astype(str)

    df = df.groupby('Case ID').apply(keep_last)
    df = df.reset_index(drop=True)

    # lower case
    column = ['ApplicationType', 'LoanGoal', 'MatchedRequest']
    for col in column:
        df[col] = df[col].str.lower()

    return df


def keep_last(group):
    return group.tail(1)


def get_duration(gr):
    df = pd.DataFrame(gr)
    if len(df[(df["Activity"] == "A_Denied") | (df["Activity"] == "A_Cancelled") | (
            df["Activity"] == "A_Pending")]) > 0:
        df['new_date'] = [datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f') for d in df['time:timestamp']]

        first_dt = df[df['Activity'] == 'O_Create Offer']['new_date']
        last_dt = \
            df[(df["Activity"] == "A_Denied") | (df["Activity"] == "A_Cancelled") | (df["Activity"] == "A_Pending")][
                'new_date']

        first_dt = first_dt[first_dt.index.values[0]]
        # print(last_dt)
        last_dt = last_dt[last_dt.index.values[0]]

        d1 = parse(str(first_dt))
        d2 = parse(str(last_dt))

        delta_days = (d2 - d1).days
        # print(delta_days,'\n')
        df['durationDays'] = delta_days
        return df
