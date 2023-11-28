# %%
from functools import reduce

import numpy
import pandas
import requests
import tabula
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions

# %%
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)

# %%
driver.get(
        "https://www.anvur.it/attivita/classificazione-delle-riviste/classificazione-delle-riviste-ai-fini-dellabilitazione-scientifica-nazionale/elenchi-di-riviste-scientifiche-e-di-classe-a/"
    )
tree = BeautifulSoup(
    driver.page_source,
    "lxml",
)

# %%
paths = [
        a["href"] for a in tree.find("h3").find_next("ul").find_all("a")
    ] + [
        a["href"] for a in tree.find("h3").find_next("h3").find_next("ul").find_all("a")
    ]

sources = []
for path in paths:
    tables = tabula.read_pdf(path, lattice=True, pages="all", silent=True)
    i=0
    while i < len(tables):
        if len(tables[i].columns) < len(tables[0].columns):
            if len(tables[i].columns) + len(tables[i+1].columns) == len(tables[0].columns)+1:
                tables.pop(i+1)
                retry = tabula.read_pdf(path, lattice=True, pages=i+1, silent=True)
                tables[i] = pandas.merge(*retry, on=list(set.intersection(*map(lambda t:set(t.columns),retry))), how='inner')              
            else:
                raise Exception()       
        if not((tables[i].columns[0] == 'TITOLO') and (tables[i].columns[1] == 'ISSN')):
            tables[i] = pandas.DataFrame(numpy.vstack([tables[i].columns, tables[i]]))
            tables[i].columns = tables[0].columns
        i+=1
    sources.append(pandas.concat(tables, ignore_index=True).dropna(axis=1, how="all").replace("\r", " "))

rs = reduce(
    lambda x, y: pandas.merge(x, y, on=["TITOLO", "ISSN"], how="outer"),
    sources
)

# %%
rs.to_excel("riviste.xlsx", index=False)
rs.to_csv("riviste.csv", index=False)
rs.to_json("riviste.json", orient="records")

# %%
driver.close()
