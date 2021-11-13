import itertools
import math
import os
import sys

import numpy as np
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go
from assignment4 import is_continuous, plot_categorical, plot_continuous
from cat_correlation import cat_cont_correlation_ratio, cat_correlation
from hw4_data import get_test_data_set
from pandas.api.types import is_numeric_dtype
from scipy import stats
from sklearn.preprocessing import LabelEncoder


# function to get the correlation coefficient of all continuous- continuous predictor pairs
# Parameters:
# dataframe - pandas dataframe containing the predictors
# list_of_predictors: list of all continuous predictors in the dataframe
# ** RETURNS **: pandas dataframe containing the correlation coefficient of each combo sorting in desc order
def cont_cont_correlation(dataframe, list_of_predictors, response):
    cont_combinations = list(itertools.combinations(list_of_predictors, 2))
    metrics = []
    pred1 = []
    pred2 = []
    for i in cont_combinations:
        pred1.append(i[0])
        pred2.append(i[1])
        metrics.append(stats.pearsonr(dataframe[i[0]], dataframe[i[1]])[0])

    # create plots for all predictors
    for i in list_of_predictors:
        fig = plot_continuous(dataframe, dataframe[i], response)
        fig.write_html(i.replace(" ", "") + ".html")

    result = pd.DataFrame(
        list(zip(pred1, pred2, metrics)),
        columns=["predictor1", "predictor2", "pearson coefficient"],
    ).sort_values(by="pearson coefficient", ascending=False)
    result.to_html(
        "finalTables/continuous_predictors_table.html",
        formatters={
            "predictor1": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
            "predictor2": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
        },
        escape=False,
    )
    return result


# helper function to determine if a series in a dataframe is binary or not
def is_binary(dataframe, column_name):
    if dataframe[column_name].nunique() == 2:
        return True
    else:
        return False


# this function will create a table with all cont-cat predictor combinations ordered by correlation metric
def cont_cat_correlation(dataframe, list_of_cont, list_of_cat, response):
    # first, get all combinations of cont-cat in a single list
    combinations = list(itertools.product(list_of_cont, list_of_cat))

    # next, decipher whether or not point biserial or the correlation ratio should be used
    # check to see if the categorical predictor is binary, if binary -> point biserial
    # if not binary -> correlation ratio

    pred1 = []
    pred2 = []
    metrics = []
    point_biserial = []
    for i in combinations:
        pred1.append(i[0])
        pred2.append(i[1])
        # condition where categorical predictor is binary, so do point biserial correlation
        if is_binary(dataframe, i[1]):
            point_biserial.append(True)
            # check to see if current series is numeric, if not, encode the series (0 and 1) and run point biserial
            if ~is_numeric_dtype(dataframe[i[1]]):
                values = list(set(dataframe[i[1]].values))
                encoded_series = dataframe[i[1]].replace([values[0], values[1]], [0, 1])
                metrics.append(stats.pointbiserialr(encoded_series, dataframe[i[0]])[0])
            # Condition where series is numeric, so no need to encode
            else:
                metrics.append(
                    stats.pointbiserialr(dataframe[i[1]], dataframe[i[0]])[0]
                )
        # condition where categorical predictor is not binary, so do correlation ratio
        else:
            point_biserial.append(False)
            metrics.append(cat_cont_correlation_ratio(dataframe[i[1]], dataframe[i[0]]))

    # produce plots of all the categorical predictors
    for i in list_of_cat:
        fig = plot_categorical(dataframe, dataframe[i], response)
        fig.write_html(i.replace(" ", "") + ".html")

    # produce plots of continuous predictors
    for i in list_of_cont:
        fig = plot_continuous(dataframe, dataframe[i], response)
        fig.write_html(i.replace(" ", "") + ".html")

    # create resulting table in a pandas dataframe
    result = pd.DataFrame(
        list(zip(pred1, pred2, metrics, point_biserial)),
        columns=["Predictor1", "Predictor2", "Correlation Metric", "point_biserial"],
    ).sort_values(by="Correlation Metric", ascending=False)

    result.to_html(
        "cat_cont_predictors_table.html",
        formatters={
            "Predictor1": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
            "Predictor2": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
        },
        escape=False,
    )

    return result


