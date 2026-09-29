# Публикация именно этой версии СтудЕды на Render

Эта папка специально называется:

`student_food_web_render_ready`

Поэтому если в Render у вас уже стоит:

`Root Directory = student_food_web_render_ready`

менять Root Directory не нужно.

## Как обновить GitHub

1. Откройте репозиторий `stud-fuell`.
2. Удалите старую папку `student_food_web_render_ready`, если она там есть.
3. Загрузите НОВУЮ папку `student_food_web_render_ready` из этого архива целиком.
4. Сделайте Commit changes.

Внутри папки должны быть видны:
- app.py
- student_food.db
- README.md
- render.yaml
- и остальные файлы проекта.

## Настройки Render

- Language / Runtime: Python
- Root Directory: `student_food_web_render_ready`
- Build Command: `echo "No build required"`
- Start Command: `python app.py`

После загрузки новой версии:
Manual Deploy -> Deploy latest commit

## Важно

На бесплатном Render SQLite хранится в файловой системе сервиса.
После некоторых перезапусков или новых деплоев сохранённые изменения могут сброситься.
Для учебной демонстрации это подходит, но для постоянных пользовательских данных
в дальнейшем лучше использовать PostgreSQL или persistent disk.
