from typing import Dict, List
import fitz


class GetErrors:
    __slots__ = ['_error_numbers', '_pdf_path', '_start_page', '_end_page', '_page_text', '_current_error',
                 '_extract_errors', '_dict_errors']

    def __init__(self, pdf_path, start_page, end_page):
        """
        Класс для извлечения информации об ошибках из PDF-файла.

        Параметры:
        - pdf_path (str): Путь к PDF-файлу.
        - start_page (int): Номер страницы, с которой начать извлечение.
        - end_page (int): Номер страницы, на которой закончить извлечение.

        Атрибуты:
        - _error_numbers (List[str]): Список кодов ошибок в формате строки.
        - _pdf_path (str): Путь к PDF-файлу.
        - _start_page (int): Номер страницы, с которой начать извлечение.
        - _end_page (int): Номер страницы, на которой закончить извлечение.
        - _page_text (str): Текст страниц PDF-файла.
        - _current_error (List[str]): Текущая ошибка, представленная списком [код, описание].
        - _extract_errors (List[List[str]]): Список извлеченных ошибок.
        - _dict_errors (Dict[str, Dict[str, str]]): Словарь, содержащий информацию об ошибках.

        Методы:
        - _open_pdf(): Открывает PDF-файл и возвращает текст страниц в виде строки.
        - _extract_num_and_name(): Извлекает номер и название ошибки из текста страниц.
        - _added_description_to_dict(): Добавляет описание ошибок в словарь _dict_errors.
        - get_data(num_error: str) -> Dict[str, str]: Возвращает информацию о конкретной ошибке по её номеру.
        - all_data() -> Dict[str, Dict[str, str]]: Возвращает все словари с ошибками
        """
        self._error_numbers: List[str] = [str(x).zfill(4) for x in range(0, 99)]
        self._pdf_path: str = pdf_path
        self._start_page: int = start_page
        self._end_page: int = end_page
        self._page_text: str = self._open_pdf()
        self._current_error: List[str] | None = None
        self._extract_errors: List[List[str]] = self._extract_num_and_name()
        self._dict_errors: Dict[str, Dict[str, str]] = self._added_description_to_dict()

    def _open_pdf(self) -> str:
        """
        Открывает PDF-файл и возвращает текст страниц в виде строки.
        """
        tmp_page = ''
        with fitz.open(self._pdf_path) as pdf:
            for page_num in range(self._start_page, self._end_page):
                page = pdf[page_num]
                tmp_page += '\n' + page.get_text()
        return tmp_page

    def _extract_num_and_name(self) -> List[List[str]]:
        """
        Извлекает номер и название ошибки из текста страниц.
        """
        extract_errors = []
        for line in self._page_text.split('\n'):
            if '...........' not in line:
                error_code = next(
                    (code for code in self._error_numbers if line.startswith(code) or line.startswith(f' {code}')),
                    None)
                if error_code:
                    if self._current_error is not None:
                        extract_errors.append(self._current_error)
                    self._current_error = line.split(f' ', 1)
                    if self._current_error[-1].startswith(f'{error_code}'):
                        self._current_error = self._current_error[-1].split(f' ', 1)
                    elif self._current_error[-1].startswith('+ axis: [AXIS n]'):
                        self._current_error[0] += ' + axis: [AXIS n]'
                else:
                    if self._current_error is not None:
                        self._current_error[-1] += ' ' + line.strip()
        if self._current_error is not None:
            extract_errors.append(self._current_error)
        return extract_errors

    def _added_description_to_dict(self) -> Dict[str, Dict[str, str]]:
        """
        Составвляет и добавляет описание ошибок в словарь _dict_errors.
        """
        tmp_dict = {}
        for data in self._extract_errors:
            tmp_dict[data[0]] = {}
            cause_start = data[-1].find("Cause: ")
            effect_start = data[-1].find("Effect: ")
            remedy_start = data[-1].find("Remedy: ")
            notes_start = data[-1].find("Notes: ")
            tmp_dict[data[0]]["Cause"] = data[-1][cause_start + len("Cause: "):effect_start].strip()
            tmp_dict[data[0]]["Effect"] = data[-1][effect_start + len("Effect: "):remedy_start].strip()
            tmp_dict[data[0]]["Remedy"] = data[-1][remedy_start + len("Remedy: "):notes_start].strip()
            tmp_dict[data[0]]["Notes"] = data[-1][notes_start + len("Notes: "):].strip()
        return tmp_dict

    def get_data(self, num_error: str) -> Dict[str, str]:
        """
        Возвращает информацию о конкретной ошибке по её номеру.

        Attributes:
        - num_error (str): Номер ошибки.

        Returns:
            Dict[str, str]: Словарь, содержащий информацию о конкретной ошибке по её номеру.
        """
        return self._dict_errors[num_error]

    def all_data(self) -> Dict[str, Dict[str, str]]:
        """
        Возвращает все словари с информацией об ошибках.

        Returns:
            Dict[str, Dict[str, str]]: Словари, содержащие информацию об ошибках.
        """
        return self._dict_errors


