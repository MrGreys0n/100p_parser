from bs4 import BeautifulSoup as bs
import requests
import fake_useragent

session = requests.Session()

url = "https://api.100points.ru/login"
user = fake_useragent.UserAgent().random

header = {'user-agent': user}
data = {
    'email': 'sergey2304s@mail.ru',
    'password': 'sergey2304s@mail.ru'
}

responce = session.post(url, data=data, headers=header)

hw_url = 'https://api.100points.ru/student_homework/index?status=passed'
hw_responce = session.get(hw_url, headers=header).text
hw_soup = bs(hw_responce, "html.parser")

links = hw_soup.find_all('a', class_='btn btn-xs bg-purple')
for i in range(len(links)):
    links[i] = links[i].get('href')

output = []

for link in links:
    link_responce = session.get(link, headers=header).text
    link_soup = bs(link_responce, "html.parser")
    temp = link_soup.find_all('input', class_='form-control')
    name = temp[2].get('value')

    temp = link_soup.find_all('div', class_='form-group col-md-3')
    temp = temp[4].text
    result = temp.split()[-1]
    output.append(name + '\t' + result)

for st in output:
    print(st)