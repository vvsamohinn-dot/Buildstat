# BuildStat

Статический одностраничный рейтинг с ежедневным агентом и публикацией через GitHub Pages.

Проверка: `python -m unittest discover -s tests`, затем `python scripts/build.py`.

`OPENAI_API_KEY` необязателен. Для международного извлечения добавьте его только в GitHub: Settings → Secrets and variables → Actions. Никогда не добавляйте ключ в файлы репозитория.

Для Pages выберите в Settings → Pages источник **GitHub Actions**.