# this function will create a table with all the categorical predictor combinations ordered by correlation coefficient
def cat_cat_correlation(dataframe, list_of_cat, response):

    # First, check to see if list_of_cat has at least 2 values (need at least 2 categorical predictors)
    # with less than 2 categorical predictors, there are no cat - cat pairs, so this function can be skipped
    if len(list_of_cat) < 2:
        print(
            "Less then 2 categorical predictors in dataframe, skipping cat-cat predictor table",
            file=sys.stderr,
        )
        return
    # first, get all combinations of cat-cat predictors
    combinations = list(itertools.combinations(list_of_cat, 2))

    # next, compute cramers V  correlation metric for all pairs
    pred1 = []
    pred2 = []
    metrics = []
    for i in combinations:
        pred1.append(i[0])
        pred2.append(i[1])
        metrics.append(cat_correlation(dataframe[i[0]].values, dataframe[i[1]].values))

    # plot all of the categorical predictors
    for i in list_of_cat:
        fig = plot_categorical(dataframe, dataframe[i], response)
        fig.write_html(i.replace(" ", "") + ".html")

    # create resulting table in a pandas dataframe
    result = pd.DataFrame(
        list(zip(pred1, pred2, metrics)),
        columns=["Predictor1", "Predictor2", "Correlation Metric"],
    ).sort_values(by="Correlation Metric", ascending=False)

    result.to_html(
        "cat_predictors_table.html",
        formatters={
            "Predictor1": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
            "Predictor2": lambda x: f'<a href="{x.replace(" ", "") + ".html"}">{x}</a>',
        },
        escape=False,
    )

    return result


# this function will create a correlation matrix heatmap for all cont-cont predictor combinations
def cont_cont_heatmap(continuous, dataframe):
    result = []
    for i in continuous:
        holder = []
        for j in continuous:
            holder.append(stats.pearsonr(dataframe[i].values, dataframe[j].values)[0])
        result.append(holder)

    fig = ff.create_annotated_heatmap(
        result, x=continuous, y=continuous, showscale=True, colorscale="Blues"
    )
    fig.update_layout(title="Continuous-Continuous Correlation Matrix")
    fig.show()


# this function will create a correlation matrix heatmap for all cont-cat predictor combinations
def cont_cat_heatmap(categoricals, continuous, dataframe):

    result = []
    for i in categoricals:
        holder = []
        for j in continuous:
            holder.append(
                cat_cont_correlation_ratio(dataframe[i].values, dataframe[j].values)
            )
        result.append(holder)

    fig = ff.create_annotated_heatmap(
        result, x=continuous, y=categoricals, showscale=True, colorscale="Blues"
    )
    fig.update_layout(title="Continuous-Categorical Correlation Matrix")
    fig.show()


# this function will create a correlation matrix heatmap for all cat-cat predictor combinations if they exist
def cat_cat_heatmap(categoricals, dataframe):
    result = []
    for i in categoricals:
        holder = []
        for j in categoricals:
            holder.append(cat_correlation(dataframe[i].values, dataframe[j].values))
        result.append(holder)

    fig = ff.create_annotated_heatmap(
        result, x=categoricals, y=categoricals, showscale=True, colorscale="Blues"
    )
    fig.update_layout(title="Categorical-Categorical Correlation Matrix")
    fig.show()


