# for "gui"
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import Center
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Log
from textual_fspicker import FileOpen

import polars as pl
import os
import sys
import glob
import shutil
import subprocess
from datetime import datetime

# template brain directory location
# ideally, include in package
AFNI_DIR = os.path.expanduser("~") + "/.afni/data/suma_MNI152_2009/"


def make_temporary_directory(directory_name):
    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists. Removing.")
        shutil.rmtree(directory_name)
        make_temporary_directory(directory_name)
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
    except Exception as e:
        print(f"An error occurred: {e}")
    return directory_name


# main fuction for processing
def process_file(USER_SUPPLIED_DATA):
    directory = os.path.dirname(USER_SUPPLIED_DATA) + "/"
    csv_file_name = os.path.splitext(os.path.basename(USER_SUPPLIED_DATA))[0]
    # Temporary files dir
    date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    TEMP_FILES_DIR = directory + csv_file_name + "_EZSUMA_OUTPUT_" + date_time + "/"
    os.chdir(directory)
    # Load in user data
    data_for_SUMA = pl.read_csv(USER_SUPPLIED_DATA).drop_nans().drop_nulls()
    make_temporary_directory(TEMP_FILES_DIR)
    os.chdir(TEMP_FILES_DIR)
    # Array of values
    statistic_values = []
    for i in data_for_SUMA[:, 1]:
        statistic_values.append(i)
    count = 0
    for i in data_for_SUMA[:, 0]:
        subprocess.run(
            [
                "3dcalc",
                "-a",
                "Brainnetome_1.0:" + i,
                "-expression",
                str(statistic_values[count]) + "*a",
                "-prefix",
                i,
            ],
            capture_output=True,
            text=True,
        )
        count += 1
    regions = os.listdir()
    # merge the regions together, output = mrg+tlrc afni files
    merge_results = subprocess.run(
        ["3dmerge", "-gmax"] + regions, capture_output=True, text=True
    )
    # grow the regions modally
    grow_results = subprocess.run(
        [
            "@ROI_modal_grow",
            "-input",
            "mrg+tlrc.BRIK.gz",
            "-niters",
            "4",
            "-prefix",
            "Modal_Grow",
        ],
        capture_output=True,
        text=True,
    )
    # finally, turn to surface dataset for SUMA
    os.chdir("rmgrow/")
    # right hemisphere
    rh_vol_surf = subprocess.run(
        [
            "3dVol2Surf",
            "-spec",
            AFNI_DIR + "MNI152_2009_both.spec",
            "-surf_A",
            "rh.pial",
            "-grid_parent",
            "Modal_Grow.nii.gz",
            "-sv",
            "Modal_Grow.nii.gz",
            "-map_func",
            "mask",
            "-out_niml",
            "data_rh.niml.dset",
        ],
        capture_output=True,
        text=True,
    )
    # left
    lh_vol_surf = subprocess.run(
        [
            "3dVol2Surf",
            "-spec",
            AFNI_DIR + "MNI152_2009_both.spec",
            "-surf_A",
            "lh.pial",
            "-grid_parent",
            "Modal_Grow.nii.gz",
            "-sv",
            "Modal_Grow.nii.gz",
            "-map_func",
            "mask",
            "-out_niml",
            "data_lh.niml.dset",
        ],
        capture_output=True,
        text=True,
    )
    # cleaning up
    # interim_files
    for dset in glob.glob("*.dset"):
        shutil.move(dset, TEMP_FILES_DIR + dset)
    # go back to the original file directory
    os.chdir(TEMP_FILES_DIR)
    # open_SUMA()
    interim_files = make_temporary_directory(TEMP_FILES_DIR + "interim_files/")
    # moving afni region and original merge folder
    for brik in glob.glob(TEMP_FILES_DIR + "*.BRIK.gz"):
        shutil.move(brik, interim_files + os.path.basename(brik))
    for head in glob.glob(TEMP_FILES_DIR + "*.HEAD"):
        shutil.move(head, interim_files + os.path.basename(head))
    # moving rmgrow folder
    shutil.move(TEMP_FILES_DIR + "rmgrow", interim_files + "rmgrow")
    final_logs = (
        merge_results.stdout
        + grow_results.stdout
        + lh_vol_surf.stdout
        + rh_vol_surf.stdout
    )
    return final_logs


