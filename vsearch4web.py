from flask import Flask, render_template, request, escape, session, copy_current_request_context
from searchletters import search4letters
from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from cheker import check_logged_in
from threading import Thread
from time import sleep

app = Flask(__name__) 

app.config['dbconfig'] = {'host': '127.0.0.1', 
                'user': 'vsearch', 
                'password': 'vsearchpasswd',
                'database': 'vsearchlogDB',}

app.secret_key = 'YouKnowWhatImean'

def do_login() ->str:
    session['logged_in'] = True
    return "You're now logged in."

def do_logout() ->str:
    session.pop('logged_in')
    return "You're now logged out" 

"""@app.route('/') 
def hello() -> 302 : #->str
    #return 'Hello world from Flask!'
    return redirect('/entry')"""

@app.route('/search4', methods=['POST'])
def do_search() -> 'html':
    # a = search4letters(phrase='life, the universe, and everything!', 
    #letters='eiru,!')
    #return ', '.join(a)  -  моё
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None: 
        sleep(15)
        """Журналирует веб-запрос и возвращаемые результаты"""
        with UseDatabase (app.config['dbconfig']) as cursor:
            _SQL = """insert into log 
                    (phrase, letters, ip, browser_string, results) 
                    values
                    (%s, %s, %s, %s, %s)"""
            cursor.execute(_SQL, (req.form['phrase'],
                                req.form['letters'],
                                req.remote_addr,
                                str(req.user_agent).partition('(')[0],
                                res, ))

    phrase = request.form['phrase']
    letters = request.form['letters']
    title = ('А вот и ваши результаты !')
    results = str(search4letters(phrase, letters))
    try:
        t = Thread(target=log_request, args=(request, results))
        t.start()
    except Exception as err:
        print('*****Упс, произошёл сбой с такой ошибкой: ', str(err))
    return render_template('results.html', 
                            the_results= results,
                            the_phrase = phrase, 
                            the_letters = letters, 
                            the_title = title)

@app.route('/') #перенесли метод просто сюда
@app.route('/entry')
def entry_page() ->'html': 
    return render_template('entry.html',
    the_title='Добро пожаловать в search4letters в интернете !')

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, 
                    results from log"""
            cursor.execute(_SQL)
            contents = cursor.fetchall()
        titles=('Фраза', 'Буквы для поиска', 'Адрес устройства', 'Браузер входа', 'Результаты')
        return render_template('viewlog.html',
                        the_title='Просмотр журнала',
                        the_row_titles=titles,
                        the_data=contents)                   
    except ConnectionError as err:
        print("Ваша база данных включена? Ошибка: ", str(err))
    except CredentialsError as err:
        print("Проблемы с логином/паролем пользователя. Ошибка: ", str(err))
    except SQLError as err:
        print("Ваш запрос верен? Ошибка: ", str(err))
    except Exception as err:
        print("Что-то пошло не так: ", str(err))
    return 'Error'

    """with open('vsearch.log') as log:  
        content = log.readlines()
        new_content = []
        for lines in content:
            new_content.append(lines.split('|'))
            #new_content = lines.split('|')
    return escape(str (new_content))
    #return escape(content) #чтобы посмотреть, как выглядят данные непосредственно в HTML доке (их)"""

if __name__ == '__main__': #добавили, чтобы открывалось как с облака, так и локально
    app.run(debug=True)