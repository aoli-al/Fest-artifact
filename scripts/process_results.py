import os
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
import math

bms = [
    "random-origin",
    "pct15-origin",
    "feedbackpct15-origin",
    "feedbackpct15-origin-no-scen",
    "pct3-origin",
    "feedbackpct3-origin",
    "feedbackpct3-origin-no-scen",
    # "feedbackpct3-origin-no-prio",
    "pct50-origin",
    "feedbackpct50-origin",
    "feedbackpct50-origin-no-scen",
    "pos-origin",
    "feedbackpos-origin",
    "feedbackpos-origin-no-scen",
    "pos-conflict-analysis",
    "feedbackpos-conflict-analysis",
    "feedbackpos-ca-no-scen",
    "rl-origin",
    # "surw-origin",
    # "feedbacksurw-origin"
]

def generate_aggregated_plot(df: pd.DataFrame):
    column = "coverage"
    sns.set(rc={'figure.figsize':(6,3)})
    fest_key = "$\\textsc{Fest}$\n$\\mathrm{PCT15}$"
    df["diff"] =  df[fest_key] / df["NoPrio"]
    print((df["diff"] > 1).value_counts())
    df = df.sort_values('diff')
    # display(df["diff"])
    # display(df["name"])
    print(df["diff"].describe())

    ax = sns.barplot(data=df, x="name", y="diff")
    ax.set_xlabel("Benchmarks")
    ax.set_ylabel("Timeline Coverage Improvement")
    ax.axhline(1.0, linestyle='--', color='red', label="NoPrio")
    ax.set_ylim((0.0, 2.1))
    ax.set_yticks((0.5, 1, 1.5, 2))
    ax.set_yticklabels(("$0.5\\times$", "$1\\times$", "$1.5\\times$", "$\geq 2\\times$"))

    ax.set_xticklabels([])
    with_string_view_line = mlines.Line2D([], [], color='#2A587A', marker='o', linestyle='-', label='Fest')
    without_string_view_line = mlines.Line2D([], [], color='red', linestyle='--', label='NoPrio')
    ax.legend(handles=[with_string_view_line, without_string_view_line])
    return ax

def read_many_and_merge(test_names, ignore_60=False, bm_filter=bms):
    dfs = []
    for test_name in test_names:
        df, _, _ = read_and_display(test_name, ignore_60, bm_filter)
        dfs.append(df)
    return pd.concat(dfs)

def read_and_display(test_name: str, ignore_60=False, bm_filter=bms):
    # test_name = "/data/aoli/p-feedback/oe/"
    total_result = []
    ranked_result = {}
    total_benches = 0


    visited = set()
    completed_results = find_complete_results(test_name, bm_filter)
    cov_info, cov_final, bug_info = extract_cov_info(test_name, completed_results)
    result_table = []
    bug_result_table = []
    valid_tests = set()

    for test, data in cov_info.items():
        idx = data.groupby("tech")["cov_timeline"].idxmax()
        max_rows = data.loc[idx]
        result_dict = max_rows.set_index('tech')['cov_timeline'].to_dict()
        has_empty = False
        for k, v in cov_final[test].items():
            if len(v) == 0:
                has_empty = True
                break
        if has_empty:
            continue

        result_dict = {tech_rename(k, True): int(sum(v) / len(v)) for k, v in cov_final[test].items() }
        bug_dict = {tech_rename(k, False): v for k, v in bug_info[test].items() }

        sorted_result = sorted(result_dict.values())
        sorted_result.reverse()
        total_benches += 1
        if sorted_result[0] < 60 and ignore_60:
            continue
        valid_tests.add(test)
        for key, value in result_dict.items():
            idx = sorted_result.index(value)
            total_result.append((key, idx))
            if key not in ranked_result:
                ranked_result[key] = {}
            if idx not in ranked_result[key]:
                ranked_result[key][idx] = 0
            ranked_result[key][idx] += 1
        result_table.append({"name": test, **result_dict})
        if sum(list(bug_dict.values())) != 0:
            bug_result_table.append({"name": test, **bug_dict})

    df = pd.DataFrame(result_table)
    bug_df = pd.DataFrame(bug_result_table)
    return df, ranked_result, bug_df

