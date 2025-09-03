"""
Dataframes with the election results

The results are are aggregated at all available administrative levels and
represented in wide form and long form.
"""
from importlib.resources import files

import polars as pl

__all__ = (
    "polling_station_results",
    "stations_wide",
    "parishes_wide",
    "subcounties_wide",
    "constituencies_wide",
    "districts_wide",
    "national_wide",
    "stations_long",
    "parishes_long",
    "subcounties_long",
    "constituencies_long",
    "districts_long",
    "national_long",
)

# The original data is in wide format
polling_station_results = pl.read_parquet(
    files("ug2021._resources").joinpath("polling-station-results.parquet")
)

# NOTE: Depends on dataset
# 
# The names come from polling_station_results.columns
# e.g. polling_station_results.columns[6:17]
CANDIDATE_COLS = [
    "Amuriat",
    "Kabuleta",
    "Kalembe",
    "Katumba",
    "Kyagulanyi",
    "Mao",
    "Mayambala",
    "Muntu",
    "Mwesigye",
    "Tumukunde",
    "Museveni",
]

ADMIN_REGION_COLS = [
    "district",
    "constituency",
    "subcounty",
    "parish",
    "station",
]

AGGREGATE_COLS = [
    "registered",
    "valid",
    "invalid",
    "total",
    "turnout"
]


def get_winners(s: pl.Series) -> str:
    """
    Given a series with candidate totals, return the winner(s) 

    If there are multiple winners, return all as a comma separated string
    """
    return ", ".join([name for won, name in zip(s, CANDIDATE_COLS) if won])


def augment_wide_data(data: pl.DataFrame) -> pl.DataFrame:
    """
    Add turnout and winner columns
    """
    res = (
        data.with_columns(
            turnout=pl.col("total") * 100 / pl.col("registered"),
            winner=(
                # 1. votes for each candidate
                # 2. whether they won
                # 3. who won
                pl.concat_list(CANDIDATE_COLS)
                .list.eval(pl.element()==pl.element().max())
                .map_elements(get_winners, return_dtype=str)
            )
        )
    )
    return res



# Polling station
stations_wide = augment_wide_data(
    polling_station_results
    .filter(pl.col("total") > 0)
    .sort(ADMIN_REGION_COLS)
)

sums = pl.col(
    CANDIDATE_COLS + ["registered", "valid", "invalid", "total"]
).sum()

# By Parish
parishes_wide = augment_wide_data(
    stations_wide
    .group_by(
        ["district", "constituency", "subcounty", "parish"],
        maintain_order=True
    )
    .agg(sums)
)

# By subcounty
subcounties_wide = augment_wide_data(
    stations_wide
    .group_by(["district", "constituency", "subcounty"], maintain_order=True)
    .agg(sums)
)

# By Constituency
constituencies_wide = augment_wide_data(
    stations_wide
    .group_by(["district", "constituency"], maintain_order=True)
    .agg(sums)
)

# By District
districts_wide = augment_wide_data(
    stations_wide
    .group_by("district", maintain_order=True)
    .agg(sums)
)


# Whole country
national_wide = augment_wide_data(stations_wide.select(sums))


# Make long form versions

def make_long(wide_data: pl.DataFrame) -> pl.DataFrame:
    """
    Make long form w.r.t. candidate

    Add columns:
      - candidate (Name of candidate)
      - votes (Number of votes)
      - won (Whether candidate won at the polling station)
      - rank (Ranking of candidate at that polling station)
    """
    index_cols = [
        *set(wide_data.columns).intersection(ADMIN_REGION_COLS),
        *AGGREGATE_COLS
    ]
    long_data = (
        wide_data
        .unpivot(
            CANDIDATE_COLS,
            index=index_cols,
            variable_name="candidate",
            value_name="votes"
        )
        .with_columns(
            won=pl.col("votes").max().over(AGGREGATE_COLS) == pl.col("votes"),
            rank=(
                pl.col("votes")
                .rank("min", descending=True)
                .over(AGGREGATE_COLS)
                .cast(int)
            )
        )
    )
    return long_data

stations_long = make_long(stations_wide)
parishes_long = make_long(parishes_wide)
subcounties_long = make_long(subcounties_wide)
constituencies_long = make_long(constituencies_wide)
districts_long = make_long(districts_wide)
national_long = make_long(national_wide)
