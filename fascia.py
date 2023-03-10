# %%
from functools import reduce

import pandas
import requests
import tabula
from bs4 import BeautifulSoup

# %%
tree = BeautifulSoup(
    requests.get(
        "https://www.anvur.it/attivita/classificazione-delle-riviste/classificazione-delle-riviste-ai-fini-dellabilitazione-scientifica-nazionale/elenchi-di-riviste-scientifiche-e-di-classe-a/"
    ).text,
    "lxml",
)

# %%
rs = reduce(
    lambda x, y: pandas.merge(x, y, on=["TITOLO", "ISSN"], how="outer"),
    [
        pandas.concat(tabula.read_pdf(path, lattice=True, pages="all", silent=True))
        .dropna(axis=1, how="all")
        .replace("\r", " ")
        for path in (
            [a["href"] for a in tree.find("h3").find_next("ul").find_all("a")]
            + [
                a["href"]
                for a in tree.find("h3").find_next("h3").find_next("ul").find_all("a")
            ]
        )
    ],
)

# %%
rs.to_excel("riviste.xlsx", index=False)
rs.to_csv("riviste.csv", index=False)
rs.to_json("riviste.json", orient="records")

# %%
