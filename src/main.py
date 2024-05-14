import csv
import os

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class RatData:
    """Data Object collected from 1 mouse.

        Attributes:
                id: the id of mouse.
                gender: the gender of mouse.
                genetics: whether the mouse is Tg, TgAD or nTg.
                metabolite: keys are the metabolite's name, value is a list of [concentration, %SD, /Cr+PCr]

            Representation Invariants:
                genetics in {Tg, nTg, TgAD}
            """
    # Attribute types
    id: str
    gender: str
    genetics: str
    metabolite: dict[str, list[int, int, float]]

    def __init__(self, rat_id: str, gender: str, genetics: str, metabolites: dict) -> None:
        self.iso = None
        self.id = rat_id
        self.gender = gender
        self.genetics = genetics
        self.metabolites = metabolites


class RatDataHighIso(RatData):
    """Data Object collected from a mouse under high iso.

            Attributes:
                iso:

            Representation Invariants:
                iso == "iso_high"
            """
    # Attribute types
    iso: str

    def __init__(self, rat_id: str, gender: str, genetics: str, metabolites: dict) -> None:
        super().__init__(rat_id, gender, genetics, metabolites)
        self.iso = "iso_high"


class RatDataLowIso(RatData):
    """Data Object collected from a mouse under low iso.

                Attributes:
                    iso: Isoflurane level

                Representation Invariants:
                    iso == "iso_low"
                """
    # Attribute types
    iso: str

    def __init__(self, rat_id: str, gender: str, genetics: str, metabolites: dict) -> None:
        super().__init__(rat_id, gender, genetics, metabolites)
        self.iso = "iso_low"


def read_csv(filename: str, rat_id: str, gender: str, genetics: str, iso: bool):
    if iso:
        rat_data = RatDataHighIso(rat_id, gender, genetics, {})
    else:
        rat_data = RatDataLowIso(rat_id, gender, genetics, {})

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data_rows = list(reader)
        for i in range(2, len(data_rows[0]), 3):
            value = [(data_rows[0][i].strip() + " " + rat_data.iso, float(data_rows[1][i])),
                     ((data_rows[0][i + 1].strip() + " " + rat_data.iso), int(data_rows[1][i + 1])),
                     ((data_rows[0][i + 2].strip() + " " + rat_data.iso), float(data_rows[1][i + 2]))]
            rat_data.metabolites[data_rows[0][i].strip()] = value

    return rat_data


def write_csv(rat_high: list[RatData], rat_low: list[RatData], path: str) -> None:
    filename = path + '/' + "MRS_Data.csv"

    if len(rat_high) < 1 or len(rat_low) < 1:
        print("No rat data available")
        return

    fields = ["Id", "Genotype", "Gender"]
    rats_data = []
    plot_data = {'Genotype': [], "iso": []}

    rat_high_field = list(rat_high[0].metabolites.keys())
    for i in range(len(rat_high_field)):
        plot_data[rat_high_field[i]] = []
        for j in range(3):
            fields.append(rat_high[0].metabolites[rat_high_field[i]][j][0])
            fields.append(rat_low[0].metabolites[rat_high_field[i]][j][0])

    for k in range(len(rat_high)):
        rat_data = {'Id': rat_high[k].id, 'Gender': rat_high[k].gender, 'Genotype': rat_high[k].genetics}
        plot_data['Genotype'].append(rat_high[k].genetics)
        plot_data['Genotype'].append(rat_high[k].genetics)
        plot_data["iso"].append(rat_high[k].iso)
        plot_data["iso"].append(rat_low[k].iso)
        for item in rat_high_field:
            plot_data[item].append(rat_high[k].metabolites[item][0][1])
            plot_data[item].append(rat_low[k].metabolites[item][0][1])
            for m in range(3):
                rat_data[rat_high[k].metabolites[item][m][0]] = rat_high[k].metabolites[item][m][1]

        rats_data.append(rat_data)

    for field in rat_high_field:
        boxplot(plot_data, field, path)

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()

        writer.writerows(rats_data)


def boxplot(data, metabolite: str, path: str) -> None:
    figsize = (1.25, 3)
    theme = "whitegrid"
    palette_geno = ['olivedrab', 'darkorange']
    title = "20"
    label = 18
    tick = 15

    plt.figure(figsize=figsize)
    sns.set_theme(style=theme)

    data = pd.DataFrame(data)
    print(data)
    genotypes = ["nTg", "Tg", "TgAD"]
    x = 'Genotype'
    y = metabolite
    y_lim = (0, 7)

    # data = [[], [], []]
    # for item in rat_data:
    #     if item.iso == iso:
    #         if item.genetics == "nTg":
    #             data[0].append(item.metabolites[metabolite][0])
    #         elif item.genetics == "Tg":
    #             data[1].append(item.metabolites[metabolite][0])
    #         else:
    #             data[2].append(item.metabolites[metabolite][0])
    # max_len = max(map(len, data))
    # for i in range(len(data)):
    #     while len(data[i]) < max_len:
    #         data[i].append(None)
    #
    # rat_dict = {"nTg": data[0], "Tg": data[1], "TgAD": data[2]}
    # data = pd.DataFrame(rat_dict)

    ax = sns.boxplot(x=x, y=y, data=data, hue="iso", order=genotypes, palette=palette_geno, showmeans=True,
                     meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                "markersize": "5"})
    ax = sns.stripplot(data=data, order=genotypes, marker="o", alpha=1, color="black", dodge=0.1)

    plt.title("{} concentration for different genotype mice\n".format(metabolite), fontsize=title)
    ax.set_xlabel("Genotype", fontsize=label)
    ax.set_ylabel("Concentration (mmol)", fontsize=label)
    ax.set_xticklabels(genotypes, size=tick)

    # ax.legend_.remove()

    plt.savefig('{}/{}_no_filter.png'.format(path, metabolite), dpi=300, bbox_inches='tight')


def main():
    output_csv = "C:/Users/Imaris Ryzen/Downloads/MRS"
    rats_high = []
    rats_low = []

    for name in os.listdir(output_csv):
        sub_folder = output_csv + '/' + name
        if os.path.isdir(sub_folder):
            lst = name.strip().split('_')
            rat_id = lst[1]
            genetics = lst[6]
            gender = lst[7]

            for iso in os.listdir(sub_folder):
                if os.path.isdir(sub_folder + '/' + iso):
                    input_csv = sub_folder + '/' + iso + '/' + "spreadsheet.csv"
                    if "high" in iso:
                        rats_high.append(read_csv(input_csv, rat_id, gender, genetics, True))
                    else:
                        rats_low.append(read_csv(input_csv, rat_id, gender, genetics, False))
                else:
                    continue

        else:
            continue

    write_csv(rats_low, rats_high, output_csv)

    print("Conversion Completed, file saved at {}".format(output_csv))


if __name__ == "__main__":
    main()
