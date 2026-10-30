#!/usr/bin/env bash
# ============================================================
# Trabalho 4 - Executa a matriz de testes de desempenho
#   versoes (python, ruby) x cache (com, sem) x usuarios (10 50 100 200)
# CSVs sao gravados em locust/resultados/
#
# Variaveis (opcionais):
#   USUARIOS="10 50 100 200"   niveis de usuarios
#   RUN_TIME=30s                duracao de cada teste
#   SPAWN_RATE=10               velocidade de subida dos usuarios
#   PAUSA=10                    segundos de descanso entre testes
# ============================================================
set -e
cd "$(dirname "$0")"

export MSYS_NO_PATHCONV=1

USUARIOS=(${USUARIOS:-10 50 100 200})
RUN_TIME=${RUN_TIME:-30s}
SPAWN_RATE=${SPAWN_RATE:-10}
PAUSA=${PAUSA:-10}

mkdir -p locust/resultados

# Funcao para limpar cache Redis
limpar_cache() {
  docker compose exec -T redis redis-cli FLUSHALL
  echo "Cache Redis limpo"
}

# Funcao para rodar um teste
rodar_teste() {
  local versao=$1
  local modo_cache=$2
  local usuarios=$3
  local host=$4
  local nome="t${versao}_${modo_cache}_u${usuarios}"

  echo "---- ${versao} | cache=${modo_cache} | usuarios=${usuarios} ----"
  sleep "${PAUSA}"

  docker compose exec -T locust locust \
    -f /locust/locustfile.py --host="${host}" \
    --headless -u "${usuarios}" -r "${SPAWN_RATE}" --run-time "${RUN_TIME}" \
    --csv "/tmp/${nome}" --only-summary || true

  docker compose exec -T locust sh -c "cp /tmp/${nome}_*.csv /locust/resultados/ && rm -f /tmp/${nome}_*.csv"

  echo "  CSVs salvos em locust/resultados/${nome}_*.csv"
}

echo "=========================================="
echo "  Trabalho 4 - Testes de Desempenho"
echo "=========================================="

# Sobe o ambiente
echo "== Subindo ambiente =="
docker compose up -d --build
sleep 15

# ============================================
# TESTE 1: Python COM cache
# ============================================
echo ""
echo "=========================================="
echo "  TESTE 1: Python COM cache"
echo "=========================================="
limpar_cache
for usr in "${USUARIOS[@]}"; do
  # Primeiro request preenche o cache
  rodar_teste "python" "com_cache" "${usr}" "http://api-python:5000"
done

# ============================================
# TESTE 2: Python SEM cache (cache limpo antes de cada teste)
# ============================================
echo ""
echo "=========================================="
echo "  TESTE 2: Python SEM cache"
echo "=========================================="
for usr in "${USUARIOS[@]}"; do
  limpar_cache
  rodar_teste "python" "sem_cache" "${usr}" "http://api-python:5000"
done

# ============================================
# TESTE 3: Ruby COM cache
# ============================================
echo ""
echo "=========================================="
echo "  TESTE 3: Ruby COM cache"
echo "=========================================="
limpar_cache
for usr in "${USUARIOS[@]}"; do
  rodar_teste "ruby" "com_cache" "${usr}" "http://api-ruby:4567"
done

# ============================================
# TESTE 4: Ruby SEM cache (cache limpo antes de cada teste)
# ============================================
echo ""
echo "=========================================="
echo "  TESTE 4: Ruby SEM cache"
echo "=========================================="
for usr in "${USUARIOS[@]}"; do
  limpar_cache
  rodar_teste "ruby" "sem_cache" "${usr}" "http://api-ruby:4567"
done

echo ""
echo "=========================================="
echo "  Todos os testes concluidos!"
echo "=========================================="
echo ""
echo "Proximos passos:"
echo "  python3 gerar_graficos.py"