# diff with mean of response on cont-cont predoctor combination
def diff_mean_response_2d_cont(dataframe, cont_pred1, cont_pred2, response, weighted):
    # get bins for both predictors
    pred1_bins = pd.cut(dataframe[cont_pred1], bins=10, labels=False)
    pred2_bins = pd.cut(dataframe[cont_pred2], bins=10, labels=False)

    # make array of tuples, where tuple is of following structure:
    # (x,y), where x = response value of position i, y = bin number of position i
    res1 = [
        (dataframe[response].values[i], pred1_bins[i]) for i in range(len(pred1_bins))
    ]
    res2 = [
        (dataframe[response].values[i], pred2_bins[i]) for i in range(len(pred2_bins))
    ]

    sorted_bins1 = sorted(res1, key=lambda x: x[1])
    sorted_bins2 = sorted(res2, key=lambda x: x[1])

    # calculate the average response value of each bin, and store in bin_response_means
    # where index 0 = bin 0, index 1 = bin 1, etc.
    bin_response_means1 = []
    bin_response_means2 = []
    for i in np.unique(pred1_bins):
        arr1 = []
        arr2 = []
        for j in range(len(sorted_bins1)):
            if sorted_bins1[j][1] == i:
                arr1.append(sorted_bins1[j][0])

            else:
                continue
        for k in range(len(sorted_bins2)):
            if sorted_bins2[k][1] == i:
                arr2.append(sorted_bins2[k][0])
            else:
                continue

        bin_response_means1.append(np.mean(arr1))
        bin_response_means2.append(np.mean(arr2))

    # count the number of observations in each bin for both predictors
    bin_count1 = np.bincount(pred1_bins)
    bin_count2 = np.bincount(pred2_bins)

    # get population response mean
    pop_mean = dataframe[response].mean()
    # get total Population of both predictors
    total_population = np.sum(bin_count1) + np.sum(bin_count2)

    # make the 2d list of means and result
    mean_matrix = []
    result_matrix = []
    residuals = []
    residuals_weighted = []
    all_combos = list(itertools.product(bin_response_means1, bin_response_means2))

    master_idx = 0
    idx = 0
    holder = []
    holder_unweighted = []
    holder_weighted = []
    heatmap_matrix = []
    for i in all_combos:
        # get current mean of predictors in bin i,j, check for empty bins, if empty, ignore bin
        if math.isnan(i[0]) and ~math.isnan(i[1]):
            curr_mean = i[1]
        elif ~math.isnan(i[0]) and math.isnan(i[1]):
            curr_mean = i[0]
        else:
            curr_mean = (i[0] + i[1]) / 2
        # append current mean to mean_matrix
        mean_matrix.append(curr_mean)
        # calculate squared difference for either weighted or unweighted
        if weighted:
            if master_idx != 0 and master_idx % 10 == 0:
                idx += 1
            pop_proportion = (bin_count1[idx] + bin_count2[idx]) / total_population
            squared_diff = pop_proportion * (curr_mean - pop_mean) ** 2
            holder_weighted.append(pop_proportion * (curr_mean - pop_mean))
        else:
            squared_diff = (curr_mean - pop_mean) ** 2

        if master_idx != 0 and master_idx % 10 == 0:
            heatmap_matrix.append(holder.copy())
            residuals.append(holder_unweighted.copy())
            residuals_weighted.append(holder_weighted.copy())
            holder.clear()
            holder_unweighted.clear()
            holder_weighted.clear()

        holder.append(curr_mean)
        holder_unweighted.append(curr_mean - pop_mean)
        result_matrix.append(squared_diff)
        master_idx += 1

    # if weighted, just return the sum of the result_matrix, but if unweighted, divide by number of bins
    if weighted:
        result = np.sum(result_matrix)
    else:
        result = np.sum(result_matrix) / 10

    # create plot of result (bin mean plot)
    bin_values1 = pd.cut(dataframe[cont_pred1], bins=10, retbins=True)[1]
    bin_values2 = pd.cut(dataframe[cont_pred2], bins=10, retbins=True)[1]
    trace = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=np.array(heatmap_matrix).T,
        colorscale="RdBu",
        showscale=True,
        zmin=0,
        zmax=1.8 * pop_mean,
        colorbar=dict(title="mean of bin i,j"),
    )
    data = [trace]
    fig = go.Figure(data=data)
    fig.update_layout(
        title=f"{cont_pred1} and {cont_pred2} bin averages",
        xaxis_title=f"{cont_pred1}",
        yaxis_title=f"{cont_pred2}",
    )
    fig.write_html(f"{cont_pred1} vs {cont_pred2}.html")

    # now plot residual plot, if weighted = true, plot weighted version, else, plot unweighted version

    if weighted:
        z_axis = np.array(residuals_weighted).T
        plot_title = f"{cont_pred1} vs {cont_pred2} weighted residuals"
    else:
        z_axis = np.array(residuals).T
        plot_title = f"{cont_pred1} vs {cont_pred2} residuals"
    trace2 = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=z_axis,
        colorscale="RdBu",
        showscale=True,
        colorbar=dict(title="residual value"),
    )
    data2 = [trace2]
    fig2 = go.Figure(data=data2)
    fig2.update_layout(
        title=plot_title,
        xaxis_title=f"{cont_pred1}",
        yaxis_title=f"{cont_pred2}",
    )
    fig2.write_html(plot_title + ".html")

    return result


