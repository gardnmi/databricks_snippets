from flask import Flask, render_template, request, jsonify
from elasticsearch import Elasticsearch, helpers
from retry import retry
import time
import os
import traceback
from scrape import get_notebook_data, export_all_notebooks


app = Flask(__name__)


@retry(tries=10, delay=6)
def get_elasticsearch():
    return Elasticsearch("http://elasticsearch:9200")


@app.route("/check_progress", methods=["GET"])
def check_progress():
    try:
        finished_file_size = os.stat("finished_notebooks.txt").st_size != 0
        all_notebooks_file_size = os.stat("all_notebooks.txt").st_size != 0
    except:
        finished_file_size = None
        all_notebooks_file_size = None

    if finished_file_size and all_notebooks_file_size:

        with open("all_notebooks.txt", "r") as file:
            content = file.read().split("\n")
            number_of_total_notebooks = len(content)

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
    start_time = time.time()
    try:
        workspace = request.args.get("workspace")
        if workspace == "":
            workspace = "/Users"

        notebook_data = get_notebook_data(workspace=workspace)
        notebooks_content = export_all_notebooks(notebook_data)

        # Inialize elasticsearch with data
        actions = [
            {
                "_index": "nodes_bulk",
                "_id": str(data["notebook_id"]),
                "_source": data,
            }
            for data in notebooks_content
        ]

        es = get_elasticsearch()
        helpers.bulk(es, actions)

        return jsonify(
            success="Notebooks are now searchable! Please Refresh the page before importing another workspace."
        )
    
    except Exception as e:
        return jsonify(error=f"""Oops...something went wrong: {e}\n{traceback.print_exc()}""")
    finally:
        app.logger.info(f"Exported workspace data in {time.time() - start_time} seconds")


@app.route("/", methods=["GET"])
def find_code_blocks(code_blocks=None):
    search = request.args.get("search")
    if search:
        es = get_elasticsearch()
        results = es.search(
            index="nodes_bulk",
            body={"query": {"match": {"notebook_content": search}}},
            size=50,
        )
        code_blocks = results.raw["hits"]["hits"]

    return render_template("index.html", code_blocks=code_blocks, search=search)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
