""" Program to read and preprocess data and then find causal rules to improve processes
"""
import argparse

from action_rules import action_discovery, interpret_rules, get_unique_actions
from data_prep import read_prep_data
from uplift_tree import create_uplift_tree

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='BPIC17_O_Accepted.csv', help='Name of dataset')
    parser.add_argument('--flexible_cols', type=list,
                        default=['binned_FirstWithdrawalAmount', 'binned_MonthlyCost', 'binned_NoOfTerms',
                                 'binned_NumberOfOffers'], help='Set of columns that can be '
                                                                'controlled')
    parser.add_argument('--stable_cols', type=list, default=['ApplicationType', 'binned_CreditScore', 'LoanGoal',
                                                             'binned_RequestedAmount'],
                        help='Set of columns that cannot be '
                             'controlled')
    parser.add_argument('--consequent_cols', type=str, default='Selected',
                        help='Target columns')
    args = parser.parse_args()

    df = read_prep_data(args.dataset)

    uplift = []
    r_list = []
    rep_list = []
    print("=================Start============================================\n")
    print(f"Stable cols: {args.stable_cols}\nFlexible_cols: {args.flexible_cols}\n")

    rules, length, rules_representation = action_discovery(df, args.stable_cols, args.flexible_cols,
                                                           args.consequent_cols)

    uplift.extend(interpret_rules(rules, length, rules_representation))

    rep_list.extend(rules_representation)
    r_list.extend(rules)

    print("===============================Finish================================\n")

    r_copy2 = get_unique_actions(r_list)
    create_uplift_tree(df, r_copy2)
