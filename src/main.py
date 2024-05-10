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





class RatDataHighGlc(RatData):
    """Data Object collected from a mouse under high iso.

            Attributes:
                iso: glucose level

            Representation Invariants:
                iso == "glc_high"
            """
    # Attribute types
    glc: str

    def __init__(self, id: int, gender: str, genetics: str, metabolite: dict) -> None:
        super().__init__(id, gender, genetics, metabolite)
        self.glc = "glc_high"



class RatDataLowGlc(RatData):
    """Data Object collected from a mouse under low iso.

                Attributes:
                    iso: T for high iso, F for low iso

                Representation Invariants:
                    iso == "glc_low"
                """
    # Attribute types
    glc: str

    def __init__(self, id: int, gender: str, genetics: str, metabolite: dict) -> None:
        super().__init__(id, gender, genetics, metabolite)
        self.glc = "glc_low"



def read_csv(filename: str, id: int, gender: str, genetics: str, glc: bool) -> RatData:
    if glc:
        rat_data = RatDataHighGlc(id, gender, genetics, {})
    else:
        rat_data = RatDataLowGlc(id, gender, genetics, {})

    with open(filename, 'r') as file:
        reader = csv.reader(file)
        data_rows = list(reader)
        for i in range(2, len(data_rows[0], 3)):
            name = data_rows[0][i] + rat_data.glc
            value = [(name, float(data_rows[1][i])), ((data_rows[0][i+1] + rat_data.glc), int(data_rows[1][i+1])),
                     ((data_rows[0][i+2] + rat_data.glc), float(data_rows[1][i+2]))]
            rat_data.metabolites[name] = value

    return rat_data

def write_csv(rat_high: list[RatData], rat_low: list[RatData], filename: str) -> None:

    with open(filename, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)

        writer.writeheader()

        writer.writerows(mydict)


def main():
    folder = "C:\Users\Imaris Ryzen\Downloads\MRS"
    rats_high = []
    rats_low = []

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