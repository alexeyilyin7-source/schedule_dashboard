from dash import Dash, dcc, html, Input, Output, callback, dash_table  # Правильный импорт
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# --- 1. ЗАГРУЗКА ДАННЫХ ---
# Загружаем основные CSV-файлы
try:
    df_aud = pd.read_csv('data/Аудитории.csv', delimiter=';', encoding='utf-8')
    df_slots = pd.read_csv('data/Временные слоты.csv', delimiter=';', encoding='utf-8')
    df_disciplines = pd.read_csv('data/Дисциплины.csv', delimiter=';', encoding='utf-8')
    df_schedule = pd.read_csv('data/Записи в Расписании.csv', delimiter=';', encoding='utf-8')
    df_groups = pd.read_csv('data/Студенческие группы.csv', delimiter=';', encoding='utf-8')
    df_teachers = pd.read_csv('data/Преподаватели.csv', delimiter=';', encoding='utf-8')
    df_plans = pd.read_csv('data/Учебные планы.csv', delimiter=';', encoding='utf-8')

    # Небольшая предобработка для расписания, чтобы объединить с другими данными
    df_schedule = df_schedule.merge(df_disciplines[['ID_Дисциплины', 'Наименование']],
                                    left_on='ID_дисциплины', right_on='ID_Дисциплины', how='left')
    df_schedule = df_schedule.merge(df_slots[['ID_Слота', 'День_недели', 'НомерПары']],
                                    left_on='ID_Слота', right_on='ID_Слота', how='left')
    print("Данные успешно загружены!")
except FileNotFoundError as e:
    print(f"Ошибка загрузки файла: {e}. Убедитесь, что файлы находятся в папке 'data'.")
    # Создаем пустые DataFrame для избежания ошибок, если данные не найдены
    df_aud = pd.DataFrame()
    df_slots = pd.DataFrame()
    df_disciplines = pd.DataFrame()
    df_schedule = pd.DataFrame()
    df_groups = pd.DataFrame()
    df_teachers = pd.DataFrame()
    df_plans = pd.DataFrame()

# --- 2. ИНИЦИАЛИЗАЦИЯ ПРИЛОЖЕНИЯ ---
external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)  # Исправлено: Dash вместо dash_table.Dash
app.title = "АИС Расписание: Структура и Данные"
server = app.server

