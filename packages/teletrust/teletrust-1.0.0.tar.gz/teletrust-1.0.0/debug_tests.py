import pytest
import sys

class Plugin:
    def pytest_runtest_logreport(self, report):
        if report.failed:
            print(f"FAILED: {report.nodeid}")
            print(str(report.longrepr))

if __name__ == "__main__":
    sys.exit(pytest.main(["-q", "--tb=short"], plugins=[Plugin()]))
