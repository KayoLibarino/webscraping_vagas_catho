from collections import Counter
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
from matplotlib import pyplot as plt

URL = 'https://www.catho.com.br/vagas/python/?q=Python'
KEYWORD = 'python'

control_characters = re.compile(r'[\n\r\t]')

jobs = []
salary_list = []


def search_result(parameter):
    response = requests.get(URL + parameter)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    return soup.find('section', attrs={'id': 'search-result'})


if search_result('') is not None:
    informations = search_result('').find_all('li')

    total_jobs = int(search_result('').find(
        'p').text.split()[-1].replace('.', ''))

    pages = total_jobs // len(informations)

    if total_jobs % len(informations) != 0:
        pages += 1

    # Percorrendo todas as páginas
    for page in range(pages):
        informations = search_result('&page=' + str(page + 1)).find_all('li')

        # Percorrendo todas as vagas de uma página
        for information in informations:
            title = information.find('h2').text
            company = information.find('p').contents[0].text

            description = information.find(
                'span', attrs={'class': 'job-description'}).text
            description = re.sub(
                ' {2,}', ' ', control_characters.sub(' ', description)).strip()

            info_job = information.find('p').find_next_sibling('div')

            info_salary = info_job.find('div').text

            if info_salary not in ('A Combinar', ''):
                for i in ['De ', 'Até ', 'Acima de ', 'R$ ', ',00', '.']:
                    info_salary = info_salary.replace(i, '')
                info_salary = [int(s) for s in info_salary.split(' a ')]
                salary = sum(info_salary) // len(info_salary)
            else:
                salary = None

            total_cities = info_job.find('strong').text.split()[0]
            cities = [city.text for city in info_job.find_all(
                'button') if 'cidades' not in city.text]
            date = info_job.find('time').contents[0].text.split()[-1]

            if KEYWORD in title.casefold():
                jobs.append([title, company, salary, total_cities,
                            cities, date, description])
                if salary is not None:
                    salary_list.append(salary)

    data = pd.DataFrame(jobs, columns=['title', 'company', 'salary',
                                       'total_cities', 'cities', 'date', 'description'])

    data.to_csv('./data/jobs.csv', index=False)

    print(f'{len(data)} Vagas encontradas com sucesso!')

    salary_list = ['R$' + str(s) for s in sorted(salary_list)]

    keys = list(Counter(salary_list).keys())
    values = list(Counter(salary_list).values())

    # Plotando o gráfico
    plt.style.use('ggplot')
    plt.barh(keys, values)
    plt.title('Vagas Python - Catho')
    plt.xlabel('Quantidade de vagas')
    plt.ylabel('Média salarial')
    plt.show()
else:
    print('Nenhuma vaga encontrada.')
