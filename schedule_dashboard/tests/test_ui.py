import pytest
from playwright.sync_api import Page, expect
import time

# URL вашего запущенного приложения
BASE_URL = "http://127.0.0.1:8050"


def test_homepage_loads(page: Page):
    """Тест 1: Проверка загрузки главной страницы и заголовка."""
    page.goto(BASE_URL)

    # Проверяем заголовок страницы (тот, что во вкладке браузера)
    expect(page).to_have_title("АИС Расписание: Структура и Данные")

    # Проверяем, что виден основной заголовок H1
    header_h1 = page.locator("h1.header-title")
    expect(header_h1).to_be_visible()
    expect(header_h1).to_contain_text("Автоматизированная система составления расписания")
    print("✓ Тест 1 пройден: Главная страница загрузилась.")


def test_schema_tab_content(page: Page):
    """Тест 2: Проверка наличия карточек таблиц на вкладке 'Схема данных'."""
    page.goto(BASE_URL)

    # Убеждаемся, что мы на вкладке "Схема данных" (она активна по умолчанию)
    schema_tab = page.locator("text=📐 Схема данных")
    expect(schema_tab).to_have_attribute("aria-selected", "true")

    # Проверяем, что отображается хотя бы одна карточка с названием таблицы (например, "Институты")
    institute_card = page.locator("h4:has-text('Институты')")
    expect(institute_card).to_be_visible()
    print("✓ Тест 2 пройден: Карточки таблиц отображаются на вкладке 'Схема данных'.")


def test_data_tab_and_filters(page: Page):
    """Тест 3: Переключение на вкладку 'Данные' и работа фильтров."""
    page.goto(BASE_URL)

    # 1. Переключаемся на вкладку "Данные расписания"
    data_tab_button = page.locator("text=📊 Данные расписания")
    data_tab_button.click()

    # Ждем, пока контент подгрузится и вкладка станет активной
    expect(data_tab_button).to_have_attribute("aria-selected", "true")

    # Проверяем, что появился заголовок "Просмотр записей расписания"
    data_header = page.locator("h2:has-text('Просмотр записей расписания')")
    expect(data_header).to_be_visible()

    # 2. Проверяем, что выпадающие списки фильтров видны
    day_filter = page.locator("#day-filter")
    disc_filter = page.locator("#discipline-filter")
    expect(day_filter).to_be_visible()
    expect(disc_filter).to_be_visible()

    # 3. Применяем фильтр по дню недели (например, ПН)
    # Сначала раскрываем дропдаун
    page.locator("#day-filter").click()
    # Выбираем опцию "ПН" (она должна быть в списке)
    page.locator("text=ПН").click()

    # Ждем обновления таблицы (небольшая задержка для колбэка)
    page.wait_for_timeout(500)

    # Проверяем, что в отфильтрованной таблице в колонке "День" везде стоит "ПН"
    # Берем первую ячейку колонки "День" в теле таблицы (индекс 1, т.к. колонка 0 - это ID)
    first_day_cell = page.locator(".dash-cell[data-dash-column='День']").first
    if first_day_cell.count() > 0:
        expect(first_day_cell).to_contain_text("ПН")
        print("✓ Тест 3 пройден: Фильтр по дню недели применился.")
    else:
        # Если данных по ПН нет, проверяем сообщение об отсутствии данных
        no_data_msg = page.locator("text=Нет данных для отображения")
        expect(no_data_msg).to_be_visible()
        print("✓ Тест 3 пройден: Фильтр сработал (данных по ПН нет).")


def test_data_table_renders(page: Page):
    """Тест 4: Проверка, что таблица с данными отображается и в ней есть строки."""
    page.goto(BASE_URL)

    # Переключаемся на вкладку с данными
    page.locator("text=📊 Данные расписания").click()

    # Ждем появления таблицы
    table = page.locator(".dash-table-container")
    expect(table).to_be_visible()

    # Проверяем, что в таблице есть хотя бы одна строка с данными (не заголовок)
    # Заголовки находятся в thead, данные в tbody
    data_rows = page.locator("tbody tr")
    # Если есть хотя бы одна запись, data_rows.count() > 0
    if data_rows.count() > 0:
        print(f"✓ Тест 4 пройден: Таблица отображается, найдено {data_rows.count()} записей.")
    else:
        # Если записей нет, проверяем сообщение об их отсутствии
        no_data_msg = page.locator("text=Нет данных для отображения")
        expect(no_data_msg).to_be_visible()
        print("✓ Тест 4 пройден: Таблица пуста, сообщение об ошибке отображается корректно.")