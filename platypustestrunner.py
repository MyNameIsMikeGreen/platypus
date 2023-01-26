from django.test.runner import DiscoverRunner


class PlatypusTestRunner(DiscoverRunner):

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        super().run_tests(test_labels, extra_tests=None, **kwargs)
