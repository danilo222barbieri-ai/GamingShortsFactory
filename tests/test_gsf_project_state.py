import importlib.util
import unittest


class ProjectStateContractTests(unittest.TestCase):
    def test_project_state_module_exists(self):
        self.assertIsNotNone(
            importlib.util.find_spec("gsf_project_state"),
            "gsf_project_state must exist as the durable project-state boundary",
        )


if __name__ == "__main__":
    unittest.main()
