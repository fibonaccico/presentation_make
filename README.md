# presentation_make

## О проекте
`presentation_make` — асинхронный движок, который генерирует структурированные презентации: текст слайдов создаётся через выбранную LLM (GigaChat или YandexGPT), изображения — через Kandinsky 3.x, а итоговый файл собирается поверх PowerPoint-шаблонов из каталога `make_presentation/templates/`. Репозиторий подходит как для запуска готового сценария (`main.py`), так и для использования пакета в сторонних сервисах.

## Возможности
- генерация тем, заголовков, подзаголовков и буллетов по произвольному контексту или теме;
- автоматическое создание иллюстраций с сохранением PNG в отдельную папку;
- набор готовых шаблонов (`classic`, `flow`, `focus`, `kfu`, `style`, `black_study`, `minima`, `2`), которые можно расширять своими макетами в `templates/template_config.py`;
- сохранение презентации в `pptx` (по умолчанию) или `pdf` через `Presentation.save(..., format="pdf")`;
- настройка длины текста, числа слайдов и опциональных вступительных/финальных экранов.

## Структура проекта
- `main.py` — пример запуска: получает контекст, вызывает `Presentation`, сохраняет результат.
- `make_presentation/` — пакет с адаптерами (`text.py`, `image.py`), шаблонизатором (`generator_models/pptx/`), фабриками API и DTO.
- `make_presentation/templates/` — PPTX-шаблоны, шрифты и foreground-изображения.
- `data/presentation/` — целевой путь для результатов (`make_presentation.config.path_to_file`). По умолчанию он создаётся **на уровень выше** папки с репозиторием, т.е. `<родитель вашего рабочего каталога>/data/presentation`. Создайте каталог вручную или измените `path_to_file` в `make_presentation/config.py`.

## Требования
- Python 3.11–3.12;
- Poetry 1.6+ (рекомендуется) или любой virtualenv;
- доступ к API GigaChat, YandexGPT и Kandinsky.

## Установка
```powershell
# Клонируем репозиторий
git clone https://github.com/<org>/presentation_make.git
cd presentation_make

# Вариант с Poetry
poetry install

# Альтернатива на чистом venv
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements_pr.txt
```
Запустите `pre-commit install`, если хотите повторять проверки из `.pre-commit-config.yaml`.

## Настройка окружения
Создайте файл `.env` в корне проекта:
```
GIGACHAT_API_KEY=...
YANDEX_API_KEY=...
YANDEX_FOLDER_ID=...
KANDINSKY_API_KEY=...
KANDINSKY_SECRET_KEY=...
```
По умолчанию `TEXT_API = "GIGACHAT"` и `IMAGE_API = "KANDINSKY"`; переключите значения в `make_presentation/config.py`, если хотите использовать YandexGPT для текста. Там же можно настроить `DEFAULT_TEMPERATURE`, `MAX_NUMBER_OF_SLIDES_IN_TEMPLATES` и другие лимиты.

## Подготовка директорий
1. Создайте каталог для результатов: `mkdir ..\data\presentation` (Windows) или `mkdir -p ../data/presentation` (Linux/macOS) относительно папки проекта.
2. При необходимости скорректируйте `save_path_for_images` в `main.py` — сюда будут складываться PNG, возвращаемые Kandinsky.

## Запуск готового сценария
```powershell
poetry run python main.py
```
Перед запуском отредактируйте блок `context` и аргументы конструктора `Presentation` в `main.py`:
- `text_generation_model`: `"FROMTEXT"`, `"ONESTEP"` или `"TWOSTEP"` (см. `TextGenModuleEnum`).
- `template`: название папки из `make_presentation/templates/templates/`.
- `number_of_slides`: передайте `int`, чтобы зафиксировать длину презентации, или `None`, чтобы модель определила её сама.
Готовый `PresentationDTO` сериализуется вызовом `Presentation.save(..., save_path=path_to_file, format="pptx"|"pdf")`; функция вернёт абсолютный путь к файлу.

## Использование как библиотеки
```python
import asyncio
from make_presentation import Presentation
from make_presentation.config import path_to_file

async def build_presentation():
    generator = Presentation(text_generation_model="FROMTEXT", template="focus")
    dto = await generator.make_presentation(
        context="Краткое описание продукта",
        number_of_slides=8,
        save_path_for_images=path_to_file + "/images",
        image_style="ANIME"  # любой стиль, поддерживаемый Kandinsky
    )
    output = Presentation.save(data=dto, save_path=path_to_file, format="pptx")
    print(f"Файл сохранён: {output}")

asyncio.run(build_presentation())
```
Такой подход уместно использовать в FastAPI/cli-приложениях: адаптеры (`TextAdapter`, `ImagesAdapter`) уже инкапсулируют работу с внешними API и семафорами.

## Проверки и тесты
В репозитории пока нет тестов, но инфраструктура готова:
- `poetry run pre-commit run --all-files` — приводит импорты к стилю isort и запускает линтеры, указанные в `.pre-commit-config.yaml`.
- `poetry run pytest` — рекомендуемый способ прогонять будущие тесты (создавайте их в каталоге `tests/`, зеркаля структуру пакета).

## Частые проблемы
- **Нет директории для результатов.** Проверьте значение `path_to_file` и создайте путь вручную.
- **Отсутствуют зависимости (`ModuleNotFoundError`).** Убедитесь, что активирован Poetry- или venv-окружение с установленными пакетами.
- **Пустые ответы от API.** Удостоверьтесь, что токены в `.env` валидны и у аккаунта есть квоты.

