import dash
import dash_core_components as dcc
import dash_html_components as html
import psycopg2
import pandas as pd

conn = psycopg2.connect(
        host="postgres",
        port=5432,  # Port PostgreSQL
        database="mydatabase",
        user="airflow",
        password="mypassword"
    )

query = "SELECT * FROM reviews"
df = pd.read_sql(query, conn)

conn.close()


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1("Selamat datang ke Plotly Dash!"),
        dcc.Graph(
            figure={
                "data": [{"x": [1, 2, 3], "y": [4, 1, 2], "type": "bar", "name": "Data 1"}],
                "layout": {"title": "Contoh Plotly Dash"}
            }
        )
    ]
)

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050, debug=True)
