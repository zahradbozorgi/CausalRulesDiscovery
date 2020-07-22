from causalml.inference.tree import UpliftTreeClassifier
from causalml.inference.tree import uplift_tree_string, uplift_tree_plot
from sklearn.model_selection import train_test_split
from log_processing import filter_log, process_data


def create_uplift_tree(df, r_copy2):
    for rule in r_copy2:
        print(rule)
        print("index:", r_copy2.index(rule))
        df_rule = filter_log(df, rule)
        print(df_rule.shape)
        df3 = process_data(df_rule)
        df_train, df_test = train_test_split(df3, test_size=0.2)
        features = df_train
        for col in ['Selected', 'Treatment']:
            features = features.drop(col, axis=1)

        # Train uplift tree
        uplift_model = UpliftTreeClassifier(max_depth=5, min_samples_leaf=200, min_samples_treatment=50,
                                            n_reg=100, evaluationFunction='KL', control_name='0')

        # Train uplift random forest
        # uplift_model = UpliftRandomForestClassifier(control_name='0')
        uplift_model.fit(features.values, treatment=df_train['Treatment'].values, y=df_train['Selected'].values)

        # Print uplift tree as a string
        result = uplift_tree_string(uplift_model.fitted_uplift_tree, features.columns.values.tolist())

        # save uplift tree as png
        graph = uplift_tree_plot(uplift_model.fitted_uplift_tree, features.columns.values.tolist())
        with open("tree2_%s.png" % r_copy2.index(rule), "wb") as png:
            png.write(graph.create_png())
        # display(Image(graph.create_png()))

    #   y_pred = uplift_model.predict(df_test.values)

    #   # Put the predictions to a DataFrame for a neater presentation
    #   result = pd.DataFrame(y_pred, columns=uplift_model.classes_)
    #   print(result)
