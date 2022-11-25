from bs4 import BeautifulSoup as bs
import requests
import fake_useragent
import math
import time

EMAIL = 'sergey2304s@mail.ru'
PASSWORD = ''
LOGINS = ['sergey2304s@mail.ru']


def group_maker():
    print("ВАЖНО! Сначала убедитесь, что имя и фамилия ученика, которые вы вводите, полностью совпадают с информацией на сайте!")
    number_of_groups = int(input("Введите количество групп: "))
    with open('students.txt', 'w') as f:
        for i in range(number_of_groups):
            number_of_students = int(input("Введите количество учеников в группе №{}: ".format(i+1)))
            students = []
            print('Вводите учеников (по одному в строку):')
            for _ in range(number_of_students):
                students.append(input().replace('\t', ' '))
            for s in students:
                f.write(s + '\n')
            f.write('*')
            print('Группа успешно сохранена!')
    '''
    with open('F:\students.txt', 'r') as f:
        a = [x for x in f.read().split('*') if x != '']
        print(a)
    '''

def get_students():
    try:
        with open('students.txt', 'r') as f:
            a = [x.split('\n') for x in f.read().split('*') if x != '']
            for i in range(len(a)):
                if a[i][-1] == '':
                    a[i].pop(-1)
            return a
    except FileNotFoundError:
        print("Сначала нужно задать список учеников")
        group_maker()
        return get_students()

#------------ Функция выбора блока ----------------
def block_chooser():
    while True:
        try:
            block = int(input('Введите номер блока (цифра) (если хотите изменить списки своих групп, введите 0): '))
            if 1 <= block <= 9:
                return (113 - block)
            if block == 0:
                group_maker()
                return block_chooser()
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
    if password == '':
        password = email

    header = {'user-agent': user}
    data = {
        'email': email,
        'password': password
    }

    session.headers.update(header)
    responce = session.post(login_url, data=data)

    stud_list = get_students()
    num_of_groups = len(stud_list)

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
            #name = name.split()[1] + ' ' + name.split()[0]
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
                result = result.replace('%', '')
                output[name] = result

    output = dict(sorted(output.items(), key=lambda x: x[0]))
    final = []
    for group in stud_list:
        f = []
        for student in group:
            if student in output.keys():
                f.append(student + ' ' + output[student])
            else:
                f.append(student + ' ' + '0')
        final.append(f)
    a = input("Для вывода результатов в консоли нажмите 0 и enter, для вывода в эксель - 1 и enter: ")
    if a == '0':
        for i in range(num_of_groups):
            print('Группа №{}:'.format(i+1))
            for student in final[i]:
                st = student.split()
                print(st[0], st[1], ' ' * (40 - len(student)), st[2])
            print('--------------------------------------------------------')
            a = input('Для вывода удобного столбика для копирования нажмите 1 и enter, для продолжения работы - просто enter: ')
            if a == '1':
                for student in final[i]:
                    print(student.split()[2])
                input('Нажмите enter для продолжения работы...')

    elif a == '1':
        pass

    print('--------------------------------------------------------')

    a = input('Нажмите Enter для завершения работы программы \nВведите любой символ и нажмите Enter для просмотра другой домашки: ')
    if a:
        main()
    return 0


if __name__ == '__main__':
    main()
