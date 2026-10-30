"""
Locustfile - Trabalho 4
Testes de desempenho no Link Extractor

Cada usuário virtual faz 10 invocações com URLs diferentes.
"""
from locust import HttpUser, task, between

# 10 URLs diferentes (todas com links <a>)
URLS_TESTE = [
    "https://www.docker.com",
    "https://www.python.org",
    "https://www.ruby-lang.org",
    "https://flask.palletsprojects.com",
    "https://redis.io",
    "https://www.github.com",
    "https://www.nginx.com",
    "https://www.mysql.com",
    "https://www.php.net",
    "https://www.apache.org",
]


class LinkExtractorUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def extrair_links(self):
        for url in URLS_TESTE:
            self.client.get(
                f"/api/{url}",
                name="/api/<url>"
            )
