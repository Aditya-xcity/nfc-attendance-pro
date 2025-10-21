# database/__init__.py
from .manager import ExcelDatabaseManager

# Global database instance
db = ExcelDatabaseManager()
