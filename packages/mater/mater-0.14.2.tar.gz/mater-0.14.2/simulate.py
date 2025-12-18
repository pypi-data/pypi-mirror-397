"""
MATER simulation script.
"""

from mater import Mater

# === CONFIGURATION ===
INPUT_FILE = "mater_example.xlsx"  # Name of your Excel input file
OUTPUT_FOLDER = "run0"  # Name of the folder where outputs are stored
START_TIME = 1901  # Initial time step
END_TIME = 2100  # Final time step
TIME_FREQUENCY = "YS"  # Time frequency
# === END CONFIGURATION ===


def main():
    """Run MATER simulation."""
    model = Mater()
    model.run_from_excel(
        OUTPUT_FOLDER,
        INPUT_FILE,
        simulation_start_time=START_TIME,
        simulation_end_time=END_TIME,
        time_frequency=TIME_FREQUENCY,
    )


if __name__ == "__main__":
    main()
