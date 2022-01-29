import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    now = int(datetime.date.today().strftime('%Y'))
    return {
        'year': now
    }
