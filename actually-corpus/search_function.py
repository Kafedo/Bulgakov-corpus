import json
import spacy
import re

# модель спейси
nlp = spacy.load("ru_core_news_lg")

# загружаем джейсон
with open("all_sentences.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# словарь для поисковых запросов типа 1
data1 = {}
for i in data.keys():
    lemmas = ""
    for j in data[i]['words']:
        if data[i]['words'][j]['часть речи'] != "PUNCT" and data[i]['words'][j]['часть речи'] != "SPACE":
            lemmas = lemmas + data[i]['words'][j]['лемма'] + " "
    lemmas = " " + lemmas
    data1[i] = lemmas

# словарь для поисковых запросов типа 2
data2 = {}
for i in data.keys():
    lemmas = ""
    for j in data[i]['words']:
        if data[i]['words'][j]['часть речи'] != "PUNCT" and data[i]['words'][j]['часть речи'] != "SPACE":
            lemmas = lemmas + j.lower() + " "
    lemmas = " " + lemmas
    data2[i] = lemmas

# словарь для поисковых запросов типа 3
# для лемм
data3 = {}
for i in data.keys():
    lemmas = ""
    for j in data[i]['words']:
        if data[i]['words'][j]['часть речи'] != "PUNCT" and data[i]['words'][j]['часть речи'] != "SPACE":
            lemmas = lemmas + data[i]['words'][j]['лемма'] + "+" + data[i]['words'][j]['часть речи'] + " "
    lemmas = " " + lemmas
    data3[i] = lemmas

# словарь для поисковых запросов типа 4
data4 = {}
for i in data.keys():
    lemmas = ""
    for j in data[i]['words']:
        if data[i]['words'][j]['часть речи'] != "PUNCT" and data[i]['words'][j]['часть речи'] != "SPACE":
            lemmas = lemmas + data[i]['words'][j]['часть речи'] + " "
    lemmas = " " + lemmas
    data4[i] = lemmas

# подход "в лоб" - датасет
data_brute = {}
for sentence in data.keys():
    words = []
    s1 = data1[sentence].split()
    s2 = data2[sentence].split()
    s3 = data3[sentence].split()
    s4 = data4[sentence].split()
    for i in range(len(s1)):
        words.append(tuple([s1[i], s2[i], s3[i], s4[i]]))
    data_brute[sentence] = words

# а это словарь всех имеющихся pos-тегов, который тоже нужен далее по коду
pos_tags = set()
for i in data.keys():
    for j in data[i]['words']:
        pos_tags.add(data[i]['words'][j]['часть речи'])


# определение типа запроса
def types_func(query):
    tokens = query.split()  # делим на токены
    types = [0, 0, 0]  # список, куда будем класть номера типов

    # определяем тип только, если с кол-вом все в порядке
    if len(tokens) <= 3 and len(tokens) != 0:
        # рассмотрим отдельно:
        # если начинается и заканчивается на кавычки ("мама мама мама"), то все типы - вторые
        # но исключаем ситуацию типа: "мама" мама "мама"
        if query.startswith('"') and query.endswith('"') and len(tokens) == 3 and query.count('"') == 2:
            rr = []
            for i in range(len(tokens)):
                if re.fullmatch(r"[^\w\s+]+", tokens[i]):
                    rr.append[i]
            for ind in sorted(rr, reverse=True):
                del tokens[ind]
            for i in range(len(tokens)):
                types[i] = 2

        # стандартный алгоритм
        else:
            for i in range(len(tokens)):
                # если вплотную стоит ", то тип 2
                if tokens[i].startswith('"') or tokens[i].endswith('"'):
                    types[i] = 2
                # если все заглавные буквы и это допустимый pos-tag, то тип 4
                elif tokens[i].isupper() and tokens[i] in pos_tags and tokens[i] != 'PUNCT' and tokens[i] != 'SPACE':
                    types[i] = 4
                # если видим +, то тип 3
                elif '+' in tokens[i]:
                    types[i] = 3
                # все остальное - тип 1
                else:
                    types[i] = 1

    return types


# защита от дурака
def fool_proof(query, types):
    # делим на токены
    tokens = query.split()
    result = ''  # сюда сложим предложения с предупреждениями
    f = True  # а это флаг, который показывает, можно ли скармливать токены основной ф-ии
    # выкинем двойные кавычки - не стоит ругаться на соблюдение требований к типу запроса
    query = query.replace('"', '')

    # проверим длину
    query1 = re.sub(r'[^\w\s+]', '', query)
    tokens1 = query1.split()
    if len(tokens1) == 0 or len(tokens1) > 3 or query1 == '+':
        result += 'Недопустимая длина запроса (позволяется ввести от 1 до 3 токенов через пробел)' + '\n'
        f = False  # единственный случай, когда это нельзя отправлять в брут-форс - чревато ошибками
    # с длиной все в порядке
    else:
        if len(query1) != len(query):
            rem = []
            for i in range(len(tokens)):
                t = re.sub(r'[^\w\s+]', '', tokens[i])
                if t == '':
                    rem.append(i)
            for ind in sorted(rem, reverse=True):
                del tokens[ind]
        # предупреждение про знаки препинания
        if re.search(r'[^\w\s+]', query):  # нашли знаки препинания
            result += 'Внимание: все знаки препинания в строке кроме + будут игнорироваться' + '\n'
            if '-' in query:  # честно предупреждаем про дефис
                result += 'Кажется, у вас в строке оказался дефис: извините, но наш корпус не умеет обрабатывать токены, его содержащие. ' \
                          'Вы можете ввести ОДНУ часть этого слова - до или после дефиса (но не обе), чтобы поиск был удачным' + '\n'

        # проверка на соответствие типа
        for i in range(len(tokens)):
            if types[i] == 1:  # в типе 1 может оказаться тип 4
                if tokens[i].upper() in pos_tags and tokens[i] != 'PUNCT' and tokens[i] != 'SPACE':
                    result += 'Внимание: если вам нужен поиск по части речи, пишите ее pos-tag заглавными буквами' + '\n'
                if tokens[i].isupper() and (tokens[i] not in pos_tags or tokens[i] == 'PUNCT' or tokens[i] == 'SPACE'):
                    result += 'Внимание: если вам нужен поиск по части речи, сверьтесь со списком допустимых тегов' + '\n'
            if types[i] == 2:  # в типе 2 тоже может оказаться тип 4
                if (tokens[i].strip('"').upper() in pos_tags) or ('+' in tokens[i]):
                    result += 'Внимание: если вам нужен поиск по части речи, пишите ее вне кавычек' + '\n'
            if types[i] == 3:  # в типе 3 после + можно запихнуть фигню
                my_match = re.search(r'\+(.*)$', tokens[i])
                sequence_after_plus = my_match.group(1)
                if sequence_after_plus not in pos_tags and sequence_after_plus != 'PUNCT' and sequence_after_plus != 'SPACE':
                    result += 'Внимание: введенный после + тэг не валиден (проверьте, написан ли он заглавными буквами и взят ли он из допустимого списка)' + '\n'
                before_plus = tokens[i].split('+')[0]  # смотрим, что до + не тег
                if before_plus.strip('"').upper() in pos_tags:
                    result += 'Внимание: убедитесь, что до знака + написано слово, а не тег' + '\n'
                if re.sub(r'[^\w\s+]', '', before_plus) == '':
                    result += 'Внимание: до знака + должно быть что-то написано' + '\n'
                    f = False
            # для типа 4 не нашла подобных дырок (смотрела по тому, как присваивается тип в types_func), мб не права

    return f, result


# ф-я для приведения токена к формату в data_brute
def generate_tok_match(token, its_type):
    # для типа 1
    if its_type == 1:
        doc = nlp(token)
        tok = doc[0].lemma_
    # для типа 2
    elif its_type == 2:
        tok = token.lower()
    # для типа 3
    elif its_type == 3:
        before_plus = token.split('+')[0]
        doc = nlp(before_plus)
        my_match = re.search(r'\+(.*)$', token)
        sequence_after_plus = my_match.group(1)
        tok = doc[0].lemma_ + '+' + sequence_after_plus
    # для типа 4 (ну и если что-то ВДРУГ сломается с определением типа, то извините, хоть ошибку не выкинет, но и ничего не найдет, конечно)
    else:
        tok = token
    return tok


# главная ф-я, которая осуществляет поиск по предложениям
# я сломалась, fancy алгоритма поиска не будет
# просто fancy поиска (с доп фичами), как минимум, пока - тоже
def brute_force(query, types):
    query = re.sub(r'[^\w\s+]', '', query)  # пунктуацию - нафиг
    tokens = query.split()  # разделим на токены
    result = []  # сюда будем складывать найденные предложения
    texts = []  # только тексты
    info = []  # только источники
    links = []  # только ссылки

    # генерим токены в формате data_brute для сверки
    tok0 = generate_tok_match(tokens[0], types[0])
    if types[1] != 0:
        tok1 = generate_tok_match(tokens[1], types[1])
    if types[2] != 0:
        tok2 = generate_tok_match(tokens[2], types[2])

    # погнали по предложениям!
    for sentence in data.keys():
        # в каждом предложении идем по словам, ищем мэтч с заданной последовательностью
        # т.к. смотрим несколько последовательных слов, то от края отступаем на (кол-во токенов - 1)
        for i in range(len(data_brute[sentence]) - (len(tokens) - 1)):
            # если токенов 3: ищем, добавляем
            if len(tokens) == 3:
                if tok0 == data_brute[sentence][i][types[0] - 1] and tok1 == data_brute[sentence][i + 1][
                    types[1] - 1] and tok2 == data_brute[sentence][i + 2][types[2] - 1]:
                    if sentence not in result:
                        cleaned_sentence = re.sub(r'^\(\d+\)\s*', '', sentence)
                        result.append(
                            f"{cleaned_sentence}\n\nИсточник:\n{data[sentence]['text']} - {data[sentence]['link']}\n")
                        texts.append(cleaned_sentence)
                        info.append(data[sentence]['text'])
                        links.append(data[sentence]['link'])
            # если токенов 2: ищем, добавляем
            if len(tokens) == 2:
                if tok0 == data_brute[sentence][i][types[0] - 1] and tok1 == data_brute[sentence][i + 1][types[1] - 1]:
                    if sentence not in result:
                        cleaned_sentence = re.sub(r'^\(\d+\)\s*', '', sentence)
                        result.append(
                            f"{cleaned_sentence}\n\nИсточник:\n{data[sentence]['text']} - {data[sentence]['link']}\n")
                        texts.append(cleaned_sentence)
                        info.append(data[sentence]['text'])
                        links.append(data[sentence]['link'])
            # если токен 1: ищем, добавляем
            if len(tokens) == 1:
                if tok0 == data_brute[sentence][i][types[0] - 1]:
                    if sentence not in result:
                        cleaned_sentence = re.sub(r'^\(\d+\)\s*', '', sentence)
                        result.append(
                            f"{cleaned_sentence}\n\nИсточник:\n{data[sentence]['text']} - {data[sentence]['link']}\n")
                        texts.append(cleaned_sentence)
                        info.append(data[sentence]['text'])
                        links.append(data[sentence]['link'])

    return result, texts, info, links


# итоговая ф-я: собираем все воедино
def search(query):
    result = []
    texts = []
    info = []
    links = []
    k = 0  # кол-во предложений
    query1 = re.sub(r'[^\w\s*]', '', query)
    if query1.strip() == '*':
        for sentence in data.keys():
            cleaned_sentence = re.sub(r'^\(\d+\)\s*', '', sentence)
            result.append(f"{cleaned_sentence}\n\nИсточник:\n{data[sentence]['text']} - {data[sentence]['link']}\n")
            texts.append(cleaned_sentence)
            info.append(data[sentence]['text'])
            links.append(data[sentence]['link'])
        k = len(result)
    else:
        query2 = re.sub(r'(?<!\S)"(?=\S[^"]*\S)"|[^\w\s+"]', "", query)
        cleaned_query = re.sub(
            r'"([^"]*?)"',
            lambda m: '"' + re.sub(r"[^\w\s+]", "", m.group(1)).strip() + '"',
            query2
        )
        cleaned_query2 = re.sub(r'""', '', cleaned_query)
        # print(cleaned_query2)
        types = types_func(cleaned_query2)  # определяем типы запросов
        # print(types)
        flag = fool_proof(query, types)[0]  # в порядке ли длина?
        warning = fool_proof(query, types)[1]  # предупреждения

        # длина не в порядке: юзер идет лесом
        if flag == False:
            result = [warning]
            texts = []
            info = []
            links = []

        # длина в порядке
        else:
            if warning != '':  # кажется, лучше немного отделить предупреждения от основного текста
                warning += '\n'
            result = brute_force(query, types)[0]  # считаем результат
            texts = brute_force(query, types)[1]
            info = brute_force(query, types)[2]
            links = brute_force(query, types)[3]
            # если предложения нашлись: возвращаем предупреждение + предложения
            k = len(result)
            if len(result) != 0:
                if warning != '':  # добавляем предупреждение, только если оно не пустое
                    result.insert(0, warning)
            # если предложений не нашлось:
            else:
                result = ['Совпадений не найдено']
                if warning != '':  # добавляем предупреждение, только если оно не пустое
                    result.insert(0, warning)

    return result, k, texts, info, links
