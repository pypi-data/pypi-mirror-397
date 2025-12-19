from pybaseball import statcast
import pandas as pd
from pathlib import Path


def main():

    Path("data").mkdir(parents=True, exist_ok=True)
    
    BARREL_CSV_URL = (
        "https://raw.githubusercontent.com/Jerm2000/stat_386_project/main/data/exit_velocity.csv"
    )


    # Selecting full season
    data = statcast(start_dt="2025-03-20", end_dt="2025-11-01")

    # keep only home runs
    hr = data[data["events"] == "home_run"].copy()

    # group by player_name and compute leaders
    leaders = (
        hr.groupby("batter")
        .agg(
            hr_count=("events", "size"),
            avg_hr_distance=("hit_distance_sc", "mean"),
            max_hr_distance=("hit_distance_sc", "max"),

            # launch speed (exit velocity) metrics
            avg_launch_speed=("launch_speed", "mean"),
            max_launch_speed=("launch_speed", "max"),
        )
        .reset_index()
    )

    # filter to players with >= 5 home runs
    leaders = leaders[leaders["hr_count"] >= 5]

    # sort after filtering
    leaders = leaders.sort_values("avg_hr_distance", ascending=False)

    #Rounding values
    leaders["avg_hr_distance"] = leaders["avg_hr_distance"].round(1)
    leaders["max_hr_distance"] = leaders["max_hr_distance"].round(1)
    leaders["avg_launch_speed"] = leaders["avg_launch_speed"].round(1)
    leaders["max_launch_speed"] = leaders["max_launch_speed"].round(1)

    leaders.to_csv("./data/hr_distance_leaders_2025.csv", index=True)

    try:
        barrel_leaders = pd.read_csv("./data/exit_velocity.csv")
    except FileNotFoundError:
        barrel_leaders = pd.read_csv(BARREL_CSV_URL)


    #Combining last name and first name into one column so both datasets match
    name_col = "last_name, first_name"
    barrel_leaders["player_name"] = barrel_leaders[name_col].str.strip()

    #Only keeping columns we want to use
    savant_barrels = barrel_leaders[["player_id", "player_name", "barrels", "brl_percent"]].copy()

    #Combining datasets on player name
    combined = leaders.merge(savant_barrels, left_on = "batter", right_on="player_id", how="inner")

    #Rounding values
    combined["brl_percent"] = combined["brl_percent"].round(1)

    combined = combined.drop(columns=["player_id"])

    combined = combined[
        [
            "player_name",     # first column
            "batter",          # ID
            "hr_count",
            "avg_hr_distance",
            "max_hr_distance",
            "avg_launch_speed",
            "max_launch_speed",
            "barrels",
            "brl_percent",
        ]
    ]

    combined.to_csv("./data/combined_leaders_2025.csv", index=False)

if __name__ == "__main__":
    main()