# diff w mean of response on cont-cat predictor combination
def diff_mean_response_cont_cat_2d(dataframe, cont, cat, response, weighted):
    # get bins for both predictors, for categorical predictor, use label encoder to make n bins,
    # where n is the number of categories.
    pred1_bins = pd.cut(dataframe[cont], bins=10, labels=False)
    encoder = LabelEncoder()
    dataframe[cat + "_encoded"] = encoder.fit_transform(dataframe[cat])
    pred2_bins = dataframe[cat + "_encoded"]

    # make array of tuples, where tuple is of following structure:
    # (x,y), where x = response value of position i, y = bin number of position i
    res1 = [
        (dataframe[response].values[i], pred1_bins[i]) for i in range(len(pred1_bins))
    ]
    res2 = [
        (dataframe[response].values[i], pred2_bins[i]) for i in range(len(pred2_bins))
    ]

    sorted_bins1 = sorted(res1, key=lambda x: x[1])
    sorted_bins2 = sorted(res2, key=lambda x: x[1])

    # calculate the average response value of each bin, and store in bin_response_means
    # where index 0 = bin 0, index 1 = bin 1, etc.
    bin_response_means1 = []
    for i in np.unique(pred1_bins):
        arr1 = []
        for j in range(len(sorted_bins1)):
            if sorted_bins1[j][1] == i:
                arr1.append(sorted_bins1[j][0])

            else:
                continue
        bin_response_means1.append(np.mean(arr1))

    bin_response_means2 = []
    for i in np.unique(pred2_bins):
        arr = []
        for j in range(len(sorted_bins2)):
            if sorted_bins2[j][1] == i:
                arr.append(sorted_bins2[j][0])
            else:
                continue
        bin_response_means2.append(np.mean(arr))

    # count the number of observations in each bin for both predictors
    bin_count1 = np.bincount(pred1_bins)
    bin_count2 = np.bincount(pred2_bins)

    # get population response mean
    pop_mean = dataframe[response].mean()
    # get total Population of both predictors
    total_population = np.sum(bin_count1) + np.sum(bin_count2)

    # make the 2d list of means and result
    mean_matrix = []
    result_matrix = []
    residuals = []
    residuals_weighted = []
    all_combos = list(itertools.product(bin_response_means1, bin_response_means2))

    master_idx = 0
    idx = 0
    idx2 = 0
    holder = []
    holder_unweighted = []
    holder_weighted = []
    heatmap_matrix = []
    for i in all_combos:
        # get current mean of predictors in bin i,j, check for empty bins, if empty, ignore bin
        if math.isnan(i[0]) and ~math.isnan(i[1]):
            curr_mean = i[1]
        elif ~math.isnan(i[0]) and math.isnan(i[1]):
            curr_mean = i[0]
        else:
            curr_mean = (i[0] + i[1]) / 2

        # append current mean to mean_matrix
        mean_matrix.append(curr_mean)
        # calculate squared difference for either weighted or unweighted
        if master_idx != 0 and master_idx % len(np.unique(pred2_bins)) == 0:
            idx += 1
            if idx % len(np.unique(pred1_bins)) == 0:
                idx = 0
        pop_proportion = (
            bin_count1[idx] + bin_count2[idx2]
        ) / total_population  # bin_count2 idx not right
        idx2 += 1
        if idx2 % len(np.unique(pred2_bins)):
            idx2 = 0
        if weighted:
            squared_diff = pop_proportion * (curr_mean - pop_mean) ** 2

        else:
            squared_diff = (curr_mean - pop_mean) ** 2

        if master_idx != 0 and master_idx % len(np.unique(pred2_bins)) == 0:
            heatmap_matrix.append(holder.copy())
            residuals.append(holder_unweighted.copy())
            residuals_weighted.append(holder_weighted.copy())
            holder.clear()
            holder_unweighted.clear()
            holder_weighted.clear()

        holder.append(curr_mean)
        holder_unweighted.append(curr_mean - pop_mean)
        holder_weighted.append(pop_proportion * (curr_mean - pop_mean))
        result_matrix.append(squared_diff)
        master_idx += 1

    heatmap_matrix.append(holder.copy())
    residuals.append(holder_unweighted.copy())
    residuals_weighted.append(holder_weighted.copy())

    # if weighted, just return the sum of the result_matrix, but if unweighted, divide by number of bins
    if weighted:
        result = np.sum(result_matrix)
    else:
        result = np.sum(result_matrix) / (
            len(np.unique(pred1_bins)) + len(np.unique(pred2_bins))
        )

    # create plot of result (bin mean plot)
    bin_values1 = pd.cut(dataframe[cont], bins=10, retbins=True)[1]
    bin_values2 = np.array(list(map(str, np.unique(dataframe[cat]))))

    trace = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=np.array(heatmap_matrix).T,
        colorscale="RdBu",
        showscale=True,
        zmin=0,
        zmax=1.8 * pop_mean,
        colorbar=dict(title="mean of bin i,j"),
    )
    data = [trace]
    fig = go.Figure(data=data)
    fig.update_layout(
        title=f"{cont} and {cat} bin averages",
        xaxis_title=f"{cont}",
        yaxis_title=f"{cat}",
    )
    fig.write_html(f"{cont} vs {cat}.html")

    # now plot residual plot, if weighted = true, plot weighted version, else, plot unweighted version

    if weighted:
        z_axis = np.array(residuals_weighted).T
        plot_title = f"{cont} vs {cat} weighted residuals"
    else:
        z_axis = np.array(residuals).T
        plot_title = f"{cont} vs {cat} residuals"
    trace2 = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=z_axis,
        colorscale="RdBu",
        showscale=True,
        colorbar=dict(title="residual value"),
    )
    data2 = [trace2]
    fig2 = go.Figure(data=data2)
    fig2.update_layout(
        title=plot_title,
        xaxis_title=f"{cont}",
        yaxis_title=f"{cat}",
    )
    fig2.write_html(plot_title + ".html")

    return result


