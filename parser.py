from bs4 import BeautifulSoup as bs
import requests
import fake_useragent
import math
import time

EMAIL = ''
PASSWORD = ''
LOGINS = ['sergey2304s@mail.ru']


#------------ Функция выбора блока ----------------
def block_chooser():
    while True:
        try:
            block = int(input('Введите номер блока (цифра): '))
            if 1 <= block <= 9:
                return (113 - block)
            raise Exception
        except:
            print('Ошибка ввода')

#------------ Функция выбора домашки ----------------
# TODO: нормально парсить номера домашек
def hw_chooser(block):
    while True:
        try:
            hw = int(input('Введите номер домашки (число, для пробника 0): '))
            if hw == 0:
                return 818
            if (1 + 8 * (block-1)) <= hw <= (8 * block):
                if block == 3:
                    return (731 + hw)
                elif block == 2:
                    return (488 + hw)
                else:
                    print('Пока не сделал')
                    return (731 + hw)
            raise Exception
        except:
            print('Ошибка ввода')

#------------ Функция получения кол-ва страниц ----------------
def get_number_of_pages(block, hw, session, header):
    print('Обрабатываю информацию...')
    try:
        hw_url = 'https://api.100points.ru/student_homework/index?status=passed&course_id=34&module_id={}&lesson_id={}&page={}'.format(block, hw, 1)
        hw_responce = session.get(hw_url, headers=header).text
        hw_soup = bs(hw_responce, "html.parser")
        pages = math.ceil(int(hw_soup.find('div', class_='dataTables_info').text.split()[-1]) / 15)
        return pages
    except:
        return 1 

def get_probnik_results(session, header, url):
    hw_responce = session.get(url, headers=header).text
    hw_soup = bs(hw_responce, "html.parser")
    a = hw_soup.find_all('option')
    out = ''
    for i in range(len(a)):
        a[i] = str(a[i])
        if "selected" in a[i]:
            out += a[i].split('">')[1].split('<')[0] + ' '
    return out.strip()
        


#------------ Ввод почты и пароля ----------------
def main():
    global EMAIL
    global PASSWORD

    session = requests.Session()
    user = fake_useragent.UserAgent().random

    login_url = "https://api.100points.ru/login"
    if len(EMAIL) == 0:
        email = input('Введите почту: ')
        if email not in LOGINS:
            print("Пользователя нет в базе, обратитесь к разработчику")
            time.sleep(3)
            return(0)
            
        password = input('Введите пароль (если он такой же, как почта, просто нажмите Enter): ')
        EMAIL = email
        PASSWORD = password
    else:
        email = EMAIL
        password = PASSWORD

    # email = 'sergey2304s@mail.ru'
    # password = 'sergey2304s@mail.ru'
    if password == '':
        password = email

    header = {'user-agent': user}
    data = {
        'email': email,
        'password': password
    }

    session.headers.update(header)
    responce = session.post(login_url, data=data)

    #------------ Выбор домашки ----------------
    block_num = block_chooser()
    hw_num = hw_chooser(113 - block_num)
    pages = get_number_of_pages(block_num, hw_num, session, header)
    
    output = {}

    for page in range(1, pages + 1):
        hw_url = 'https://api.100points.ru/student_homework/index?status=passed&course_id=34&module_id={}&lesson_id={}&page={}'.format(block_num, hw_num, page)
        hw_responce = session.get(hw_url, headers=header).text
        hw_soup = bs(hw_responce, "html.parser")
        links = hw_soup.find_all('a', class_='btn btn-xs bg-purple')
        for i in range(len(links)):
            links[i] = links[i].get('href')

        for link in links:
            link_responce = session.get(link, headers=header).text
            link_soup = bs(link_responce, "html.parser")
            temp = link_soup.find_all('input', class_='form-control')
            name = temp[2].get('value')
            name = name.split()[1] + ' ' + name.split()[0]
            if hw_num == 818:
                link += '?status=checked'
                res = get_probnik_results(session, header, link)
                if len(res.split()) == 26:
                    res += ' ?'
                output[name] = res
            else:
                temp = link_soup.find_all('div', class_='form-group col-md-3')
                temp = temp[4].text
                result = temp.split()[-1]
                result = int(result.replace('%', ''))
                output[name] = result

    output = dict(sorted(output.items(), key=lambda x: x[0]))
    for st in output:
        l = 30 - len(st) - len(str(output[st]))
        if l < 1:
            l = 100 - len(st) - len(str(output[st]))
        print(st, ' ' * l, output[st])

    print('--------------------------------------------------------')

    a = input('Нажмите Enter для завершения работы программы \nВведите любой символ и нажмите Enter для просмотра другой домашки: ')
    if a:
        main()
    return 0


if __name__ == '__main__':
    main()
