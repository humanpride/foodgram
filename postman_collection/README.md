## Postman collection for API testing

The `foodgram.postman_collection.json` file contains a Postman collection: a set of predefined requests for testing the API.

## Preparing the Django project to run the collection:
1. Make sure the virtual environment is set up and activated, and the project dependencies are installed.
2. To test the API locally, configure SQLite3 as the database in `settings.py`
and set `DEBUG = True`.
3. Apply migrations, then create at least 2 ingredients and 3 tags in the database.
4. Start the development web server.

*After setting up the project, make a copy of the `db.sqlite3` database file:
you may need it if something goes wrong.*

## Importing the collection into Postman:

1. Launch Postman.
2. In the upper-left corner, click `File` -> `Import`.
3. In the dialog that opens, drag and drop the collection file or select it using the file browser.
Import `foodgram.postman_collection.json` into Postman.

## Running the collection:

1. After completing the steps above, the imported collection will appear in the `Collections` tab on the left side of the Postman window.
Hover over the collection, click the three dots next to its name, and select `Run collection` from the dropdown menu. The collection's requests will appear in the center of the screen,
with the run settings menu on the right.
2. In the menu on the right, enable `Persist responses for a session` to view API responses after running the collection.
3. Click `Run <collection name>`.
4. The collection and test results will appear in the center of the screen. To show only failed tests, open the `Failed` tab.
Click a test to view details of the request and its response.

## Running the collection again:
1. Navigate to the `postman_collection` directory in the project root.
2. With the project's virtual environment activated, run the script that removes objects created by the collection's requests from the database: `bash clear_db.sh`.
The script deletes all users and objects created during the previous collection run, provided that the `on_delete` parameters are configured correctly in the project models.

If database cleanup fails, replace the current database file with your backup copy of `db.sqlite3`.
Alternatively, recreate the database and populate it with the objects required to run the collection, as described in step 3 of _Preparing the Django project to run the collection_.

## Postman usage limits
The free version of Postman has a technical limit: you can run a collection without interruptions 25 times per month.
Once you reach this limit, Postman will not turn into a pumpkin: it will still run collections, but runs may occasionally be blocked for 30 seconds, sometimes twice in a row. During these pauses, the interface will display a prompt to upgrade to a paid plan.
You can upgrade to a paid plan or continue using the free version with occasional advertising breaks.

There are no limits on sending individual requests.