# this function will perform diff w mean of response on a pair of categorical predictors
def diff_mean_response_cat_cat_2d(dataframe, cat1, cat2, response, weighted):
    # get bins for both predictors, for categorical predictor, use label encoder to make n bins,
    # where n is the number of categories.
    encoder = LabelEncoder()
    encoder2 = LabelEncoder()
    dataframe[cat1 + "_encoded"] = encoder.fit_transform(dataframe[cat1])
    pred1_bins = dataframe[cat1 + "_encoded"]
    dataframe[cat2 + "_encoded"] = encoder2.fit_transform(dataframe[cat2])
    pred2_bins = dataframe[cat2 + "_encoded"]

    # make array of tuples, where tuple is of following structure:
    # (x,y), where x = response value of position i, y = bin number of position i
    res1 = [
        (dataframe[response].values[i], pred1_bins[i]) for i in range(len(pred1_bins))
    ]
    res2 = [
        (dataframe[response].values[i], pred2_bins[i]) for i in range(len(pred2_bins))
    ]

    sorted_bins1 = sorted(res1, key=lambda x: x[1])
    sorted_bins2 = sorted(res2, key=lambda x: x[1])

    # calculate the average response value of each bin, and store in bin_response_means
    # where index 0 = bin 0, index 1 = bin 1, etc.
    bin_response_means1 = []
    for i in np.unique(pred1_bins):
        arr1 = []
        for j in range(len(sorted_bins1)):
            if sorted_bins1[j][1] == i:
                arr1.append(sorted_bins1[j][0])

            else:
                continue
        bin_response_means1.append(np.mean(arr1))

    bin_response_means2 = []
    for i in np.unique(pred2_bins):
        arr = []
        for j in range(len(sorted_bins2)):
            if sorted_bins2[j][1] == i:
                arr.append(sorted_bins2[j][0])
            else:
                continue
        bin_response_means2.append(np.mean(arr))

    # count the number of observations in each bin for both predictors
    bin_count1 = np.bincount(pred1_bins)
    bin_count2 = np.bincount(pred2_bins)

    # get population response mean
    pop_mean = dataframe[response].mean()
    # get total Population of both predictors
    total_population = np.sum(bin_count1) + np.sum(bin_count2)

    # make the 2d list of means and result
    mean_matrix = []
    result_matrix = []
    residuals = []
    residuals_weighted = []
    all_combos = list(itertools.product(bin_response_means1, bin_response_means2))

    master_idx = 0
    idx = 0
    idx2 = 0
    holder = []
    holder_unweighted = []
    holder_weighted = []
    heatmap_matrix = []
    for i in all_combos:
        # get current mean of predictors in bin i,j, check for empty bins, if empty, ignore bin
        if math.isnan(i[0]) and ~math.isnan(i[1]):
            curr_mean = i[1]
        elif ~math.isnan(i[0]) and math.isnan(i[1]):
            curr_mean = i[0]
        else:
            curr_mean = (i[0] + i[1]) / 2

        # append current mean to mean_matrix
        mean_matrix.append(curr_mean)
        # calculate squared difference for either weighted or unweighted
        if master_idx != 0 and master_idx % len(np.unique(pred2_bins)) == 0:
            idx += 1
            if idx % len(np.unique(pred1_bins)) == 0:
                idx = 0
        pop_proportion = (
            bin_count1[idx] + bin_count2[idx2]
        ) / total_population  # bin_count2 idx not right
        idx2 += 1
        if idx2 % len(np.unique(pred2_bins)):
            idx2 = 0
        if weighted:
            squared_diff = pop_proportion * (curr_mean - pop_mean) ** 2

        else:
            squared_diff = (curr_mean - pop_mean) ** 2

        if master_idx != 0 and master_idx % len(np.unique(pred2_bins)) == 0:
            heatmap_matrix.append(holder.copy())
            residuals.append(holder_unweighted.copy())
            residuals_weighted.append(holder_weighted.copy())
            holder.clear()
            holder_unweighted.clear()
            holder_weighted.clear()

        holder.append(curr_mean)
        holder_unweighted.append(curr_mean - pop_mean)
        holder_weighted.append(pop_proportion * (curr_mean - pop_mean))
        result_matrix.append(squared_diff)
        master_idx += 1

    heatmap_matrix.append(holder.copy())
    residuals.append(holder_unweighted.copy())
    residuals_weighted.append(holder_weighted.copy())

    # if weighted, just return the sum of the result_matrix, but if unweighted, divide by number of bins
    if weighted:
        result = np.sum(result_matrix)
    else:
        result = np.sum(result_matrix) / (
            len(np.unique(pred1_bins)) + len(np.unique(pred2_bins))
        )

    # create plot of result (bin mean plot)
    bin_values1 = np.array(list(map(str, np.unique(dataframe[cat1]))))
    bin_values2 = np.array(list(map(str, np.unique(dataframe[cat2]))))

    trace = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=np.array(heatmap_matrix).T,
        colorscale="RdBu",
        showscale=True,
        zmin=0,
        zmax=1.8 * pop_mean,
        colorbar=dict(title="mean of bin i,j"),
    )
    data = [trace]
    fig = go.Figure(data=data)
    fig.update_layout(
        title=f"{cat1} and {cat2} bin averages",
        xaxis_title=f"{cat1}",
        yaxis_title=f"{cat2}",
    )
    fig.write_html(f"{cat1} vs {cat2}.html")

    # now plot residual plot, if weighted = true, plot weighted version, else, plot unweighted version

    if weighted:
        z_axis = np.array(residuals_weighted).T
        plot_title = f"{cat1} vs {cat2} weighted residuals"
    else:
        z_axis = np.array(residuals).T
        plot_title = f"{cat1} vs {cat2} residuals"
    trace2 = go.Heatmap(
        x=bin_values1,
        y=bin_values2,
        z=z_axis,
        colorscale="RdBu",
        showscale=True,
        colorbar=dict(title="residual value"),
    )
    data2 = [trace2]
    fig2 = go.Figure(data=data2)
    fig2.update_layout(
        title=plot_title,
        xaxis_title=f"{cat1}",
        yaxis_title=f"{cat2}",
    )
    fig2.write_html(plot_title + ".html")

    return result


