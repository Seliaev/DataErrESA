import os

from flask import Flask, render_template, jsonify, abort
from utils.get_error_from_pdf import GetErrors

app = Flask(__name__)
root = os.getcwd()
file_path = os.path.join(root, 'utils', '752md1gb.pdf')
if not os.path.isfile(file_path):
    raise FileNotFoundError(f'File not found: {file_path}')

e = GetErrors(pdf_path=file_path, start_page=1, end_page=80)

@app.route('/')
def index() -> render_template:
    """
    Отображает главную страницу веб-приложения.

    Returns:
    - render_template: HTML-шаблон с выпадающим меню ошибок.
    """
    errors_list = list(e.all_data().keys())
    return render_template('index.html', errors_list=errors_list)


@app.route('/get_error_data/<num_error>')
def get_error_data(num_error: str) -> jsonify:
    """
    Обрабатывает запрос на получение данных об ошибке по её номеру.

    Attributes:
    - num_error (str): Номер ошибки.

    Returns:
    - jsonify: JSON-представление данных об ошибке.
    """
    try:
        error_data = e.get_data(num_error)
        return jsonify(error_data)
    except KeyError:
        abort(404)
    except Exception as ex:
        abort(500)




@app.errorhandler(404)
def page_not_found(error):
    return "Страница не найдена", 404



@app.errorhandler(500)
def internal_server_error(error):
    return "Внутренняя ошибка сервера", 500
