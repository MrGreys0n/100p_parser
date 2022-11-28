from bs4 import BeautifulSoup as bs
import requests
import fake_useragent
import math

#EMAIL = 'sergey2304s@mail.ru'
EMAIL = ''
PASSWORD = ''
PROBNIK = [818, 536]
flag = False

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
    '''
    with open('F:\students.txt', 'r') as f:
        a = [x for x in f.read().split('*') if x != '']
        print(a)
    '''

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
def block_chooser():
    global flag
    while True:
        try:
            block = int(input('Введите номер блока (цифра) (если хотите изменить списки своих групп, введите 0): '))
            if 1 <= block <= 9:
                flag = False
                return (113 - block)
            if block == 0:
                flag = True
                group_maker()
                break
            raise Exception
        except Exception as e:
            print(e)
            print('Ошибка ввода')

#------------ Функция выбора домашки ----------------
# TODO: нормально парсить номера домашек
def hw_chooser(block):
    while True:
        try:
            hw = int(input('Введите номер домашки (число, для пробника 0): '))
            if hw == 0:
                if block == 3:
                    return 818
                elif block == 2:
                    return 536
            if (1 + 8 * (block-1)) <= hw <= (8 * block):
                if block == 3:
                    return (731 + hw)
                elif block == 2:
                    return (488 + hw)
                else:
                    print('Пока ничего нет')
                    return hw_chooser(block)
            raise Exception
        except:
            print('Ошибка ввода')

#------------ Функция получения кол-ва страниц ----------------
def get_number_of_pages(block, hw, session, header):
    print('Обрабатка информации может занять длительное время...')
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
    global flag

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

    #------------ Выбор домашки ----------------
    block_num = block_chooser()
    while flag:
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
            if hw_num in PROBNIK:
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
    unknown = []
    for group in stud_list:
        f = []
        for student in group:
            if student in output.keys():
                f.append(student + ' ' + output[student])
                del output[student]
            else:
                f.append(student + ' ' + '0')
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
                if len(st) == 3 and hw_num in PROBNIK:
                    print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])) + 'не сдан')
                elif len(st) == 3:
                    print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])), st[2])
                else:
                    print(st[0] + ' ' * (20 - len(st[0])) + st[1] + ' ' * (20 - len(st[1])), end='')
                    del st[0:2]
                    summa = 0
                    soch = 0
                    for x in st:
                        soch = len(x)
                        if x != '?':
                            summa += int(x)
                        print(x, end=' ')
                    if soch == 2: soch = 0
                    print(' ' * soch + str(summa))

            print('------------------------------------------------------------------------------------------------------------')
            a = input('Для вывода удобного столбика для копирования нажмите 0 и enter, для продолжения работы - просто enter: ')
            if a == '0':
                for student in final[i]:
                    st = student.split()[2:]
                    if len(st) == 1 and hw_num in PROBNIK:
                        print('не сдан')
                    else:
                        summa = 0
                        for x in st:
                            if x != '?':
                                summa += int(x)
                            print(x, end=' ')
                        if hw_num in PROBNIK: print(str(summa))
                        else: print()
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
            soch = 0
            for x in st:
                soch = len(x)
                if x != '?':
                    summa += int(x)
                print(x, end=' ')
            if soch == 2: soch = 0
            if hw_num in PROBNIK: print(' ' * soch + str(summa))
            else: print()
            
        print('------------------------------------------------------------------------------------------------------------')

    print('------------------------------------------------------------------------------------------------------------')

    a = input('Нажмите Enter для завершения работы программы \nВведите любой символ и нажмите Enter для просмотра другой домашки: ')
    if a:
        main()
    return 0


if __name__ == '__main__':
    main()