# this function will output a "cont_brute_force_table.html" file in the same directory.
# Parameters: dataframe - dataframe used
# cont_predictors - list of all continuous predictors in dataframe (list of strings)
# response - string name of response column
def cont_cont_brute_force(dataframe, cont_predictors, response):

    unweighted = []
    weighted = []
    pred1 = []
    pred2 = []
    plot_column = []
    residual_plot = []
    weighted_residual_plot = []
    cont_combos = list(itertools.combinations(cont_predictors, 2))

    for i in cont_combos:
        pred1.append(i[0])
        pred2.append(i[1])
        plot_column.append(f"{i[0]} vs {i[1]}")
        residual_plot.append(f"{i[0]} vs {i[1]} residuals")
        weighted_residual_plot.append(f"{i[0]} vs {i[1]} weighted residuals")
        weighted.append(
            diff_mean_response_2d_cont(dataframe, i[0], i[1], response, True)
        )
        unweighted.append(
            diff_mean_response_2d_cont(dataframe, i[0], i[1], response, False)
        )

    # create table of weighted + unweighted (need to do plots for these as well)
    cont_table = pd.DataFrame(
        list(
            zip(
                pred1,
                pred2,
                weighted,
                unweighted,
                plot_column,
                residual_plot,
                weighted_residual_plot,
            )
        ),
        columns=[
            "Predictor 1",
            "Predictor 2",
            "weighted DMR",
            "unweighted DMR",
            "bin mean plot",
            "residual plot",
            "weighted residual plot",
        ],
    ).sort_values(by="weighted DMR", ascending=False)

    cont_table.to_html(
        "finalTables/cont_cont_brute_force_table.html",
        formatters={
            "bin mean plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "weighted residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
        },
        escape=False,
    )


