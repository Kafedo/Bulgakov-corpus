# Bulgakov-corpus
Проект по предмету "Основы NLP".
Ссылка на сайт: *в процессе*

**Группа:**
* Федорищева Екатерина
* Воинская Алеся
* Серёгина Полина
* Бандулевич Мария

Наш корпус состоит из рассказов М. А. Булгакова из цикла “Записки юного врача”.

Это **9** рассказов, **3661** предложение или **34393** словоформы!

## Этапы работы
1) Скачивание тектов, их деление на предложения (Федорищева) 
2) Токенизация, получение граммразборов и формирование структуры корпуса (Воинская)
3) Создание функции поиска по структуре нескольких типов (Серёгина)
4) Разработка сайта (Бандулевич, Воинская)
5) Колупания с деплоем сайта (Бандулевич)
6) Колупания с красивым репозиторием и редактуройвсеговпоследниймомент (Федорищева)

## Структура репозитория
В папке _preprocessing_ лежат: 
* скрипт с краулером и первичной обработкой предложений, он работает с  папкой _texts_ (с исходниками рассказов) и возвращает _csv-файл_ (all_sentences.csv) структуры "предложение, источник, ссылка" 
* скрипт, делающий разбор каждого предложения из csv-файла, и выстраивающий структуру словаря, по которому будет производиться поиск, после сохраняет его в _json-файл_, используемый уже в следующей папке.

В папке _actually-corpus_ лежат:
* _all_sentences.json_ со словарём, содержащим корпус
* _search_function.py_ с функцией поиска по корпусу
* _flsite.py_ отвечает за запуск и работу всего сайта 
* папка _templates_ с шаблонами страниц сайта (_index.html_ — главная, _instruction.html_ — инструкция, _results.html_ — выдача, _base.html_ — меню с кнопками "Главная" и "Инструкция")
* папка _static_ с используемыми изображениями
* _requirements.txt_ содержит список требуемых модулей и их версии 

## Что может наш корпус?
В корпусе можно вбить запрос по описанным ниже правилам, чтобы найти соответствующие предложения. В выдаче вы увидите количество найденных предложений, сами предложения, а также название рассказов, откуда они взяты и ссылки на них. Всю эту информацию, так же как и сами предложения, вы сможете скопировать по отдельности с помощью специальной кнопки. Кроме этого, вам могут быть выведены в начале предупреждения, напоминающие о формате запросов. Если по вашему запросу ничего не будет найдено, вы увидите текст “Совпадений не найдено”. 

### **Правила запросов:** 

Во-первых, вы можете ввести только _от 1 до 3 валидных последовательностей_ (“токенов”), разделенных пробелом. Любое другое число токенов будет выдавать нулевое количество примеров и сообщение с напоминанием об этом правиле.

Во-вторых, примите во внимание, что _никакая пунктуация, которую вы вводите, не будет учитываться_ — кроме знаков "+", которые являются частью третьего типа запросов (об этом ниже). В связи с этим, к сожалению, наш корпус _не умеет обрабатывать слова с дефисами внутри_ (например, “где-нибудь”). Вы можете попробовать ввести либо первую, либо вторую часть такого слова, чтобы получить результаты (но не слитно и не обе через пробел). Заметим в скобках, что это связано в том числе и с недочетами разметки библиотеки SpaCy, на которой основывается наш корпус.

В-третьих, наш корпус поддерживает **4+1 типов запросов**.

Добавим также, что не играет роли, используете ли вы заглавные буквы или строчные во всем кроме тегов - теги всегда надо прописывать большими буквами.
#### Тип 1: _поиск по лемме_
Вы можете ввести слово в любой форме, и вам выпадут все предложения, содержащие введенную лемму.

_Например_: запросы _человек_, _люди_ и _людей_ найдут одинаковый набор предложений, в которых есть все слова с этой леммой.

#### Тип 2: _точный поиск_
Введите слово (или слова) в двойных кавычках - и вам выпадут предложения, содержащие точные совпадения по форме.

_Например_: запрос “человеку” выдаст только те предложения, в которых содержится эта конкретная форма.

#### Тип 3: _лемма+тег_ (часть речи)
Введите лемму (конкретная форма не важна), дальше знак + и тег из списка ниже _большими буквами_. _Разрывать эту последовательность пробелами запрещено_.

Разрешенные теги: 
* NOUN (существительное),
* ADJ (прилагательное),
* VERB (глагол),
* ADV (наречие),
* PROPN (имя собственное),
* INTJ (междометие),
* PRON (местоимение),
* DET (определительное местоимение),
* NUM (числительное),
* CCONJ (сочинительный союз),
* SCONJ (подчинительный союз),
* PART (частица),
* AUX (вспомогательный глагол)

Например: запрос _знать+NOUN_ выдаст все предложения с леммой _знать_, где оно - существительное.

#### Тип 4: _тег_
Введите тег из списка выше, чтобы найти все предложения, в которых содержится эта часть речи.

_Например_: запрос NOUN выдаст все предложения с существительными. <br>

#### Эти типы можно _комбинировать_: 
тогда в выдаче будут показаны только те предложения, в которых введенные вами токены встречаются в введенном вами порядке.

_Например_: запрос _ADJ люди_ выдаст вам все предложения корпуса, в которых перед леммой человек стоит прилагательное.

#### Тип +1: * (вывести все предложения)
По запросу * (звездочка, астериск) вы можете вывести все предложения, содержащиеся в корпусе

#### _**Особенности, чтобы на десяточку:**_
* Примеры (с источниками), можно _скопировать_ по отдельности с помощью специальной кнопки.
* _Защита от дурака_: напоминание о формате запроса, если ввод не подходит под формат, и уведомление, что по запросу ничего не найдено, если он верный, но в корпусе такого нет.
* _Вывод всех предложений_ корпуса через *.

