#!/usr/bin/env bash
set -e

# Default PostgreSQL parameters if not provided
export POSTGRES_USER=${POSTGRES_USER:-school}
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-123456}
export POSTGRES_DB=${POSTGRES_DB:-school}
export POSTGRES_HOST=${POSTGRES_HOST:-localhost}
export POSTGRES_PORT=${POSTGRES_PORT:-5050}
export TEACHER_PASSWORD=${TEACHER_PASSWORD:-123456}
export PORT=${PORT:-8000}
export HOST=${HOST:-0.0.0.0}

echo "=== Запуск платформи уроків та завдань ==="
echo "База даних: postgresql://${POSTGRES_USER}:***@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
echo "Адреса сервера: http://${HOST}:${PORT}"
echo "Пароль вчителя за замовчуванням: ${TEACHER_PASSWORD}"
echo "========================================="

python3 main.py
