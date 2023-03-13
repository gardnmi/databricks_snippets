<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

<!-- PROJECT LOGO -->
<br />
<div align="center">

  <h3 align="center">Databricks Snippets</h3>

  (Forked from [gardnmi's Databricks Snippets](https://github.com/gardnmi/databricks_snippets).)

  <p align="center">
    An Elasticsearch site to help you find snippets of code in your Databricks notebooks.
    <br />
    <br />
  </p>
</div>

## UPDATES:  

* 5/26/2022 - [Databricks has added a similiar search feature on its platform.](https://docs.databricks.com/release-notes/product/2022/may.html#improved-workspace-search-public-preview)    

<!-- ABOUT THE PROJECT -->

## About The Project

![Alt Text](https://media1.giphy.com/media/GIS49S3MU28GBQMnMX/giphy.gif?cid=790b7611cf0f47f83ee07e5804d41bf151525e71ed16a422&rid=giphy.gif&ct=gf)

An Elasticsearch website built to find code snippets in your Databricks workspace.

<p align="right">(<a href="#top">back to top</a>)</p>

### Built With

- [flask](https://flask.palletsprojects.com/en/2.0.x/)
- [databricks](https://databricks.com/)
- [elastic search](https://www.elastic.co/)
- [python](https://www.python.org/)

<p align="right">(<a href="#top">back to top</a>)</p>

### Prerequisites

Docker must be installed

- https://docs.docker.com/get-docker/

<p align="right">(<a href="#top">back to top</a>)</p>

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/harjeeth/databricks_snippets
   ```
2. Create an `.env` file with these enviroment variables:

   ```sh
   DATABRICKS_URL=https://<databricks-instance>.com # i.e. https://cust-success.cloud.databricks.com
   DATABRICKS_TOKEN=<token>  # https://docs.databricks.com/dev-tools/api/latest/authentication.html
   ```

   The file should be saved directly below the root directory:

   ```bash
   ├── databricks_snippets
   │   ├── .env
   │   └── app.py
   │   └── ..
   ```

3. Navigate to the project in your shell

   ```sh
   cd databricks_snippets
   ```

4. Run the Docker command in your shell

   ```sh
   docker-compose up
   ```

5. Open up your browser and navigate to:
   ```
   http://localhost:5001/
   ```
6. Before searching you will need to import Notebooks from your Workspace or Repo.

   ![](https://i.imgur.com/G2vwlPD.png)

   ```
   /Users/mike.gardner@kytheralabs.com
   ```

   or

   ```
   /Repos/mike.gardner@kytheralabs.com
   ```

   The app uses the [workspace api](https://docs.databricks.com/dev-tools/api/latest/workspace.html#list) to list the desired notebooks and scrape the notebooks.

7. To close the app, press `Ctrl+C` in the console.
<p align="right">(<a href="#top">back to top</a>)</p>

### Development
To apply changes in your code:
1. Close the app (`Ctrl+C`)
2. In the console, remove containers, app image and volume by running:
```
make clean
```
3. Restart the app (`docker-compose up`)

<p align="right">(<a href="#top">back to top</a>)</p>

### Debug Resources

- [Elasticsearch Docker Image Setup Guide](https://www.elastic.co/guide/en/elasticsearch/reference/7.16/docker.html)
- [wsl2 Docker High Memory Usage](https://medium.com/@lewwybogus/how-to-stop-wsl2-from-hogging-all-your-ram-with-docker-d7846b9c5b37)

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>
