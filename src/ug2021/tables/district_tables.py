import polars as pl
from great_tables import GT, loc, style

from ug2021.data import results

def summary() -> GT: 
    data = (
        results.districts_wide
        .with_columns(
            pl.col("turnout") / 100
        )
        .select("district", "registered", "valid", "invalid", "total", "turnout", "winner")
        .rename(str.capitalize)
    )

    sel_votes = pl.col("Invalid", "Valid")
    sel_turnout = pl.col("Total", "Turnout")

    table = (
        GT(data)
        .tab_header("District Summary")
        .tab_spanner("The Votes", sel_votes)
        .tab_spanner("Turnout", sel_turnout)
        .cols_label(
            Turnout="Percentage"
        ).data_color(
            columns="Registered",
            palette=[
                "#00A600", "#E6E600", "#E8C32E", "#D69C4E", "#Dc863B", "sienna", "sienna4", "tomato4", "brown"
            ],
            domain=[data["Registered"].min(), data["Registered"].max()]
        )
        # format
        .fmt_integer(pl.col("Registered", "Invalid", "Valid", "Total"))
        .fmt_percent(columns=pl.col("Turnout"), decimals=0)
        # style
        .tab_style(
            style=style.fill(color="palegoldenrod"),
            locations=loc.body(columns=sel_votes),
        )
        .tab_style(
            style=style.fill(color="powderblue"),
            locations=loc.body(columns=sel_turnout),
        )
    )
    return table