# Define a function to apply LaTeX formatting with color for max values
def highlight_max(style):
    def f(s):
        is_max = s == s.max()
        return [style if v else '' for v in is_max]
    return f

TECHs = ["PCT3", "PCT15", "PCT50", "POS", "POS+",
          "QL"
         ]
name_dict = {}
name_map = {}
def get_name(name: str):
    # return name
    prefix = ""
    if name.startswith("TwoPhaseCommit"):
        prefix = "TwoPhaseCommit"
    if name.startswith("German"):
        prefix = "German"
    if name.startswith("OSR"):
        prefix = "OSR"
    if name.startswith("paxos"):
        prefix = "Paxos"
    if name.startswith("tc"):
        prefix = "3FS"
    if not prefix:
        return None
    global name_dict
    if prefix not in name_dict:
        name_dict[prefix] = 0
    name_dict[prefix] += 1
    new_name = f"{prefix}{name_dict[prefix]:02}"
    name_map[name] = new_name
    return f"{prefix}{name_dict[prefix]:02}"


def visualize_dfs(df):
    sns.set(rc={'figure.figsize':(6,3)})
    improved = pd.DataFrame()
    improved['name'] = df['name']
    print(len(df))
    for tech in TECHs:
        if tech == "QL":
            continue
        fest_key = "$\\textsc{Fest}$\n$\\mathrm{" + tech + "}$"
        new_key = "$\\textsc{Fest}_\\mathrm{" + tech + "}\\ vs.\\ \\mathrm{" + tech + "}$"
        df[tech] = df[tech].clip(lower=1)
        improved[new_key] = (df[fest_key] - df[tech]) / df[tech]
        print(tech)
        print("no improvements: ", (improved[new_key] < 0).value_counts())
        print("mean improvements", improved[new_key].mean())
        print("max improvements", max(improved[new_key]))
    melted_df = improved.melt(id_vars=['name'], var_name='Comparison', value_name='Improvements of Timeline Coverage')
    filtered = melted_df[melted_df["Improvements of Timeline Coverage"] < 0]
    print("improvements stats:")
    print(melted_df['Improvements of Timeline Coverage'].describe())
    print("degrataion stats:")
    print(filtered.describe())
    # sns.violinplot(data=melted_df, x="technique", y="value")
    # sns.violinplot(x=melted_df["value"])
    # melted_df = melted_df[abs(melted_df['Improvement']) > 0.1]
    g = sns.ecdfplot(data=melted_df, x="Improvements of Timeline Coverage", hue="Comparison")
    for lines, linestyle, legend_handle in zip(g.lines[::-1], ['-', '--', ':', "-.", (5, (10, 3))], g.get_legend_handles_labels()[0]):
        lines.set_linestyle(linestyle)
        legend_handle.set_linestyle(linestyle)

    g.set(xlim=(-1, 50))
    plt.xscale('symlog')
    plt.xticks([-0.5, 0, 1, 10], ["-0.5x", "0x", "1x", "10x"])
    fig = g.get_figure()

def visualize_max(df, path):
    sns.set(rc={'figure.figsize':(6,3)})
    df = df.drop(["name"], axis=1)
    max_counts = {}

    # Iterate through each row in the dataframe
    for _, row in df.iterrows():
        # Find the maximum value in the row
        max_value = row.max()
        # Find all columns with the maximum value
        max_columns = row[row == max_value].index

        # Increment the count for each column with the max value
        for col in max_columns:
            if col in max_counts:
                max_counts[col] += 1
            else:
                max_counts[col] = 1

    # max_df = df.idxmax(axis=1, numeric_only=True).value_counts().reset_index()
    # max_df.columns = ["Technique", "Best Performance Count"]
    max_df = pd.DataFrame(list(max_counts.items()), columns=["Technique", "Best Performance Count"])
    max_df = max_df.sort_values("Best Performance Count", ascending=False).reset_index()
    display(max_df)

    g = sns.barplot(max_df, x="Technique", y="Best Performance Count")
    fig = g.get_figure()
    fig.savefig(os.path.join(path), bbox_inches='tight')