def cont_cat_brute_force(dataframe, cont_predictors, cat_predictors, response):
    unweighted = []
    weighted = []
    pred1 = []
    pred2 = []
    plot_column = []
    residual_plot = []
    weighted_residual_plot = []
    cont_combos = list(itertools.product(cont_predictors, cat_predictors))

    for i in cont_combos:
        pred1.append(i[0])
        pred2.append(i[1])
        plot_column.append(f"{i[0]} vs {i[1]}")
        residual_plot.append(f"{i[0]} vs {i[1]} residuals")
        weighted_residual_plot.append(f"{i[0]} vs {i[1]} weighted residuals")
        weighted.append(
            diff_mean_response_cont_cat_2d(dataframe, i[0], i[1], response, True)
        )
        unweighted.append(
            diff_mean_response_cont_cat_2d(dataframe, i[0], i[1], response, False)
        )

    # create table of weighted + unweighted
    cont_table = pd.DataFrame(
        list(
            zip(
                pred1,
                pred2,
                weighted,
                unweighted,
                plot_column,
                residual_plot,
                weighted_residual_plot,
            )
        ),
        columns=[
            "Predictor 1",
            "Predictor 2",
            "weighted DMR",
            "unweighted DMR",
            "bin mean plot",
            "residual plot",
            "weighted residual plot",
        ],
    ).sort_values(by="weighted DMR", ascending=False)

    cont_table.to_html(
        "finalTables/cont_cat_brute_force_table.html",
        formatters={
            "bin mean plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "weighted residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
        },
        escape=False,
    )


def cat_cat_brute_force(dataframe, cat_predictors, response):
    unweighted = []
    weighted = []
    pred1 = []
    pred2 = []
    plot_column = []
    residual_plot = []
    weighted_residual_plot = []
    cont_combos = list(itertools.combinations(cat_predictors, 2))

    for i in cont_combos:
        pred1.append(i[0])
        pred2.append(i[1])
        plot_column.append(f"{i[0]} vs {i[1]}")
        residual_plot.append(f"{i[0]} vs {i[1]} residuals")
        weighted_residual_plot.append(f"{i[0]} vs {i[1]} weighted residuals")
        weighted.append(
            diff_mean_response_cat_cat_2d(dataframe, i[0], i[1], response, True)
        )
        unweighted.append(
            diff_mean_response_cat_cat_2d(dataframe, i[0], i[1], response, False)
        )

    # create table of weighted + unweighted
    cont_table = pd.DataFrame(
        list(
            zip(
                pred1,
                pred2,
                weighted,
                unweighted,
                plot_column,
                residual_plot,
                weighted_residual_plot,
            )
        ),
        columns=[
            "Predictor 1",
            "Predictor 2",
            "weighted DMR",
            "unweighted DMR",
            "bin mean plot",
            "residual plot",
            "weighted residual plot",
        ],
    ).sort_values(by="weighted DMR", ascending=False)

    cont_table.to_html(
        "finalTables/cat_cat_brute_force_table.html",
        formatters={
            "bin mean plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
            "weighted residual plot": lambda x: f'<a href="{x}.html">{x}</a>',
        },
        escape=False,
    )


