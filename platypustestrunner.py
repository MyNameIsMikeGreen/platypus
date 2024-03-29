from django.test.runner import DiscoverRunner
import django.conf as conf


from testcontainers.postgres import PostgresContainer


class PlatypusTestRunner(DiscoverRunner):

    POSTGRESQL_PORT = 5432

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        with PostgresContainer('postgres:12.9') as container:
            conf.settings.DATABASES['default']['HOST'] = container.get_container_host_ip()
            conf.settings.DATABASES['default']['PORT'] = container.get_exposed_port(self.POSTGRESQL_PORT)
            conf.settings.DATABASES['default']['USER'] = "test"
            conf.settings.DATABASES['default']['PASSWORD'] = "test"
            super().run_tests(test_labels, extra_tests=None, **kwargs)
