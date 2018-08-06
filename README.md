mcd_database

Internal database for all mcd assets

1. Uploading assets
2. Tagging assets
3. Search and Filter assets
4. Manage assets

Notable components used in this project
1. Datatables(js)
2. Flask(py)
3. Flask SQLAlchemy(py, sql)
4. Postgres(db)
5. Flask Whoosh Alchemy(py)
6. Dropzone(js)
7. Selectize(js)
9. Flask Socketio(py, js)

Important Notes:
Search Index(Whoosh) will not search correctly after Weekends. Most likely due to server resets, and/or network shutdown during weekends. Restarting the mcd_db server will show socket in use. Using lsof -i:80 will show those sockets are still up. Kill those, and the server will run, however, the database will be off synced and not reconnect properly. To fix, I have devised a plan where i will,
	1. automatically reset the server on monday mornings
	2. rebuild the index by running build_index.py as a service in /etc/systemd/system/build_index.service
	3. run mcd_db.service.

