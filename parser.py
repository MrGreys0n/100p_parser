from bs4 import BeautifulSoup as bs
import requests
import fake_useragent
import math


EMAIL = ''
PASSWORD = ''
COURSE_ID = 0
PROBNIK = []
IS_PROBNIK = False
flag = False
TRANSLATE_TABLE_MATH = {
    1: 6,
    2: 11,
    3: 17,
    4: 22,
    5: 27,
    6: 34,
    7: 40,
    8: 46,
    9: 52,
    10: 58,
    11: 64,
    12: 66,
    13: 68,
    14: 70,
    15: 72,
    16: 74,
    17: 76,
    18: 78,
    19: 80,
    20: 82,
    21: 84,
    22: 86,
    23: 88,
    24: 90,
    25: 92,
    26: 94,
    27: 96,
    28: 98,
    29: 100,
    30: 100,
    31: 100
}


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
            for s in range(len(students)):
                if len(students[s].split()) == 1:
                    for i in range(1, len(students[s])):
                        if students[s][i] == students[s][i].upper():
                            students[s] = students[s][:i] + ' ' + students[s][i:]
                            break
                f.write(students[s] + '\n')
            f.write('*')
            print('Группа успешно сохранена!')
        f.close()
    print("Рекомендуется перезапустить программу (на некоторых устройствах могут возникнуть непредвиденные ошибки, если этого не сделать)")

def get_students():
    try:
        with open('students.txt') as f:
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
def block_chooser(session, header):
    global flag
    global COURSE_ID
    while True:
        try:
            url = 'https://api.100points.ru/student_homework/index?status=passed&course_id={}'.format(COURSE_ID)
            hw_responce = session.get(url, headers=header).text
            hw_soup = bs(hw_responce, "html.parser")
            a = hw_soup.find_all('option')
            block_list = []
            for i in a:
                if "блок" in i.text.lower():
                    block_list.append(i.text.strip() + ': ID = ' + i['value'])
            block_list.sort()
            for i in block_list:
                print(i)
            block = int(input('Введите ID блока (ЧИСЛО) (если хотите изменить списки своих групп, введите 0): '))
            if block == 0:
                flag = True
                group_maker()
                break
            return block
        except Exception as e:
            print(e)
            print('Ошибка ввода')

#------------ Функция выбора домашки ----------------
def hw_chooser(block, session, header):
    global PROBNIK
    global COURSE_ID
    while True:
        try:
            url = 'https://api.100points.ru/student_homework/index?status=passed&course_id={}&module_id={}'.format(COURSE_ID, block)
            hw_responce = session.get(url, headers=header).text
            hw_soup = bs(hw_responce, "html.parser")
            a = hw_soup.find_all('option')
            hws_list = []
            for i in a:
                if ("урок" in i.text.lower() or 'пробник' in i.text.lower()) and 'все уроки' not in i.text.lower():
                    hws_list.append(i.text.strip() + ': ID = ' + i['value'])
                    if 'пробник' in i.text.lower():
                        PROBNIK.append(int(i['value']))
            hws_list.sort()
            for i in hws_list:
                print(i)
            hw_str = input('Введите id домашки: ')
            hw = int(hw_str)
            return hw
        except Exception as e:
            print(e)
            print('Ошибка ввода')

