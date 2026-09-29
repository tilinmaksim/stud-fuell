# Публикация Student Fuel через Render

## Шаг 1. GitHub
1. Создайте аккаунт на GitHub.
2. Нажмите New repository.
3. Назовите репозиторий `student-fuel`.
4. Сделайте его Public.
5. Нажмите Create repository.
6. Выберите `uploading an existing file`.
7. Перетащите ВСЕ файлы и папки из этой распакованной папки.
8. Нажмите Commit changes.

Важно: загрузите содержимое проекта, а не ZIP одним файлом.

## Шаг 2. Render
1. Откройте Render.
2. Нажмите New -> Web Service.
3. Подключите GitHub.
4. Выберите репозиторий `student-fuel`.

## Шаг 3. Настройки
- Runtime: Python
- Build Command: оставить пустым
- Start Command: `python app.py`

Нажмите Create Web Service.

## Шаг 4. Ссылка
После запуска Render выдаст публичный адрес примерно:
`https://student-fuel.onrender.com`

Эту ссылку можно отправить преподавателю. Python на его устройстве не нужен.

## Важно
SQLite на обычном облачном сервисе может быть временной: после нового деплоя данные могут сброситься.
Для учебной демонстрации это допустимо. Для постоянных данных лучше подключить PostgreSQL или persistent disk.
