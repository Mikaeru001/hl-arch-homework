from injector import Injector
from infra.db.config.database import DatabaseModule

# Инициализация инжектора с модулем базы данных
injector = Injector([DatabaseModule()])
