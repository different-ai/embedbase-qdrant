from monorepo.tests.test_end_to_end import vector_databases
from qdrant_db import Qdrant

# override default vector databases with our integration
vector_databases.clear()
vector_databases.append(Qdrant())

# poetry run pytest test_integration.py