def df_to_latex(df, show_no_scen=False):
    fest_cols = [col for col in df.columns if 'Fest' in col]
    non_fest_cols = [col for col in df.columns if 'Fest' not in col and col != 'name']
    rs = "rrr" if show_no_scen else "rr"

    latex_str = "\\begin{tabular}{l|" + f"{rs}|{rs}|{rs}|{rs}|{rs}" + """|r}
    \\toprule
    """
    for tech in TECHs:
        if tech == "QL":
            latex_str += "& QL"
        else:
            if show_no_scen:
                latex_str += " & \\multicolumn{3}{c}{" + tech + "}"
            else:
                latex_str += " & \\multicolumn{2}{c}{" + tech + "}"
    latex_str += "\\\\\n Name"
    for tech in TECHs:
        if tech == "QL":
            latex_str += "& "
        else:
            if show_no_scen:
                latex_str += "& Ori & No-Scen & {\\systemname}"
            else:
                latex_str += "& Ori & {\\systemname}"
    latex_str += "\\\\\n"
    lines = []
    improve_count = 0
    max_count = 0
    improve_average = []
    global name_dict
    name_dict = {}
    for k, row in df.iterrows():
        if show_no_scen:
            latex_row = get_title_short(row["name"])
        else:
            latex_row = get_name(row["name"])
            # if row["name"] not in BM_MAP:
            #     latex_row = row["name"]
            # else:
            #     latex_row = BM_MAP[row["name"]]
        del row["name"]
        # row = row.drop(columns=["name"])
        max_value = max(row.values)
        for tech in TECHs:
            ori_field = f"{int(row[tech])}"
            if row[tech] == max_value:
                ori_field = "\\color{red!80} \\bfseries " + ori_field
            if tech == "QL":
                latex_row += f"& {ori_field}"
                continue
            if show_no_scen:
                no_scen_key = "$\\textsc{Fest-}$\n$\\mathrm{" + tech + "}$"
                # no_scen_key = "NoScen"
                no_scen_field = f"{row[no_scen_key]}"
                if row[no_scen_key] == max_value:
                    no_scen_field = "\\color{red!80} \\bfseries " + no_scen_field
            fest_key = "$\\textsc{Fest}$\n$\\mathrm{" + tech + "}$"
            fest_field = f"{row[fest_key]}"
            if row[fest_key] >= row[tech]:
                fest_field = "\\cellcolor{cyan!40} " + fest_field
                improve_count += 1
            if row[fest_key] == max_value:
                fest_field = "\\color{red!80} \\bfseries " + fest_field
                max_count += 1
            if (row[tech] > 0):
                improve_average.append((row[fest_key] - row[tech]) / row[tech])
            if show_no_scen:
                latex_row += f"& {ori_field} & {no_scen_field} & {fest_field}"
            else:
                latex_row += f"& {ori_field} & {fest_field}"
        latex_row += "\\\\\n"
        lines.append(latex_row)
    lines = sorted(lines)
    latex_str += "".join(lines)
    latex_str += "\\end{tabular}"

    print(len(improve_average))
    print(sum(improve_average) / len(improve_average))
    print(max(improve_average))
    print(improve_count)
    print(max_count)
    print(latex_str)




# for key, value in ranked_result.items():


def find_complete_results(path: str, techniques):
    results = {}
    for f in os.scandir(path):
        if f.is_dir():
            test_name = f.path.split("/")[-1]
            for rep in range(5):
                if os.path.exists(os.path.join(f.path, str(rep), "stdout.txt")):
                    test_case_name = get_test_case_name(test_name)
                    technique_name = get_technique_name(test_name)
                    if technique_name not in techniques:
                        continue
                    if test_case_name not in results:
                        results[test_case_name] = {}
                    if technique_name not in results[test_case_name]:
                        results[test_case_name][technique_name] = []
                    results[test_case_name][technique_name].append(str(rep))
    return results

