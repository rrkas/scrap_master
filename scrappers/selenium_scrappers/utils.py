from selenium.webdriver.common.by import By


def recursive_scrap_tree(element):
    currBranch = {}
    currBranch["tag"] = element.tag_name
    currBranch["text"] = element.text

    currBranch["attrs"] = {}
    for attr in element.get_property("attributes"):
        currBranch["attrs"][attr["name"]] = attr["value"]

    currBranch["children"] = []
    for ch in element.find_elements(By.XPATH, "*"):
        currBranch["children"].append(recursive_scrap_tree(ch))

    return currBranch
