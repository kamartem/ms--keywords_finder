import concurrent.futures
import logging
import os
import sys
from collections import Counter
from io import BytesIO
from pyexcelerate import Workbook
import requests
import urllib3
from bs4 import BeautifulSoup
from django import forms
from django.conf import settings
from django.conf.urls import url
from django.http import HttpResponse
from django.shortcuts import render
from pyexcelerate import Workbook

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONNECTIONS = 100
TIMEOUT = 5
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

LOG = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_HOSTS = ['*']
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')]
}]
DEBUG = os.getenv('DEBUG', False)

settings.configure(DEBUG=DEBUG,
                   ROOT_URLCONF=sys.modules[__name__],
                   TEMPLATES=TEMPLATES,
                   ALLOWED_HOSTS=ALLOWED_HOSTS)


class ProcessForm(forms.Form):
    url_list = forms.CharField(
        label='Список URL', widget=forms.Textarea(attrs={'placeholder': 'domain.com\ndomain2.com'}))
    keyword_list = forms.CharField(
        label='Список ключевых слов', widget=forms.Textarea(attrs={'placeholder': 'слово 1\nслово 2'}))


def load_url(url):
    url = f'http://{url}' if not url.startswith('http') else url
    ans = requests.get(url, timeout=TIMEOUT, headers=headers, verify=False)
    return ans.content.decode('utf-8', 'ignore').lower()


def get_pages(domain, count=5):
    data = []

    try:
        ans = requests.get(f'http://{domain}', timeout=TIMEOUT, headers=headers, verify=False)
        ans.encoding = ans.apparent_encoding

        soup = BeautifulSoup(ans.content.decode('utf-8', 'ignore'), features="lxml")
        hrefs = [
            f'http://{domain}{link["href"] if link["href"].startswith("/") else "/" + link["href"]}' for link in
            soup.find_all("a", href=lambda x: x and not x.startswith('http') and ':' not in x and not x.startswith('#'))
        ]
        hrefs2 = [link["href"] for link in soup.find_all("a", href=lambda x: x and domain in x)]
        result = [f'http://{domain}', ] + hrefs + hrefs2
        c = Counter(result)
        data = list(set([domain[0] for domain in c.most_common(count)]))
    except Exception as e:
        LOG.error(e)

    return data


def index(request):
    if request.method == 'POST':
        form = ProcessForm(request.POST)
        if form.is_valid():
            domains = form.cleaned_data.get('url_list').lower().splitlines()
            keywords = form.cleaned_data.get('keyword_list').lower().splitlines()
            results = {}
            final_results = {}

            domains = [domain for domain in domains if domain]
            keywords = [keyword for keyword in keywords if keyword]
            with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
                future_to_domain = {executor.submit(get_pages, domain): domain for domain in domains}
                for future in concurrent.futures.as_completed(future_to_domain):
                    domain = future_to_domain[future]
                    for result in future.result():
                        results[result] = domain

            with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
                future_to_url = {executor.submit(load_url, url): url for url in results.keys()}
                for future in concurrent.futures.as_completed(future_to_url):
                    url = future_to_url[future]

                    try:
                        data = future.result()
                        domain = results[url]
                        kwords = final_results.setdefault(domain, [])
                        kwords += [kw for kw in keywords if kw in data and kw not in kwords]
                    except Exception as exc:
                        LOG.error(exc)

            result = [[k, ','.join(v)] for k, v in final_results.items()]
            stream = BytesIO()
            wb = Workbook()
            wb.new_sheet("sheet name", data=result)
            wb.save(stream)
            response = HttpResponse(stream.getvalue(), content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="search.xlsx"'
            return response
    else:
        form = ProcessForm()

    return render(request, 'index.html', {'form': form})


urlpatterns = [
    url(r'^$', index),
]

if __name__ == '__main__':
    if DEBUG:
        from django.core.management import execute_from_command_line

        execute_from_command_line(sys.argv)
    else:
        import netius.servers
        from django.core.wsgi import get_wsgi_application

        application = get_wsgi_application()
        server = netius.servers.WSGIServer(app=application)
        server.serve(port=8566)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
