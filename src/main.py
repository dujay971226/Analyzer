import csv
import os

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
    id: int
    gender: str
    genetics: str
    metabolite: dict[str, list[int, int, float]]

    def __init__(self, id: int, gender: str, genetics: str, metabolite: dict) -> None:
        self.id = id
        self.gender = gender
        self.genetics = genetics
        self.metabolite = metabolite





class RatDataHighiso(RatData):
    """Data Object collected from a mouse under high iso.

            Attributes:
                iso:

            Representation Invariants:
                iso == "iso_high"
            """
    # Attribute types
    iso: str

    def __init__(self, id: int, gender: str, genetics: str, metabolite: dict) -> None:
        super().__init__(id, gender, genetics, metabolite)
        self.iso = "iso_high"



class RatDataLowiso(RatData):
    """Data Object collected from a mouse under low iso.

                Attributes:
                    iso: Isoflurane level

                Representation Invariants:
                    iso == "iso_low"
                """
    # Attribute types
    iso: str

    def __init__(self, id: int, gender: str, genetics: str, metabolite: dict) -> None:
        super().__init__(id, gender, genetics, metabolite)
        self.iso = "iso_low"



def read_csv(filename: str, id: int, gender: str, genetics: str, iso: bool):
    if iso:
        rat_data = RatDataHighiso(id, gender, genetics, {})
    else:
        rat_data = RatDataLowiso(id, gender, genetics, {})

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data_rows = list(reader)
        for i in range(2, len(data_rows[0], 3)):
            value = [(data_rows[0][i] + "_" + rat_data.iso, float(data_rows[1][i])),
                     ((data_rows[0][i+1] + "_" + rat_data.iso), int(data_rows[1][i+1])),
                     ((data_rows[0][i+2] + "_" + rat_data.iso), float(data_rows[1][i+2]))]
            rat_data.metabolites[data_rows[0][i]] = value

    return rat_data

def write_csv(rat_high: list[RatData], rat_low: list[RatData], filename: str) -> None:

    if len(rat_high) < 1 or len(rat_low) < 1:
        print("No rat data available")
        return

    fields = ["Id", "Genotype", "Gender"]
    rats_data = []

    rat_high_field = rat_high[0].metabolites.keys()
    rat_low_field = rat_low[0].metabolites.keys()
    for i in range(len(rat_high_field)):
        for j in range(3):
            fields.append(rat_high[0].metabolites[rat_high_field[i]][j])
            fields.append(rat_low[0].metabolites[rat_low_field[i]][j])

    for k in range(len(rat_high)):
        rat_low_metab = rat_low[k].metabolites
        rat_high_metab = rat_high[k].metabolites
        rat_data = [rat_high[k].id, rat_high[k].gender, rat_high[k].genetics]
        for item in fields[3:]:
            rat_data.append(rat_high[k].metabolites[item])
            rat_data.append(rat_low[k].metabolites[item])
        rats_data.append(rat_data)


    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()

        writer.writerows(rats_data)


def main():
    folder = "C:\Users\Imaris Ryzen\Downloads\MRS"
    rats_high = []
    rats_low = []
    fields = []

    for name in os.listdir(folder):
        lst = name.strip().split('_')
        id = int(lst[1])
        genetics = lst[6]
        gender = lst[7]

        sub_folder = os.path.join(folder, name)
        if os.path.isdir(sub_folder):
            for iso in os.listdir(folder):
                root_folder = os.path.join(sub_folder, iso)
                input_csv = os.path.join(root_folder, "spreadsheet.csv")
                if "high" in iso:
                    rats_high.append(read_csv(input_csv, id, gender, genetics, True))
                else:
                    rats_low.append(read_csv(input_csv, id, gender, genetics,False))

        else:
            continue

    output_csv = "MRS_Data.csv"

    write_csv(rats_low, rats_high, output_csv)

    print("Conversion Completed, file saved at {}".format(folder))


if __name__ == "__main__":
    main()