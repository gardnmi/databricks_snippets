import requests
import json
from collections import defaultdict
from dotenv import dotenv_values

config = dotenv_values(".env")


def get_notebook_data(
    workspace,
    databricks_url=config["DATABRICKS_URL"],
    token=config["DATABRICKS_TOKEN"],
):

    api_url = "/api/2.0/workspace/list"
    headers = {"Authorization": f"Bearer {token}"}
    api_data = defaultdict(list)

    def get_api_data(workspace):

        data = {"path": workspace}
        response = requests.get(
            f"{databricks_url}{api_url}", headers=headers, json=data
        )

        objects = response.json().get("objects")

        if objects:
            for object in objects:
                if object["object_type"] == "NOTEBOOK":
                    api_data["object_type"].append(object["object_type"])
                    api_data["path"].append(object["path"])
                    api_data["object_id"].append(object["object_id"])
                    api_data["language"].append(object["language"])
                else:
                    get_api_data(workspace=object["path"])
        else:
            pass

    get_api_data(workspace)

    with open("notebook_data.json", "w") as outfile:
        json.dump(api_data, outfile)

    return api_data


def get_cell_data(notebook_data):

    code_blocks = []

    # erase file conents
    open("finished_notebooks.txt", "w").close()

    headers = {
        "authority": f"{config['DATABRICKS_URL']}",
        "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Microsoft Edge";v="96"',
        "accept": "*/*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43",
        "sec-ch-ua-platform": '"Windows"',
        "origin": f"{config['DATABRICKS_URL']}",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "referer": f"{config['DATABRICKS_URL']}/login.html",
        "accept-language": "en-US,en;q=0.9",
    }

    data = {
        "j_username": config["DATABRICKS_USERNAME"],
        "j_password": config["DATABRICKS_PASSWORD"],
    }

    for id, language in zip(notebook_data["object_id"], notebook_data["language"]):

        with requests.Session() as s:
            login_url = f"{config['DATABRICKS_URL']}/j_security_check"
            notebook_url = f"{config['DATABRICKS_URL']}/notebook/{id}/command"

            login = s.post(login_url, headers=headers, data=data)
            headers["x-databricks-org-id"] = login.headers["x-databricks-org-id"]

            json_data = s.get(
                f"{config['DATABRICKS_URL']}/config",
                headers=headers,
                cookies=s.cookies,
            )

            headers["x-csrf-token"] = json_data.json()["csrfToken"]

            json_data = s.get(notebook_url, headers=headers,
                              cookies=s.cookies).json()

            # Add the ?o paramater otherwise you get csfr errors when accessing link
            notebook_url = f"{config['DATABRICKS_URL']}/?o={config['DATABRICKS_OID']}#notebook/{id}/command"

            for code_block in json_data:
                code_block["notebook_id"] = id
                code_block["notebook_language"] = language
                code_block["notebook_url"] = notebook_url
                code_block["code_block_url"] = f"{notebook_url}/{code_block['id']}"

                if "%python" in code_block["command"]:
                    code_block["code_block_language"] = "python"
                elif "%scala" in code_block["command"]:
                    code_block["code_block_language"] = "scala"
                elif "%sql" in code_block["command"]:
                    code_block["code_block_language"] = "sql"
                elif "%md" in code_block["command"]:
                    code_block["code_block_language"] = "markdown"
                else:
                    code_block["code_block_language"] = language.lower()

            code_blocks += json_data

        with open("finished_notebooks.txt", "a") as file:
            file.write(f"{id}\n")

        print(notebook_url)

    return code_blocks
