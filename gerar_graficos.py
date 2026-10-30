#!/usr/bin/env python3
"""
Trabalho 4 - Gera gráficos dos testes de desempenho do Link Extractor

Uso:
  python3 gerar_graficos.py
  python3 gerar_graficos.py --pasta locust/resultados
"""
import argparse
import csv
import os
import re
import sys
from collections import defaultdict

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("ERRO: matplotlib nao instalado. Rode: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def parsear_nome_arquivo(nome):
    """
    Extrai versao, modo_cache e usuarios do nome do CSV.
    Formato: t{versao}_{modo_cache}_u{usuarios}_stats.csv
    Exemplo: tpython_com_cache_u10_stats.csv
    """
    m = re.match(r"t(python|ruby)_(com_cache|sem_cache)_u(\d+)_stats\.csv", nome)
    if m:
        return {
            "versao": m.group(1),
            "modo_cache": m.group(2),
            "usuarios": int(m.group(3)),
        }
    return None


def ler_stats(caminho):
    """Le um CSV de stats do Locust e retorna as metricas."""
    metricas = {}
    try:
        with open(caminho, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Linha do total (vazio no Name)
                if row.get("Name", "").strip() == "" or row.get("Name", "").strip() == "Aggregated":
                    metricas = {
                        "request_count": int(row.get("Request Count", 0)),
                        "failure_count": int(row.get("Failure Count", 0)),
                        "avg_ms": float(row.get("Average Response Time", 0)),
                        "min_ms": float(row.get("Min Response Time", 0)),
                        "max_ms": float(row.get("Max Response Time", 0)),
                        "p50_ms": float(row.get("50%", 0)),
                        "p95_ms": float(row.get("95%", 0)),
                        "rps": float(row.get("Requests/s", 0)),
                    }
                    break
    except Exception as e:
        print(f"  ERRO ao ler {caminho}: {e}", file=sys.stderr)
    return metricas


def carregar_dados(pasta):
    """Carrega todos os CSVs da pasta e organiza por versao e modo_cache."""
    dados = defaultdict(lambda: defaultdict(list))

    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith("_stats.csv"):
            continue
        info = parsear_nome_arquivo(nome)
        if not info:
            continue
        caminho = os.path.join(pasta, nome)
        metricas = ler_stats(caminho)
        if metricas:
            chave = (info["versao"], info["modo_cache"])
            dados[chave]["usuarios"].append(info["usuarios"])
            dados[chave]["metricas"].append(metricas)

    return dados


def gerar_graficos(pasta):
    """Gera os graficos de comparacao."""
    dados = carregar_dados(pasta)
    pasta_saida = os.path.join(pasta, "graficos")
    os.makedirs(pasta_saida, exist_ok=True)

    if not dados:
        print(f"Nenhum CSV encontrado em {pasta}", file=sys.stderr)
        return

    metricas_nomes = [
        ("avg_ms", "Tempo medio (ms)"),
        ("p50_ms", "Mediana - Percentil 50% (ms)"),
        ("p95_ms", "Percentil 95% (ms)"),
        ("rps", "Requisicoes por segundo (RPS)"),
        ("failure_count", "Total de falhas"),
    ]

    # Grafico 1: Comparacao Python vs Ruby (com cache)
    for modo_cache in ["com_cache", "sem_cache"]:
        fig, axes = plt.subplots(5, 1, figsize=(10, 15))
        fig.suptitle(
            f"Link Extractor - Comparacao Python vs Ruby ({modo_cache.replace('_', ' ')})",
            fontsize=14, fontweight="bold"
        )

        for idx, (campo, titulo) in enumerate(metricas_nomes):
            ax = axes[idx]
            for versao, cor in [("python", "blue"), ("ruby", "red")]:
                chave = (versao, modo_cache)
                if chave in dados:
                    usuarios = sorted(dados[chave]["usuarios"])
                    valores = [
                        m[campo] for u, m in zip(dados[chave]["usuarios"], dados[chave]["metricas"])
                        if u in usuarios
                    ]
                    ax.plot(usuarios, valores, "o-", label=versao, color=cor)

            ax.set_title(titulo)
            ax.set_xlabel("Usuarios simultaneos")
            ax.set_ylabel(titulo)
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        caminho = os.path.join(pasta_saida, f"comparacao_{modo_cache}.png")
        plt.savefig(caminho, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  grafico: {caminho}")

    # Grafico 2: Comparacao com cache vs sem cache (por versao)
    for versao in ["python", "ruby"]:
        fig, axes = plt.subplots(5, 1, figsize=(10, 15))
        fig.suptitle(
            f"Link Extractor - {versao.capitalize()} - Com vs Sem Cache",
            fontsize=14, fontweight="bold"
        )

        for idx, (campo, titulo) in enumerate(metricas_nomes):
            ax = axes[idx]
            for modo_cache, cor in [("com_cache", "green"), ("sem_cache", "orange")]:
                chave = (versao, modo_cache)
                if chave in dados:
                    usuarios = sorted(dados[chave]["usuarios"])
                    valores = [
                        m[campo] for u, m in zip(dados[chave]["usuarios"], dados[chave]["metricas"])
                        if u in usuarios
                    ]
                    ax.plot(usuarios, valores, "o-", label=modo_cache.replace("_", " "), color=cor)

            ax.set_title(titulo)
            ax.set_xlabel("Usuarios simultaneos")
            ax.set_ylabel(titulo)
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        caminho = os.path.join(pasta_saida, f"cache_{versao}.png")
        plt.savefig(caminho, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"  grafico: {caminho}")

    print(f"\nPronto! Graficos em: {pasta_saida}")


def main():
    ap = argparse.ArgumentParser(description="Gera graficos dos testes")
    ap.add_argument("--pasta", default="locust/resultados", help="Pasta com os CSVs")
    args = ap.parse_args()

    gerar_graficos(args.pasta)


if __name__ == "__main__":
    main()