# --- 3. МАКЕТ ПРИЛОЖЕНИЯ (ИСПОЛЬЗУЕМ ВКЛАДКИ) ---
app.layout = html.Div(
    children=[
        # Шапка
        html.Div(
            children=[
                html.P(children="📅", className="header-emoji"),
                html.H1(
                    children="Автоматизированная система составления расписания",
                    className="header-title",
                ),
                html.P(
                    children="Визуализация структуры базы данных и просмотр учебного расписания",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        # Контейнер для вкладок и основного контента
        html.Div(
            children=[
                dcc.Tabs(
                    id="tabs",
                    value="tab-schema",
                    children=[
                        dcc.Tab(label="📐 Схема данных", value="tab-schema"),
                        dcc.Tab(label="📊 Данные расписания", value="tab-data"),
                    ],
                    className="dash-tabs",
                ),
                html.Div(id="tab-content", className="tab-content"),
            ],
            className="wrapper",
        ),
        # Подвал
        html.Div(
            children=[
                html.P("© 2026 Дипломный проект. На основе Государственного Университета Управления."),
            ],
            className="footer",
        ),
    ]
)


# --- 4. КОЛЛБЭК ДЛЯ ПЕРЕКЛЮЧЕНИЯ МЕЖДУ ВКЛАДКАМИ ---
@callback(
    Output("tab-content", "children"),
    Input("tabs", "value")
)
def render_tab(tab_name):
    if tab_name == "tab-schema":
        return render_schema_tab()
    elif tab_name == "tab-data":
        return render_data_tab()


# --- 5. ФУНКЦИИ ДЛЯ РЕНДЕРИНГА КАЖДОЙ ВКЛАДКИ ---

def render_schema_tab():
    """
    Вкладка "Схема данных".
    Здесь мы вручную создаем визуализацию структуры БД,
    используя информацию из диплома и ER-диаграммы.
    """
    # Данные для схемы (упрощенное представление)
    tables_info = {
        "Институты": {"pk": "ID_Института", "desc": "Справочник институтов"},
        "Кафедры": {"pk": "ID_Кафедры", "desc": "Справочник кафедр, связан с институтом"},
        "Преподаватели": {"pk": "ID_Преподавателя", "desc": "Данные о преподавателях"},
        "Студ.Группы": {"pk": "ID_Студ_Группы", "desc": "Учебные группы студентов"},
        "Дисциплины": {"pk": "ID_Дисциплины", "desc": "Справочник дисциплин"},
        "Учебные_Планы": {"pk": "ID_Записи_Учебного_Плана", "desc": "Связь групп, дисциплин и преподавателей"},
        "Аудитории": {"pk": "ID_Аудитории", "desc": "Аудиторный фонд"},
        "Временные_Слоты": {"pk": "ID_Слота", "desc": "Дни недели и время пар"},
        "Записи_в_расписании": {"pk": "ID_записи_в_расписании", "desc": "Готовое расписание"},
        "Пользователи": {"pk": "ID_Пользователя", "desc": "Учетные записи"},
        "Уведомления": {"pk": "ID_Уведомления", "desc": "Журнал уведомлений"},
    }

    # Создаем визуальное представление таблиц с помощью html.Div
    table_cards = []
    for table_name, info in tables_info.items():
        card = html.Div([
            html.H4(table_name,
                    style={'color': '#2A5298', 'margin-bottom': '5px', 'border-bottom': '2px solid #2A5298'}),
            html.P(f"PK: {info['pk']}", style={'fontSize': '14px', 'fontWeight': 'bold', 'color': '#1E3C72'}),
            html.P(info['desc'], style={'fontSize': '12px', 'color': '#666'}),
        ], style={
            'border': '1px solid #ddd',
            'borderRadius': '8px',
            'padding': '15px',
            'margin': '10px',
            'backgroundColor': '#f9f9f9',
            'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
            'width': '250px',
            'display': 'inline-block',
            'verticalAlign': 'top'
        })
        table_cards.append(card)

    # Текстовое описание связей из диплома
    relationships_desc = [
        "🔗 Институт (1) -- (M) Кафедра",
        "🔗 Кафедра (1) -- (M) Преподаватель",
        "🔗 Кафедра (1) -- (M) Студ.Группа",
        "🔗 Учебная группа (1) -- (M) Учебные_Планы",
        "🔗 Дисциплина (1) -- (M) Учебные_Планы",
        "🔗 Преподаватель (1) -- (M) Учебные_Планы",
        "🔗 Учебные_Планы (1) -- (M) Записи_в_расписании",
        "🔗 Аудитория (1) -- (M) Записи_в_расписании",
        "🔗 Временные_Слоты (1) -- (M) Записи_в_расписании",
        "🔗 Преподаватель (1) -- (1) Пользователи",
        "🔗 Пользователь (1) -- (M) Уведомления",
    ]

    return html.Div([
        html.H2("Логическая модель данных (IDEF1X)", style={'margin-bottom': '20px', 'color': '#1E3C72'}),
        html.P(
            "Ниже представлены основные сущности базы данных и связи между ними, спроектированные в дипломной работе.",
            style={'margin-bottom': '30px', 'fontSize': '16px'}),
        html.Div(table_cards, style={'textAlign': 'center'}),
        html.H3("Связи между сущностями", style={'margin-top': '40px', 'margin-bottom': '20px', 'color': '#1E3C72'}),
        html.Ul([html.Li(desc, style={'fontSize': '16px', 'marginBottom': '8px'}) for desc in relationships_desc],
                style={'listStyleType': 'none', 'paddingLeft': '20px'}),
    ])


def render_data_tab():
    """
    Вкладка "Данные расписания".
    Отображает таблицу с расписанием и фильтры.
    """
    # Проверяем, загрузились ли данные
    if df_schedule.empty or df_disciplines.empty or df_slots.empty:
        return html.Div("Ошибка: Не удалось загрузить данные. Проверьте файлы в папке 'data'.",
                        style={'color': 'red', 'fontSize': '18px', 'textAlign': 'center'})

    # Создаем элементы для фильтрации
    unique_days = ['Все'] + sorted(df_slots['День_недели'].unique().tolist())
    unique_disciplines = ['Все'] + sorted(df_disciplines['Наименование'].unique().tolist())

    return html.Div([
        html.H2("Просмотр записей расписания", style={'margin-bottom': '20px', 'color': '#1E3C72'}),

        # Блок фильтров
        html.Div([
            html.Div([
                html.Div("Фильтр по дню недели", className="menu-title"),
                dcc.Dropdown(
                    id='day-filter',
                    options=[{'label': day, 'value': day} for day in unique_days],
                    value='Все',
                    clearable=False,
                    className="dropdown"
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

            html.Div([
                html.Div("Фильтр по дисциплине", className="menu-title"),
                dcc.Dropdown(
                    id='discipline-filter',
                    options=[{'label': disc, 'value': disc} for disc in unique_disciplines],
                    value='Все',
                    clearable=False,
                    className="dropdown"
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'textAlign': 'center', 'backgroundColor': '#f8f9fa', 'borderRadius': '8px', 'padding': '20px',
                  'marginBottom': '30px'}),

        # Таблица для отображения данных
        html.Div(id='schedule-table-container')
    ])


# --- 6. КОЛЛБЭК ДЛЯ ОБНОВЛЕНИЯ ТАБЛИЦЫ НА ВКЛАДКЕ "ДАННЫЕ" ---
@callback(
    Output('schedule-table-container', 'children'),
    [Input('day-filter', 'value'),
     Input('discipline-filter', 'value')]
)
def update_schedule_table(selected_day, selected_discipline):
    # Начинаем с полного датасета расписания
    filtered_df = df_schedule.copy()

    # Применяем фильтры
    if selected_day != 'Все':
        filtered_df = filtered_df[filtered_df['День_недели'] == selected_day]
    if selected_discipline != 'Все':
        filtered_df = filtered_df[filtered_df['Наименование'] == selected_discipline]

    # Выбираем и переименовываем колонки для красивого отображения
    display_cols = {
        'ID_записи_в_расписании': 'ID',
        'День_недели': 'День',
        'НомерПары': 'Пара',
        'Наименование': 'Дисциплина',
        'ID_Аудитории': 'Ауд. ID',
        'Чётность_недели': 'Четность',
        'Флаг_отмены_занятия': 'Отмена'
    }

    # Выбираем только те колонки, которые есть в DataFrame
    available_cols = {k: v for k, v in display_cols.items() if k in filtered_df.columns}
    df_to_display = filtered_df[list(available_cols.keys())].rename(columns=available_cols)

    if df_to_display.empty:
        return html.Div("Нет данных для отображения с выбранными фильтрами.",
                        style={'textAlign': 'center', 'padding': '20px'})

    # Создаем таблицу с помощью Dash DataTable для интерактивности
    table = dash_table.DataTable(
        data=df_to_display.to_dict('records'),
        columns=[{"name": i, "id": i} for i in df_to_display.columns],
        page_size=15,
        style_table={'overflowX': 'auto'},
        style_cell={
            'textAlign': 'left',
            'padding': '10px',
            'fontFamily': 'Lato, sans-serif',
            'fontSize': '14px',
            'minWidth': '100px',
        },
        style_header={
            'backgroundColor': '#2A5298',
            'color': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        filter_action="native",
        sort_action="native",
        sort_mode="multi",
    )
    return html.Div([
        html.P(f"Найдено записей: {len(df_to_display)}", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
        table
    ])


# --- 7. ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')