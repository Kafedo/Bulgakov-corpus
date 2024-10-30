from flask import Flask, render_template, url_for, request
from search_function import search
from markupsafe import Markup

app = Flask(__name__)


# Кастомный фильтр для замены \n на <br>
# (понадобится при принте результатов из функции поиска)
@app.template_filter("nl2br")
def nl2br(value):
    return Markup(value.replace("\n", "<br>"))


@app.route("/")  # Главная страница с формой поиска
def index():
    return render_template("index.html")


@app.route("/results")  # Страница с результатами поиска
def results():
    query = request.args.get("search", "")  # Получаем запрос из URL-параметров
    # request.args позволяет получить параметры, переданные в URL.
    # Если в URL указан параметр search, его значение будет присвоено переменной query.
    # Если параметр не найден, используется пустая строка "".

    results, count, texts, info, links = search(query)  # Используем функцию поиска из search_function.py
    results_length = len(results)
    # Отображаем страницу с результатами
    return render_template("results.html", query=query, results=results, count=count,
                           texts=texts, info=info, links=links, results_length=results_length)


@app.route("/instruction")  # отображение страницы с инструкцией
def instruction():
    return render_template('instruction.html')


if __name__ == "__main__":
    app.run(debug=True)
