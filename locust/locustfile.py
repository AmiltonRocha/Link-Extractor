"""
Locustfile - Trabalho 4
Testes de desempenho no Link Extractor (Python e Ruby)

Cada usuário virtual faz 10 invocações com URLs diferentes.

O host é definido pelo --host:
  Python: http://api-python:5000
  Ruby:   http://api-ruby:4567
"""
from locust import HttpUser, task, between

# 10 URLs diferentes — sites testados manualmente no Link Extractor
URLS_TESTE = [
    "https://www.opovo.com.br/",                     # 169 links
    "https://www.folha.uol.com.br/",                 # 772 links
    "https://www.gov.br/pt-br",                      # 261 links
    "https://www.cnnbrasil.com.br/",                 # 437 links
    "https://abc.com/",                              # 302 links
    "https://open.spotify.com/intl-pt",              # 92 links
    "https://www.claro.com.br/",                     # 264 links
    "https://github.com/",                           # 146 links
    "https://diariodonordeste.verdesmares.com.br/",  # 139 links
    "https://www.uol.com.br/",                       # 452 links
]


class LinkExtractorUser(HttpUser):
    # Espera entre 0.5 e 1.5 segundos entre cada sequência de 10 URLs
    wait_time = between(0.5, 1.5)

    @task
    def extrair_links(self):
        for url in URLS_TESTE:
            self.client.get(
                f"/api/{url}",
                name="/api/<url>"
            )
