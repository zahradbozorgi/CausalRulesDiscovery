""" Define function for reading and preprocessing event log
"""

import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)


def read_prep_data(file):
    """ Function to read and preprocess a event log dataset

    :param file: event log in CSV format
    :return: preprocessed event data in dataframe format
    """
    df = pd.read_csv(r"../data/%s" % file, sep=';', parse_dates=["time:timestamp"])

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
    # df2 = df[df['Activity']=='A_Incomplete']
    # df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    # df_new.columns = ['Case ID', 'FrequencyOfIncompleteness']
    # df_new = pd.DataFrame(df_new.groupby('Case ID')['FrequencyOfIncompleteness'].sum()).reset_index()
    # df = pd.merge(df_new, df, on='Case ID')

    # For NumberOfOffers
    df2 = df[df['Activity'] == "O_Created"]  # to count offers
    df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    df_new.columns = ['Case ID', 'NumberOfOffers']
    df = pd.merge(df_new, df, on='Case ID')

    df['MatchedRequest'] = np.where((df.RequestedAmount <= df.OfferedAmount), 'True', 'False')

    # Calculate time from offer date to finished
    df_first_date = pd.DataFrame(
        df[(df["Activity"].isin(["O_Create Offer"]))].groupby("Case ID")["time:timestamp"].min())
    df_first_date.columns = ["start_date"]
    df_end_date = pd.DataFrame(
        df[(df["Activity"].isin(["A_Denied", "A_Cancelled", "A_Pending"]))].groupby("Case ID")["time:timestamp"].max())
    df_end_date.columns = ["end_date"]
    df = pd.merge(df, df_first_date, on="Case ID", how="left")
    df = pd.merge(df, df_end_date, on="Case ID", how="left")
    df["duration"] = df.end_date - df.start_date
    df["durationDays"] = df["duration"].apply(lambda x: x.days)

    # Additional Feature: Responding time between first activity and offer sent to customer
    df_first_activity = pd.DataFrame(df.groupby("Case ID")["time:timestamp"].min())
    df_first_activity.columns = ["start_date_r"]
    df_sent_offer = pd.DataFrame(
        df[(df["Activity"].isin(["O_Sent (mail and online)", "O_Sent (online only)"]))].groupby("Case ID")[
            "time:timestamp"].max())
    df_sent_offer.columns = ["sent_date"]
    df = pd.merge(df, df_first_activity, on="Case ID", how="left")
    df = pd.merge(df, df_sent_offer, on="Case ID", how="left")
    df["response_time"] = df.sent_date - df.start_date_r
    df["responseDays"] = df["response_time"].apply(lambda x: x.days)
    # fill NAs: these cases have been cancelled, we replace these cases with high response intervals
    df.responseDays.replace(np.nan, 1001.00, inplace=True)

    df.reset_index(drop=True, inplace=True)

    # O_Sent (mail and online)
    # df2 = df[df['Activity'] == 'O_Sent (mail and online)'] # to count offers
    # df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    # df_new.columns = ['Case ID', 'O_sent_mail_online_frequency']
    # df = pd.merge(df_new, df, on='Case ID')

    # O_Sent (online only)
    # df2 = df[df['Activity'] == 'O_Sent (online only)'] # to count offers
    # df_new = pd.DataFrame(df2.groupby(['Case ID'])['Activity'].count()).reset_index()
    # df_new.columns = ['Case ID', 'O_sent_online_only_frequency']
    # df = pd.merge(df_new, df, on='Case ID')

    # binning columns
    # df['new_duration'] = pd.cut(df['durationDays'], [0,8,15,30,31,168],
    # include_lowest=True, right=False, labels=['0-7','8-14','15-29','30','31+'])
    # df['new_duration'] = df['new_duration'].astype(str)
    # df['new_FrequencyOfIncompleteness'] = pd.cut(df['FrequencyOfIncompleteness'], 15)
    # df['new_FrequencyOfIncompleteness'] = df['new_FrequencyOfIncompleteness'].astype(str)xs

    df['binned_RequestedAmount'] = pd.qcut(df['RequestedAmount'], 5, labels=['0-5000', '5001-10000',
                                                                             '10001-15000', '15001-25000', '25000+'])
    df['binned_RequestedAmount'] = df['binned_RequestedAmount'].astype(str)

    df['binned_duration'] = pd.qcut(df['durationDays'], 5, labels=['0-8', '9-13', '14-22', '23-30', '30+'])
    df['binned_duration'] = df['binned_duration'].astype(str)

    # Response Time binning
    df['binnedResponseTime'] = pd.cut(df['responseDays'], bins=[0,2,4,5,7,1000,1001], labels=['0-2', '2-4', '4-5', '5-7','7-1000', '1000+'], include_lowest=True)
    df['binnedResponseTime'] = df['binnedResponseTime'].astype(str)

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
    df = df.groupby('Case ID').tail(1)
    df = df.reset_index(drop=True)

    # lower case
    column = ['ApplicationType', 'LoanGoal', 'MatchedRequest']
    for col in column:
        df[col] = df[col].str.lower()

    return df