def tech_rename(tech, newline=True):
    # if "pct" in te
    # if ""
    # return tech
    is_fest = False
    no_scen = False
    if "feedback" in tech:
        is_fest = True
        if "no-scen" in tech:
            no_scen = True
        else:
            no_scen = False
        if "no-prio" in tech:
            no_prio = True
        else:
            no_prio = False
    tech_name = ""

    if "pct" in tech:
        pattern = re.compile(r"pct(\d+)")
        bound = int(pattern.search(tech).group(1))
        tech_name = f"PCT{bound}"

    elif "rl-origin" in tech:
        return "QL"
    elif "random-origin" in tech:
        return "RW"
    elif "surw" in tech:
        tech_name = "SURW"
    else:
        tech_name = "POS"
        if "conflict-analysis" in tech or "-ca-" in tech:
            tech_name += "+"
    if is_fest:
        if no_scen:
            return "NoScen"
            # return "$\\textsc{Fest-}$\n$\\mathrm{" + tech_name + "}$"
        if no_prio:
            return "NoPrio"
        if newline:
            return "$\\textsc{Fest}$\n$\\mathrm{" + tech_name + "}$"
        else:
            return "$\\textsc{Fest}_\\mathrm{" + tech_name + "}$"
    else:
        return tech_name
    if "feedbackpct15-origin" in tech:
        return "$\\textsc{Fest}_\\mathrm{PCT}$"
    if "feedback-origin" in tech:
        return "$\\textsc{Fest}_\\mathrm{RW}$"
    if "pct15-origin" in tech:
        return "PCT"
    if "feedbackpct15-pos" in tech :
        return "$\\textsc{Fest}_\\mathrm{POS}$"
    if "pct15-pos" in tech:
        return "POS"
    if "feedbackpct15-no-pattern" in tech:
        return "\sc{Feedback-No-Scene}"
    if "feedbackpct15-no-priority" in tech:
        return "\sc{Feedback-No-Priority}"
    if "rl-feedback" in tech:
        return "RL"
    if "rl-no-diversity" in tech:
        return "RL2"
    if "random-origin" in tech:
        return "RW"
    if "rff" in tech:
        return "RFF"
    print(tech)


def extract_cov_info(path, results: dict):
    cov_pattern = re.compile(r"Elapsed: ([0-9]*[.][0-9]+), # timelines: (\d+)")
    final_cov_pattern = re.compile(r"Explored (\d+) timeline")
    total_time_pattern = re.compile(r"Elapsed ([0-9]+).[0-9]+ sec.")
    cov_info = {}
    cov_final = {}
    bug_info = {}
    for test_case_name in sorted(results.keys()):
        technique_and_iter = results[test_case_name]
    # for test_case_name, technique_and_iter in results.items():
        cov_all = []
        cov_final[test_case_name] = {}
        bug_info[test_case_name] = {}
        for tech, iters in technique_and_iter.items():
            cov_final[test_case_name][tech] = []
            bug_found = 0
            for iter in iters:
                cov_result = [[0, 0, tech_rename(tech), 0]]
                max_covered_timeline = 0
                final_cov = 0
                total_time = 0
                with open(os.path.join(path, f"{test_case_name}-{tech}", iter, "stdout.txt")) as f:
                    for line in f:
                        if "triggered bug #1" in line:
                            bug_found = 1
                        matched = cov_pattern.search(line)
                        if matched:
                            time = float(matched.group(1))
                            covered_timeline = int(matched.group(2))
                            max_covered_timeline = max(max_covered_timeline, covered_timeline)
                            cov_result.append([time, covered_timeline, tech_rename(tech), 0])
                            final_cov = max(final_cov, covered_timeline)
                        final_cov_matched = final_cov_pattern.search(line)
                        if final_cov_matched:
                            final_cov = int(final_cov_matched.group(1))
                            max_covered_timeline = final_cov
                        total_time_matched = total_time_pattern.search(line)
                        if total_time_matched:
                            total_time = int(total_time_matched.group(1))
                if final_cov != 0 and total_time != 0:
                    cov_result.append([total_time, final_cov, tech_rename(tech), 0])
                else:
                    continue
                data = pd.DataFrame(cov_result, columns=['iter', "cov_timeline", "tech", "valid_schedules"])
                data["iter"] = data["iter"].astype(int) // 60
                data = data.copy().drop_duplicates(keep='first', subset=["iter"])
                data = data.set_index("iter").reindex(range(0, 70)).infer_objects(copy=False)
                data = data.ffill()
                data = data.reset_index()
                data["iter"] = data["iter"]
                cov_all.append(data.head(70))
                cov_final[test_case_name][tech].append(max_covered_timeline)
            bug_info[test_case_name][tech] = bug_found
        if cov_all:
            cov_info[test_case_name] = pd.concat(cov_all)
    return cov_info, cov_final, bug_info


