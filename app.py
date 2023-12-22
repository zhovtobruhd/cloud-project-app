import os
import io
import datetime
import base64

from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

from azure.cosmos import CosmosClient
import matplotlib.pyplot as plt
from matplotlib.backends.backend_svg import FigureCanvasSVG


url = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
database_name = os.environ["DATABASE_NAME"]
container_name = os.environ["CONTAINER_NAME"]

app = Flask(__name__)

def plot_to_uri():
    # Create a simple Matplotlib plot
    x = [1, 2, 3, 4, 5]
    y = [2, 3, 5, 7, 11]

    fig, ax = plt.subplots()
    ax.plot(x, y)
    ax.set_xlabel('X-axis')
    ax.set_ylabel('Y-axis')
    ax.set_title('Matplotlib Plot')

    # Convert the plot to SVG format
    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    svg_data = output.getvalue()
    output.close()

    # Encode the SVG data to base64

    b = base64.b64encode(svg_data) # bytes
    svg_base64 = "data:image/svg+xml;base64," + b.decode().strip()

    return svg_base64

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
    start_date = int(datetime.datetime.strptime(request.form.get('start_date'), "%Y-%m-%dT%H:%M").timestamp())
    end_date = int(datetime.datetime.strptime(request.form.get('end_date'), "%Y-%m-%dT%H:%M").timestamp())

    if start_date > end_date:
        start_date, end_date = end_date, start_date

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
                query=f'SELECT * FROM {container_name} c WHERE c._ts BETWEEN {start_date} AND {end_date} ORDER BY c._ts DESC OFFSET 0 LIMIT 1000',
                enable_cross_partition_query=True
            )]
        except Exception as e:  # pylint: disable=broad-except
            data = [
                {
                    "id": str(e)
                }
            ]

    return render_template('data.html', value=data, start_date=start_date, end_date=end_date, img=plot_to_uri())

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

