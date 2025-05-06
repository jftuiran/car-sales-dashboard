import pandas as pd
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

# Carga los datos
df = pd.read_csv(r"C:\Users\WorkStation-JF\Desktop\TrabajoVisualizacionDash\CarSales.csv")
df.columns = df.columns.str.strip()
df['Date'] = pd.to_datetime(df['Date'], format="%m/%d/%Y")
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.strftime('%B')
month_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
df['Month'] = pd.Categorical(df['Month'], categories=month_order, ordered=True)

min_date = df['Date'].min()
max_date = df['Date'].max()

external_stylesheets = [dbc.themes.CYBORG]
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server 
app.title = "Car Sales Dashboard"

# Colores para líneas y scatter que contrastan en ambos fondos
LINE_COLORS = {"2022": "#1f77b4", "2023": "#ff7f0e"}
LINE_FILL_COLORS = {"2022": "rgba(31,119,180,0.2)", "2023": "rgba(255,127,14,0.2)"}
SCATTER_COLORS_DARK = px.colors.qualitative.Plotly
SCATTER_COLORS_LIGHT = px.colors.qualitative.D3

app.layout = dbc.Container([
    html.H1("Car Sales Dashboard", className="text-center text-primary mb-4"),
    dbc.Row([
        dbc.Col([
            html.Label("Marca:", className="d-block text-center fw-bold mb-1"),
            dcc.Dropdown(
                id="brand-dropdown",
                options=[{"label": b, "value": b} for b in df["Company"].unique()],
                value=df["Company"].unique()[0],
                clearable=False,
                style={"width": "180px"}
            )
        ], width="auto"),
        dbc.Col([
            html.Label("Año:", className="d-block text-center fw-bold mb-1"),
            dcc.Dropdown(
                id="year-dropdown",
                options=[{"label": y, "value": y} for y in sorted(df["Year"].unique())],
                value=sorted(df["Year"].unique())[0],
                clearable=False,
                style={"width": "120px"}
            )
        ], width="auto"),
        dbc.Col([
            html.Label("Rango de fechas:", className="d-block text-center fw-bold mb-1"),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=min_date,
                max_date_allowed=max_date,
                start_date=min_date,
                end_date=max_date,
                style={"background": "#222", "height": "38px"}
            )
        ], width="auto"),
        dbc.Col([
            html.Label("Fondo de gráficos:", className="d-block text-center fw-bold mb-1"),
            html.Button(
                "Cambiar fondo",
                id="background-btn",
                n_clicks=0,
                style={"height": "38px", "width": "150px", "display": "block", "margin": "0 auto"}
            )
        ], width="auto"),
        dbc.Col([
            html.Label("Gráfico circular:", className="d-block text-center fw-bold mb-1"),
            dcc.Dropdown(
                id="pie-dropdown",
                options=[
                    {"label": "Distribución por carrocería", "value": "Body Style"},
                    {"label": "Distribución por género", "value": "Gender"}
                ],
                value="Body Style",
                clearable=False,
                style={"width": "230px"}
            )
        ], width="auto")
    ], justify="center", align="center", className="mb-4"),
    # Gráficos en 2x2
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph1"), width=6),
        dbc.Col(dcc.Graph(id="graph2"), width=6)
    ]),
    dbc.Row([
        dbc.Col(dcc.Graph(id="graph3"), width=6),
        dbc.Col(dcc.Graph(id="graph4"), width=6)
    ])
], fluid=True)