models = {}
patterns = {}

def get_title_short(test_name):
    # return test_name
    global models
    global patterns
    return test_name

def get_title(test_name):
    global models
    global patterns
    model, pattern = test_name.split("-")
    return test_name


    if model not in models:
        models[model] = f"M{len(models)}"
        patterns[model] = {}
    m = models[model]
    if pattern not in patterns[model]:
        patterns[model][pattern] = f"P{len(patterns[model])}"
    p = patterns[model][pattern]
    return f"{m}-{p}"

def visualize_cov_info_bar(data, path):
    sns.set(rc={'figure.figsize':(6,3)})
    axis = sns.barplot(data, x="Benchmark", y="Result", hue="Technique", hue_order=sorted(data['Technique'].unique()))
    # axis.set_yscale("log")
    axis.set(xlabel = "Benchmark")
    axis.set_xlabel("Benchmark")
    axis.set_ylabel("Scenario Coverage")
    pattern = ['-', '*', 'x']
    hatches= ['-', '*', 'x']
    # hatches=np.repeat(pattern,7)

    for container, hatch, handle in zip(axis.containers, hatches, axis.get_legend().legend_handles):
        # update the hatching in the legend handle
        handle.set_hatch(hatch)

        # iterate through each rectangle in the container
        for rectangle in container:

            # set the rectangle hatch
            rectangle.set_hatch(hatch)



    # for pat,bar in zip(hatches, axis.patches):
    #     bar.set_hatch(pat)
    # sns.move_legend(axis, "upper right")
    sns.move_legend(
    axis, "lower center",
    bbox_to_anchor=(.5, 1), ncol=3, title=None, frameon=False, fontsize=14
)
    fig = axis.get_figure()
    fig.savefig(os.path.join(path), bbox_inches='tight')


def visualize_cov_info_single(data, test_name, path):
    visualize_cov_info(data, test_name, path, plt.gca(), 6)
    plt.gca().legend(ncol=4, loc='upper center', bbox_to_anchor=(1, 1.55))
    plt.show()

def visualize_cov_info(data, test_name, path, ax, idx, suffix=""):
    axis = sns.lineplot(ax=ax, x="iter", y="cov_timeline", hue='tech', style='tech',
                    hue_order=sorted(data['tech'].unique()),
                    style_order=sorted(data['tech'].unique()), data=data)
    if idx // 2 == 3:
        axis.set(xlabel = "Time (min)")
    else:
        axis.set(xlabel = "")
    if idx % 2 == 0:
        axis.set(ylabel = "Scenario Coverage")
    else:
        axis.set(ylabel = "")

    title = get_title(test_name)
    axis.set(title = title)
    # fig = axis.get_figure()
    axis.legend([], [], frameon=False)
    # plt.legend(title='', loc='upper left')
    # fig.savefig(os.path.join(path, title + suffix +".pdf"), bbox_inches='tight')
    # plt.show()

def visualize_input_info(data, test_name):
    axis = data.set_index("tech").plot(kind="bar", stacked=True)
    axis.set(ylabel = "# Input")
    axis.set(xlabel = "Algorithm")
    axis.set(title = test_name)
    plt.show()





def get_test_case_name(test_name: str):
    return "-".join(test_name.split("-")[0:1])


def get_technique_name(test_name: str):
    return "-".join(test_name.split("-")[1:])