#------------ Функция получения кол-ва страниц ----------------
def get_number_of_pages(block, hw, session, header):
    try:
        hw_url = 'https://api.100points.ru/student_homework/index?status=passed&course_id={}&module_id={}&lesson_id={}&page={}'.format(COURSE_ID, block, hw, 1)
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
    global flag
    global PROBNIK
    global COURSE_ID
    global IS_PROBNIK

    secondary = False
    with_soch = False

    session = requests.Session()
    user = fake_useragent.UserAgent().random

    login_url = "https://api.100points.ru/login"
    if len(EMAIL) == 0:
        email = input('Введите почту: ')
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

    # courses = {"1": 25, "2": 34}
    # course_num = input("Введите номер курса (1 (Легион) или 2 (Гуляка)): ")
    # COURSE_ID = courses[course_num]
    rus = [34, 79]
    courses = {"1": 34, "2": 79}
    course_num = input("Введите номер курса (1 (Гуляка) или 2 (Гуляка 2.0)): ")
    COURSE_ID = courses[course_num]

    #------------ Выбор домашки ----------------
    block_num = block_chooser(session, header)
    while flag:
        block_num = block_chooser()

    hw_num = hw_chooser(block_num, session, header)
    pages = get_number_of_pages(block_num, hw_num, session, header)
    
    if COURSE_ID == 25:
        s = input('Это пробник (да/нет): ')
        if s.lower() == 'да':
            IS_PROBNIK = True
            s = input('Вторичные баллы (да/нет): ')
            if s.lower() == 'да':
                secondary = True
    elif COURSE_ID in rus:
        s = input('Сочинение (да/нет): ')
        if s.lower() == 'да':
            with_soch = True
    
    print('Обработка информации может занять длительное время...')
    
    output = {}

    for page in range(1, pages + 1):
        hw_url = 'https://api.100points.ru/student_homework/index?status=passed&course_id={}&module_id={}&lesson_id={}&page={}'.format(COURSE_ID, block_num, hw_num, page)
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
            if IS_PROBNIK and COURSE_ID == 25:
                temp = link_soup.find_all('div', class_='form-group col-md-3')
                result = temp[5].text.split()[-1].split('/')[0]
                if secondary:
                    result = str(TRANSLATE_TABLE_MATH[int(result)])
                output[name] = result
            else:
                temp = link_soup.find_all('div', class_='form-group col-md-3')
                result = temp[5].text.split()[2].split('/')[0]
                if with_soch:
                    result += ' ' + str ( int(temp[5].text.split()[-1].split('/')[0]) - int(result) )
                output[name] = result

    output = dict(sorted(output.items(), key=lambda x: x[0]))
    final = []
    unknown = []
    for group in stud_list:
        f = []
        for student in group:
            if student in output.keys():
                if len(student.split()) == 1:
                    f.append(student + ' ? '  + output[student])
                else:
                    f.append(student + ' ' + output[student])
                del output[student]
            else:
                final_res = '0'
                if with_soch and COURSE_ID in rus:
                    final_res += ' 0'
                if len(student.split()) == 1:
                    f.append(student + ' ? '  + final_res)
                else:
                    f.append(student + ' ' + final_res)
        final.append(f)
    for student in output:
        unknown.append(student + ' ' + output[student])
    a = input("Для вывода результатов в консоли нажмите enter: ")
    if a == '':
        for i in range(num_of_groups):
            print('Группа №{}:'.format(i+1))
            for student in final[i]:
                st = student.split()
                l = 40 - len(st[0]) - len(st[1]) - 2
                if len(st) == 3:
                    print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])), st[2])
                elif len(st) == 4:
                    print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])), st[2], st[3])

            print('------------------------------------------------------------------------------------------------------------')
            a = input('Для вывода удобного столбика для копирования нажмите 0 и enter, для продолжения работы - просто enter: ')
            if a == '0':
                for student in final[i]:
                    st = student.split()[2:]
                    if len(st) == 1 and hw_num in PROBNIK:
                        print(0)
                    else:
                        print(' '.join(st))
                input('Нажмите enter для продолжения работы...')
        print('Ученики, которых нет в списке, но есть на сайте:')
        for i in unknown:
            st = i.split()
            if st[1] in ["0", "1"]:
                temp = [st[0], '?']
                for x in st[1:]:
                    temp.append(x)
                st = temp
            l = 40 - len(st[0]) - len(st[1]) - 2
            print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])), end='')
            del st[0:2]
            summa = 0
            for x in st:
                print(x, end=' ')
            print()
            
        print('------------------------------------------------------------------------------------------------------------')

    print('------------------------------------------------------------------------------------------------------------')

    a = input('Нажмите Enter для завершения работы программы \nВведите любой символ и нажмите Enter для просмотра другой домашки: ')
    if a:
        main()
    return 0


if __name__ == '__main__':
    main()
