from bs4 import BeautifulSoup, Tag, NavigableString


def recursive_scrap_tree(element: BeautifulSoup):
    currBranch = {}

    if isinstance(element, BeautifulSoup):
        currBranch["root"] = []
        for e in element:
            currBranch["root"].append(recursive_scrap_tree(e))
    elif isinstance(element, NavigableString):
        currBranch = {
            "tag": "string",
            "text": element.get_text(),
        }
    elif isinstance(element, Tag):
        currBranch["tag"] = element.name
        currBranch["text"] = element.get_text()
        currBranch["attrs"] = element.attrs.copy()
        currBranch["children"] = []
        for ch in element.children:
            currBranch["children"].append(recursive_scrap_tree(ch))

    return currBranch
