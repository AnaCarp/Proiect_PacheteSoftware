import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt
import seaborn as sns

def nan_replace_t(t):
    assert isinstance(t, pd.DataFrame)
    for v in t.columns:
        if any(t[v].isna()):
            if is_numeric_dtype(t[v]):
                t[v].fillna(t[v].mean(), inplace=True)
            else:
                t[v].fillna(t[v].mode()[0], inplace=True)

def minutes_to_hours(t):
    assert isinstance(t, pd.DataFrame)
    x = t.values
    p = np.round(np.transpose(x.T / 60),0)
    return pd.DataFrame(p, t.index, t.columns)

def day_name(weekday):
    if weekday == 1:
        return "Sunday"
    if weekday == 2:
        return "Monday"
    if weekday == 3:
        return "Tuesday"
    if weekday == 4:
        return "Wednesday"
    if weekday == 5:
        return "Thursday"
    if weekday == 6:
        return "Friday"
    if weekday == 7:
        return "Saturday"


from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

def conf_mtrx(y_test, y_pred, model_name):
    cm = confusion_matrix(y_test, y_pred)
    f, ax = plt.subplots(figsize=(5, 5))
    sns.heatmap(cm, annot=True, linewidths=0.5, linecolor="red", fmt=".0f", ax=ax)
    plt.xlabel("predicted y values")
    plt.ylabel("real y values")
    plt.title("\nConfusion Matrix " + model_name)
    plt.show()


'''Functie pentru afisarea curbei ROC si AUC'''
from sklearn.metrics import roc_auc_score, roc_curve


def roc_auc_curve_plot(model_name, X_testt, y_testt):
    ns_probs = [0 for _ in range(len(y_testt))]
    # probabiltatile modelului
    model_probs = model_name.predict_proba(X_testt)
    # pastram doar probabilitatile pentru valorile pozitive
    model_probs = model_probs[:, 1]
    # calcul scor auc
    ns_auc = roc_auc_score(y_testt, ns_probs)
    lr_auc = roc_auc_score(y_testt, model_probs)

    print('No Skill: ROC AUC=%.3f' % (ns_auc))
    print(': ROC AUC=%.3f' % (lr_auc))
    #  roc curves
    ns_fpr, ns_tpr, _ = roc_curve(y_testt, ns_probs)
    model_fpr, model_tpr, _ = roc_curve(y_testt, model_probs)
    # plot the roc curve for the model
    plt.plot(ns_fpr, ns_tpr, linestyle='--', label='No Skill')
    plt.plot(model_fpr, model_tpr, marker='.', label='Clasifier')
    # axis labels
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.legend()
    plt.show()