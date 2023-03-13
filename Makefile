.EXPORT_ALL_VARIABLES:

PROJECT = databricks_snippets

clean: clean-app clean-data

clean-app:
	docker-compose down
	docker rmi -f "$(PROJECT)-app"

clean-data:
	docker volume rm -f "$(PROJECT)_data"
