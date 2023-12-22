import os

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

from azure.cosmos import CosmosClient


url = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
database_name = os.environ["DATABASE_NAME"]
container_name = os.environ["CONTAINER_NAME"]

app = Flask(__name__)



@app.route('/')
def index():
    try:
        client = CosmosClient(url, key)
        database = client.get_database_client(database=database_name)
        container = database.get_container_client(container_name)
    except Exception as e:  # pylint: disable=broad-except
        data = [
                {
                    "id": str(e)
                }
            ]
    else:
        try:
            data = [item for item in container.query_items(
                query=f'SELECT * FROM {container_name} c ORDER BY c._ts DESC OFFSET 0 LIMIT 10',
                enable_cross_partition_query=True
            )]
        except Exception as e:  # pylint: disable=broad-except
            data = [
                {
                    "id": str(e)
                }
            ]
    print('Request for index page received')
    return render_template('index.html', value=data)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/process_dates', methods=['POST'])
def process_dates():
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    try:
        client = CosmosClient(url, key)
        database = client.get_database_client(database=database_name)
        container = database.get_container_client(container_name)
    except Exception as e:  # pylint: disable=broad-except
        data = [
                {
                    "id": str(e)
                }
            ]
    else:
        try:
            data = [item for item in container.query_items(
                query=f'SELECT * FROM {container_name} c ORDER BY c._ts DESC OFFSET 0 LIMIT 10',
                enable_cross_partition_query=True
            )]
        except Exception as e:  # pylint: disable=broad-except
            data = [
                {
                    "id": str(e)
                }
            ]

    return render_template('data.html', value=data, start_date=start_date, end_date=end_date)

@app.route('/hello', methods=['POST'])
def hello():
    name = request.form.get('name')

    if name:
        print(f'Request for hello page received with name={name}')
        return render_template('hello.html', name=name)

    print('Request for hello page received with no name or blank name -- redirecting')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()

