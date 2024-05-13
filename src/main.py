import csv
import os
import numpy as np
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


def write_csv(rat_high: list[RatData], rat_low: list[RatData], filename: str) -> None:
    if len(rat_high) < 1 or len(rat_low) < 1:
        print("No rat data available")
        return

    fields = ["Id", "Genotype", "Gender"]
    rats_data = []

    rat_high_field = list(rat_high[0].metabolites.keys())
    for i in range(len(rat_high_field)):
        for j in range(3):
            fields.append(rat_high[0].metabolites[rat_high_field[i]][j][0])
            fields.append(rat_low[0].metabolites[rat_high_field[i]][j][0])

    for k in range(len(rat_high)):
        rat_data = {'Id': rat_high[k].id, 'Gender': rat_high[k].gender, 'Genotype': rat_high[k].genetics}
        for item in rat_high_field:
            rat_data[rat_high[k].metabolites[item][0][0]] = rat_high[k].metabolites[item][0][1]
            rat_data[rat_low[k].metabolites[item][0][0]] = rat_low[k].metabolites[item][0][1]
            rat_data[rat_high[k].metabolites[item][1][0]] = rat_high[k].metabolites[item][1][1]
            rat_data[rat_low[k].metabolites[item][1][0]] = rat_low[k].metabolites[item][1][1]
            rat_data[rat_high[k].metabolites[item][2][0]] = rat_high[k].metabolites[item][2][1]
            rat_data[rat_low[k].metabolites[item][2][0]] = rat_low[k].metabolites[item][2][1]
        rats_data.append(rat_data)

    total_data = rat_low + rat_high
    for field in rat_high_field:
        boxplot(total_data, field, "iso_low")
        boxplot(total_data, field, "iso_high")

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()

        writer.writerows(rats_data)


def boxplot(rat_data: list[RatData], metabolite: str, iso: str) -> None:
    figsize = (1.25, 3)
    theme = "whitegrid"
    palette_geno = ['olivedrab', 'darkorange']
    title = "20"
    label = 18
    tick = 15

    plt.figure(figsize=figsize)
    sns.set_theme(style=theme)

    data = {item.genetics: item.metabolites[metabolite][0] for item in rat_data if item.iso == iso}
    x = data.keys()
    y = data.items()
    y_lim = (0, 7)

    ax = sns.boxplot(x=x, y=y, data=data, order=["nTg", "Tg", "TgAD"], palette=palette_geno, showmeans=True,
                     meanprops={"marker": "o", "markerfacecolor": "white", "markeredgecolor": "black",
                                "markersize": "5"})
    ax = sns.stripplot(x=x, y=y, data=data, order=["nTg", "Tg", "TgAD"], marker="o", alpha=1, color="black", dodge=0.1)

    plt.title("{} Concentration for {}\n".format(metabolite, iso), fontsize=title)
    ax.set_xlabel("Genotype", fontsize=label)
    ax.set_ylabel("concentration (mmol)", fontsize=label)
    ax.set(ylim=y_lim)
    ax.set_xticklabels(["nTg", "Tg", "TgAD"], size=tick)

    # ax.legend_.remove()

    plt.savefig('plots/tau_pre_CHOW_nofilter.png', dpi=300, bbox_inches='tight')


def main():
    folder = "C:/Users/Imaris Ryzen/Downloads/MRS"
    rats_high = []
    rats_low = []

    for name in os.listdir(folder):
        sub_folder = folder + '/' + name
        if os.path.isdir(sub_folder):
            lst = name.strip().split('_')
            id = lst[1]
            genetics = lst[6]
            gender = lst[7]

            for iso in os.listdir(sub_folder):
                if os.path.isdir(sub_folder + '/' + iso):
                    input_csv = sub_folder + '/' + iso + '/' + "spreadsheet.csv"
                    if "high" in iso:
                        rats_high.append(read_csv(input_csv, id, gender, genetics, True))
                    else:
                        rats_low.append(read_csv(input_csv, id, gender, genetics, False))
                else:
                    continue

        else:
            continue

    output_csv = folder + '/' + "MRS_Data.csv"

    write_csv(rats_low, rats_high, output_csv)

    print("Conversion Completed, file saved at {}".format(folder))


if __name__ == "__main__":
    main()