def map_electrodes(USER_SUPPLIED_DATA):
    # user_path =
    afni_output = subprocess.Popen(
        [
            "whereami_afni",
            "-coord_file",
            str(USER_SUPPLIED_DATA) + "'[0,1,2]'",
            "-max_areas",
            "1",
            "-tab",
            "-atlas",
            "Brainnetome_1.0",
        ],
        stdout=subprocess.PIPE,
    )
    coords_with_values = pl.read_csv(USER_SUPPLIED_DATA, has_header=False)
    # TODO add error handling for electrodes only
    csv_vals = coords_with_values[:, 3]
    grepped = subprocess.check_output(
        ("grep", "Brainnetome_1.0"), stdin=afni_output.stdout
    )
    afni_output.wait()
    # reads in output of whereami_afni command to polars df
    electrodes = pl.read_csv(grepped, separator="\t", has_header=False)
    # drops extraneous columns, bit clunky but afni_output should always have stuff in this position
    electrodes = electrodes.drop(["column_1", "column_2", "column_4", "column_5"])
    # combining afni regions with values given
    combined = electrodes.hstack([csv_vals])
    combined = combined.rename({"column_3": "Region", "column_4": "Value"})
    combined = combined.with_columns(pl.col("Region").str.strip_chars())
    # grouping by regions with same name and averaging out values
    combined = combined.group_by("Region").agg(pl.col("Value").mean())
    combined = combined.with_columns(pl.col("Region").str.replace(r"/", "_"))
    fname = str(os.path.splitext(USER_SUPPLIED_DATA)[0]) + "_BN_REGIONS.csv"
    combined.write_csv(fname)
    return fname


def open_SUMA(dataset=""):
    subprocess.Popen(
        ["suma", "-spec", AFNI_DIR + "MNI152_2009_both.spec", "-input", dataset],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


class LogScreen(ModalScreen):
    def compose(self) -> ComposeResult:
        yield Label(LOGS)
        yield Button("ok", id="ok")

    @on(Button.Pressed)
    def handle_yes(self) -> None:
        self.dismiss(True)


class FileOpenApp(App[None]):
    CSS = """
    Screen {
        align: center middle; 
        }
    """

    def compose(self) -> ComposeResult:
        self.logo = Center(
            Label("""
░██████████ ░█████████   ░██████   ░██     ░██ ░███     ░███    ░███    
░██               ░██   ░██   ░██  ░██     ░██ ░████   ░████   ░██░██   
░██              ░██   ░██         ░██     ░██ ░██░██ ░██░██  ░██  ░██  
░█████████     ░███     ░████████  ░██     ░██ ░██ ░████ ░██ ░█████████ 
░██           ░██              ░██ ░██     ░██ ░██  ░██  ░██ ░██    ░██ 
░██          ░██        ░██   ░██   ░██   ░██  ░██       ░██ ░██    ░██ 
░██████████ ░█████████   ░██████     ░██████   ░██       ░██ ░██    ░██ 
""")
        )
        yield self.logo
        yield Center(Label("I want to..."))
        yield Center(
            Button(
                "map electrodes to Brainnetome Atlas regions",
                id="electrodes",
                variant="primary",
            )
        )
        yield Center(
            Button(
                "map values to Brainnetome Atlas regions",
                id="color_planes",
                variant="warning",
            )
        )
        yield Center(Button("open SUMA", id="open_SUMA", variant="primary"))
        yield Center(Button("quit", id="quit", variant="warning"))

    def on_mount(self) -> None:
        self.theme = "tokyo-night"

    @on(Button.Pressed, "#electrodes")
    @work
    async def electrode_file_open(self) -> None:
        if opened := await self.push_screen_wait(FileOpen()):
            result_file = map_electrodes(opened)
            self.notify("Processed, saved to " + result_file)

    @on(Button.Pressed, "#color_planes")
    @work
    async def region_file_open(self) -> None:
        if opened := await self.push_screen_wait(FileOpen()):
            LOGS = process_file(opened)
            self.notify("Processed.")

    @on(Button.Pressed, "#open_SUMA")
    @work
    async def suma_init(self) -> None:
        open_SUMA()
        self.notify("SUMA opened.")

    @on(Button.Pressed, "#quit")
    @work
    async def exit_program(self) -> None:
        quit()


def main():
    FileOpenApp().run()


if __name__ == "__main__":
    sys.exit(main())