def run_all(dataframe, predictors, response):
    # first need to split dataset on predictors in list between categoricals and continuous
    categoricals = []
    continuous = []
    for i in predictors:
        if is_continuous(dataframe, i):
            continuous.append(i)
        else:
            categoricals.append(i)

    # next calculate correlation metrics between all predictors (can assume all categoricals are nominal)
    # first do all continuous-continuous pairs, this function will create a "continuous_predictors_table" html file
    cont_cont_correlation(dataframe, continuous, response)

    # next, do continuous-categorical pairs, this function will create a "cat_cont_predictors_table" html file
    # which contains the table and all linking plots
    cont_cat_correlation(dataframe, continuous, categoricals, response)

    # lastly, do categorical-categorical, will create html file "cat_predictors_table.html"
    cat_cat_correlation(dataframe, categoricals, response)

    # continuous-continuous correlation matrix heatmap, will open in browser
    if len(continuous) == 0:
        print(
            "No continuous predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cont_cont_heatmap(continuous, dataframe)

    # Continuous-Categorical correlation matrix heatmap, will open in browser
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    elif len(continuous) == 0:
        print(
            "No continuous predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cont_cat_heatmap(categoricals, continuous, dataframe)

    # Categorical-Categorical correlation matrix heatmap, heatmap will open in browser
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, skipping cat-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cat_cat_heatmap(categoricals, dataframe)

    # before brute force, check if response is numeric in order to correctly perform brute force
    if ~is_numeric_dtype(dataframe[response]):
        values = list(set(dataframe[response].values))
        encoded_series = dataframe[response].replace([values[0], values[1]], [0, 1])
        dataframe[response] = encoded_series

    # brute force for continuous - continuous will output html file "cont_cont_brute_force_table.html"
    cont_cont_brute_force(dataframe, continuous, response)

    # brute force for continuous - categorical, will output html file "cont_cat_brute_force_table.html"
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, cont cat brute force table",
            file=sys.stderr,
        )
    else:
        cont_cat_brute_force(dataframe, continuous, categoricals, response)

    # brute force for categorical - categorical, will output html file called, "cat_cat_brute_force_table.html"
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, skipping cat-cat brute force table",
            file=sys.stderr,
        )
    else:
        cat_cat_brute_force(dataframe, categoricals, response)


def main(dataframe, predictors, response):

    # first need to split dataset on predictors in list between categoricals and continuous
    categoricals = []
    continuous = []
    for i in predictors:
        if is_continuous(dataframe, i):
            continuous.append(i)
        else:
            categoricals.append(i)

    # next calculate correlation metrics between all predictors (can assume all categoricals are nominal)
    # first do all continuous-continuous pairs, this function will create a "continuous_predictors_table" html file
    cont_cont_correlation(dataframe, continuous, response)

    # next, do continuous-categorical pairs, this function will create a "cat_cont_predictors_table" html file
    # which contains the table and all linking plots
    cont_cat_correlation(dataframe, continuous, categoricals, response)

    # lastly, do categorical-categorical, will create html file "cat_predictors_table.html"
    cat_cat_correlation(dataframe, categoricals, response)

    # continuous-continuous correlation matrix heatmap, will open in browser
    if len(continuous) == 0:
        print(
            "No continuous predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cont_cont_heatmap(continuous, dataframe)

    # Continuous-Categorical correlation matrix heatmap, will open in browser
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    elif len(continuous) == 0:
        print(
            "No continuous predictors in dataset, skipping cont-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cont_cat_heatmap(categoricals, continuous, dataframe)

    # Categorical-Categorical correlation matrix heatmap, heatmap will open in browser
    if len(categoricals) == 0:
        print(
            "No categorical predictors in dataset, skipping cat-cat corr matrix",
            file=sys.stderr,
        )
    else:
        cat_cat_heatmap(categoricals, dataframe)

    # before brute force, check if response is numeric in order to correctly perform brute force
    if ~is_numeric_dtype(dataframe[response]):
        values = list(set(dataframe[response].values))
        encoded_series = dataframe[response].replace([values[0], values[1]], [0, 1])
        dataframe[response] = encoded_series

    # brute force for continuous - continuous will output html file "cont_cont_brute_force_table.html"
    cont_cont_brute_force(dataframe, continuous, response)

    # brute force for continuous - categorical, will output html file "cont_cat_brute_force_table.html"
    cont_cat_brute_force(dataframe, continuous, categoricals, response)

    # brute force for categorical - categorical, will output html file called, "cat_cat_brute_force_table.html"
    cat_cat_brute_force(dataframe, categoricals, response)


if __name__ == "__main__":
    #  this loop will delete any existing html file in the current working directory to keep directory clean
    for f in os.listdir(os.getcwd()):
        if not f.endswith(".html"):
            continue
        os.remove(os.path.join(os.getcwd(), f))

    df, predictors, response = get_test_data_set()
    main(df, predictors, response)
