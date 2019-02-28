import pandas as pd
from bs4 import BeautifulSoup
from load_save import load_rev_sublist

from functools import lru_cache


def generate_js_bookmarklet(html_doc, domain):
    """
    Generate the javascript for a bookmarklet that hides papers not in domain `domain`

    Arguments
    ---------
    html_doc : str
        source of the table in easychair status page (very long string)
    domain : str
        name of domain you want to view (i.e. filter all other domains)
    """
    # load submissions
    _, sublist, _, _ = load_rev_sublist()

    subdf = get_papers_df(html_doc)
    domains = []

    # iterate over papers df and create 'domain' column
    for i, id, title in subdf.itertuples():
        res = [sub.domain for sub in sublist if sub.title == title.strip()]
        if res:
            domains.append(res[0])
        else:
            domains.append("scipy tools")

    subdf = subdf.assign(domain=domains)

    jsdomain = subdf[subdf.domain != domain][0].values
    jsdomain = [dom.strip().replace("l", "r") for dom in jsdomain]

    js = (
        r"javascript:(function(){var%20papers="
        + f"{jsdomain}"
        + r";for(paper%20in%20papers){var%20d=document.getElementById(papers[paper]);if(d.hidden==true){d.hidden=false;}else{d.hidden=true}};})()"
    )

    return js


@lru_cache(maxsize=None)
def get_papers_df(html_doc):
    """
    Parse html_doc, grab the list of element ids of all papers
    """
    # create long raw string variable of source from status page in easychair
    soup = BeautifulSoup(html_doc, "html.parser")

    papers = []
    for item in soup.find_all("a"):
        if item.get("class"):
            if item["class"][0] == "title":
                papers.append((item["id"], item.text))

    subdf = pd.DataFrame(papers)
    return subdf
