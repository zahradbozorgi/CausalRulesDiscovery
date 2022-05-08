""" Functions to detect action rules and print results
"""

import pandas as pd
from actionrules.actionRulesDiscovery import ActionRulesDiscovery

pd.set_option('display.max_columns', None)


def action_discovery(data, stable_cols, flexible_cols, consequent_col):
    """ Function for action rule discovery

    :param data: preprocessed event log data
    :param stable_cols: list of variables that cannot be influenced
    :param flexible_cols:  list of variables that can be controlled
    :param consequent_col:  list of target variables to be influenced
    :return: list of rules, number of rules, list of rule representations
    """
    # print(f"Stable_cols: {stabel_cols}\n")
    # print(f"flexible_cols: {flexible_cols}\n")

    actionrulesdiscovery = ActionRulesDiscovery()
    actionrulesdiscovery.load_pandas(data)
    actionrulesdiscovery.fit(stable_attributes=stable_cols,
                             flexible_attributes=flexible_cols,
                             consequent=consequent_col,
                             conf=55,
                             supp=3,
                             desired_classes=["1"],  # fail to success / not survived to survived
                             max_stable_attributes=30,
                             max_flexible_attributes=30,
                             )
    rules = actionrulesdiscovery.get_action_rules()
    rules_representation = actionrulesdiscovery.get_action_rules_representation()
    length = len(actionrulesdiscovery.get_action_rules_representation())

    return rules, length, rules_representation


def interpret_rules(rules, length, rules_representation):
    """ Function to interpret rules

    :param rules: list of rules
    :param length: number of rules
    :param rules_representation: list of rule representations
    :return: list for uplift of discovered rules
    """
    print(f"The number of discovered rules are: {len(rules)}\n")
    # i = 1
    [print(f"Rule: {rule}\n") for rule in rules_representation]
    # print("+++++++++++++++++++++++++++++++++++++++++++++++++++")

    supp = []
    conf = []
    uplift = []
    if not rules:
        print("No Discovered Rules")
    else:
        [supp.append(rules[i][1][2]) for i in range(length)]
        [conf.append(rules[i][2][2]) for i in range(length)]
        [uplift.append(rules[i][3]) for i in range(length)]

        print(f"max supp: {max(supp)}")
        print(f"max conf: {max(conf)}")
        print(f"max uplift: {max(uplift)}")
        # print(f"================ Finish=================\n\n")

    return uplift


def get_unique_actions(r_copy):
    """ Function to detect unique actions from rule set

    :param r_copy: list of rules
    :return: dataframe of unique actions
    """
    rule_id = 0
    df_tmp_list = []
    for rule in r_copy:
        tmp = pd.DataFrame()
        j = 0
        for i in rule:
            tmp.at[0, j] = str(i)
            j += 1
        rule_id += 1
        df_tmp_list.append(tmp)
    df_u = pd.concat(df_tmp_list, ignore_index=True)
    df_u.columns = ["a", "b", "c", "d"]
    df_u["a_new"] = "0"

    for index, row in df_u.iterrows():
        lst = [i for i in str(row["a"]).split("]],")]
        row["a_new"] = lst

    df2 = pd.concat([df_u, df_u["a_new"].apply(pd.Series)], axis=1)
    df2.columns = ["a", "b", "c", "d", "a_new", "stable", "flex", "outcome"]
    rules_processed = df2
    tmp = []
    for _, rule in rules_processed.groupby("flex"):
        #     tmp.append(rule["a"].iloc[0])
        tmp.append(rule.index[0])

    r_copy2 = []
    for i in tmp:
        r_copy2.append(r_copy[i])

    return r_copy2
