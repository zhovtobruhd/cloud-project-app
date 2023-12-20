import os
import json

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
    except Exception as e:
        data = str(e)
    else:
        try:
            data = [json.dumps(item, indent=True) for item in container.query_items(
                query=f'SELECT * FROM {container_name} c ORDER BY c.order_date DESC OFFSET 0 LIMIT 10',
                enable_cross_partition_query=True
            )]
        except Exception as e:
            data = str(e)
    print('Request for index page received')
    return render_template('index.html', value=json.dumps(data))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


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

