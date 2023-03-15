import requests
import json
from collections import defaultdict
from dotenv import dotenv_values
import base64


config = dotenv_values(".env")


def get_notebook_data(
    workspace: str,
    databricks_url: str = config["DATABRICKS_URL"],
    token: str = config["DATABRICKS_TOKEN"],
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

    with open("all_notebooks.txt", "w") as f:
        f.write('\n'.join([str(id) for id in api_data["object_id"]]))
    
    return api_data


def export_all_notebooks(
    notebook_data,
    databricks_url: str = config["DATABRICKS_URL"],
    token: str = config["DATABRICKS_TOKEN"],
):
    # Create or overwrite file
    open("finished_notebooks.txt", "w").close()

    code_blocks = []

    api_url = "/api/2.0/workspace/export"
    headers = {"Authorization": f"Bearer {token}"}  

    for id, language, path in zip(notebook_data["object_id"], notebook_data["language"], notebook_data["path"]):

        data = {"path": path}
        response = requests.get(
            f"{databricks_url}{api_url}", headers=headers, json=data
        )

        notebook_url = f"{databricks_url}/#notebook/{id}"
        notebook_content = base64.b64decode(response.json().get('content')).decode('utf-8')

        code_blocks.append({
            "notebook_path": path,
            "notebook_id": id,
            "notebook_language": language,
            "notebook_url": notebook_url,
            "notebook_content": notebook_content,
        })

        with open("finished_notebooks.txt", "a") as f:
            f.write(f"{id}\n")
    
    return code_blocks
