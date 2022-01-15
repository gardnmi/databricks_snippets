from flask import Flask, render_template, escape, request, jsonify
from elasticsearch import Elasticsearch, helpers
from retry import retry
import json
import time
import os
from scrape import get_notebook_data, get_cell_data

app = Flask(__name__)


@retry(tries=10, delay=6)
def get_elasticsearch():
    return Elasticsearch("http://elasticsearch:9200")


@app.route("/check_progress", methods=["GET"])
def check_progress():

    try:
        finished_file_size = os.stat("finished_notebooks.txt").st_size != 0
        notebook_data_file_size = os.stat("notebook_data.json").st_size != 0
    except:
        finished_file_size = None
        notebook_data_file_size = None

    if finished_file_size and notebook_data_file_size:

        with open("notebook_data.json", "r") as file:
            notebook_data = json.load(file)
            number_of_total_notebooks = len(notebook_data["object_id"])

        with open("finished_notebooks.txt", "r") as file:
            content = file.read().split("\n")
            number_of_read_notebooks = len(content) - 1

        percentage = int(number_of_read_notebooks /
                         number_of_total_notebooks * 100) - 1

        if percentage < 2:
            percentage = 2

        found_notebooks = f"Imported: {number_of_read_notebooks} of {number_of_total_notebooks} Notebooks"

    else:
        percentage = 2
        number_of_read_notebooks = 0
        found_notebooks = "Searching for Notebooks...."

    time.sleep(1)
    return jsonify(
        percentage=str(percentage),
        found_notebooks=found_notebooks,
    )


@app.route("/get_workspace", methods=["GET"])
def get_workspace():

    try:
        workspace = request.args.get("workspace")

        notebook_data = get_notebook_data(workspace=workspace)
        cell_data = get_cell_data(notebook_data)

        with open("data.json", "w") as outfile:
            json.dump(cell_data, outfile)

        # Inialize elasticsearch with data
        with open("data.json") as file:
            json_data = json.loads(file.read())

        keep_cols = [
            "id",
            "command",
            "pathName",
            "notebook_id",
            "notebook_language",
            "notebook_url",
            "code_block_url",
            "code_block_language",
        ]

        json_data = [{key: data[key] for key in keep_cols}
                     for data in json_data]

        actions = [
            {
                "_index": "nodes_bulk",
                "_type": "external",
                "_id": str(data["id"]),
                "_source": data,
            }
            for data in json_data
        ]

        es = get_elasticsearch()
        helpers.bulk(es, actions)

        # clear out files for next run
        open("finished_notebooks.txt", "w").close()
        open("notebook_data.json", "w").close()

        return jsonify(
            success="Notebooks are now searchable! Please Refresh the page before importing another workspace."
        )
    except Exception as e:
        # clear out files for next run
        open("finished_notebooks.txt", "w").close()
        open("notebook_data.json", "w").close()

        return jsonify(error=f"""Oops...something went wrong: {e}""")


@app.route("/", methods=["GET"])
def find_code_blocks(code_blocks=None):

    search = request.args.get("search")
    if search:
        es = get_elasticsearch()
        results = es.search(
            index="nodes_bulk",
            body={"query": {"match": {"command": search}}},
            size=50,
        )
        code_blocks = results.raw["hits"]["hits"]

    return render_template("index.html", code_blocks=code_blocks, search=search)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
