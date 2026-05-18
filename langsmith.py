# langsmith.py mock

class Client:
    def __init__(self, api_key=None, **kwargs):
        self.api_key = api_key

    def list_runs(self, project_name=None, limit=1, **kwargs):
        class MockRun:
            pass
        return [MockRun()]