@app.callback(
    Output("graph1", "figure"),
    Output("graph2", "figure"),
    Output("graph3", "figure"),
    Output("graph4", "figure"),
    Input("brand-dropdown", "value"),
    Input("year-dropdown", "value"),
    Input("background-btn", "n_clicks"),
    Input('date-range', 'start_date'),
    Input('date-range', 'end_date'),
    Input('pie-dropdown', 'value')
)
def update_graphs(brand, year, n_clicks, start_date, end_date, pie_value):
    mask = (
        (df["Company"] == brand) &
        (df["Date"] >= pd.to_datetime(start_date)) &
        (df["Date"] <= pd.to_datetime(end_date))
    )
    dff = df[mask]
    color = "#222" if n_clicks % 2 == 0 else "#fff"
    text_color = "#fff" if n_clicks % 2 == 0 else "#222"
    grid_color = "#888" if color == "#222" else "#bbb"

    # Gráfico 1: Línea comparativa 2022 vs 2023 por marca
    ventas_mes = dff.groupby(["Year", "Month"]).size().unstack(fill_value=0).reindex([2022, 2023], fill_value=0)
    x = month_order
    y_2022 = ventas_mes.loc[2022, :].reindex(month_order, fill_value=0) if 2022 in ventas_mes.index else [0]*12
    y_2023 = ventas_mes.loc[2023, :].reindex(month_order, fill_value=0) if 2023 in ventas_mes.index else [0]*12

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=x, y=y_2022, mode='lines', name='2022',
        line=dict(color=LINE_COLORS["2022"], width=3),
        fill='tozeroy', fillcolor=LINE_FILL_COLORS["2022"]
    ))
    fig1.add_trace(go.Scatter(
        x=x, y=y_2023, mode='lines', name='2023',
        line=dict(color=LINE_COLORS["2023"], width=3),
        fill='tozeroy', fillcolor=LINE_FILL_COLORS["2023"]
    ))
    fig1.update_layout(
        title=f'Ventas por mes comparando 2022 y 2023 ({brand})',
        xaxis_title='Mes',
        yaxis_title='Cantidad de ventas',
        plot_bgcolor=color,
        paper_bgcolor=color,
        font_color=text_color,
        title_x=0.5
    )
    fig1.update_xaxes(showgrid=True, gridcolor=grid_color)
    fig1.update_yaxes(showgrid=True, gridcolor=grid_color)

    # Gráfico 2: Barras por mes (solo año seleccionado)
    dff_year = dff[dff["Year"] == year]
    ventas_mes_year = dff_year.groupby("Month").size().reindex(month_order, fill_value=0)
    fig2 = px.bar(
        x=ventas_mes_year.index, y=ventas_mes_year.values,
        title=f"Ventas por mes ({brand})",
        labels={"x": "Mes", "y": "Cantidad de ventas"},
        color_discrete_sequence=["#2ca02c"]
    )
    fig2.update_layout(plot_bgcolor=color, paper_bgcolor=color, font_color=text_color, title_x=0.5)
    fig2.update_xaxes(showgrid=True, gridcolor=grid_color)
    fig2.update_yaxes(showgrid=True, gridcolor=grid_color)

    # Gráfico 3: Dispersión Precio vs. Ingreso Anual del cliente
    dff_disp = dff_year.copy()
    dff_disp['Annual Income'] = pd.to_numeric(dff_disp['Annual Income'], errors='coerce')
    dff_disp['Price ($)'] = pd.to_numeric(dff_disp['Price ($)'], errors='coerce')
    dff_disp = dff_disp.dropna(subset=['Annual Income', 'Price ($)'])
    scatter_colors = SCATTER_COLORS_DARK if color == "#222" else SCATTER_COLORS_LIGHT
    fig3 = px.scatter(
        dff_disp, x="Annual Income", y="Price ($)", color="Model",
        title=f"Precio vs. Ingreso anual ({brand} - {year})",
        labels={"Annual Income": "Ingreso anual", "Price ($)": "Precio ($)"},
        color_discrete_sequence=scatter_colors
    )
    fig3.update_layout(plot_bgcolor=color, paper_bgcolor=color, font_color=text_color, title_x=0.5)
    fig3.update_xaxes(showgrid=True, gridcolor=grid_color)
    fig3.update_yaxes(showgrid=True, gridcolor=grid_color)

    # Gráfico 4: Pastel por tipo de carrocería O por género
    pie_colors = scatter_colors
    if pie_value == "Body Style":
        fig4 = px.pie(
            dff_year, names="Body Style",
            title=f"Distribución por tipo de carrocería ({brand} - {year})",
            color_discrete_sequence=pie_colors
        )
    else:
        fig4 = px.pie(
            dff_year, names="Gender",
            title=f"Distribución por género ({brand} - {year})",
            color_discrete_sequence=pie_colors
        )
    fig4.update_layout(plot_bgcolor=color, paper_bgcolor=color, font_color=text_color, title_x=0.5)

    return fig1, fig2, fig3, fig4

if __name__ == "__main__":
    app.run(debug=True)
