import sqlalchemy
from django.test.runner import DiscoverRunner
from testcontainers.postgres import PostgresContainer


class PlatypusTestRunner(DiscoverRunner):

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        with PostgresContainer('postgres:12.3') as container:
            engine = sqlalchemy.create_engine(container.get_connection_url())
            version, = engine.execute("select version()").fetchone()
            print(version)

            super().run_tests(test_labels, extra_tests=None, **kwargs)
