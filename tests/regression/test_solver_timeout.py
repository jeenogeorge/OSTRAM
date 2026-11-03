"""Hard wall-clock solver timeout (solver_timeout_hours)."""

from __future__ import annotations

import subprocess
import sys
import time
import unittest
from unittest import mock

from ostram.pipeline.execution import orchestrator as b2


class SolverTimeoutSecondsTests(unittest.TestCase):
    def test_hours_convert_to_seconds(self) -> None:
        self.assertEqual(b2.solver_timeout_seconds({"solver_timeout_hours": 4}), 14400.0)
        self.assertEqual(b2.solver_timeout_seconds({"solver_timeout_hours": "0.5"}), 1800.0)

    def test_missing_blank_or_zero_means_no_limit(self) -> None:
        for params in ({}, {"solver_timeout_hours": None}, {"solver_timeout_hours": ""},
                       {"solver_timeout_hours": 0}, {"solver_timeout_hours": -1}):
            self.assertIsNone(b2.solver_timeout_seconds(params))

    def test_non_number_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            b2.solver_timeout_seconds({"solver_timeout_hours": "four"})


class InvokeSolverTimeoutTests(unittest.TestCase):
    def test_stuck_solver_is_killed_and_raises(self) -> None:
        stuck = [sys.executable, "-c", "import time; time.sleep(60)"]
        with mock.patch.object(b2, "resolve_paths") as paths:
            paths.return_value.stage_workspace.return_value = "."
            started = time.monotonic()
            with self.assertRaises(b2.SolverTimeoutError):
                b2.invoke_solver_command(stuck, subprocess.run, timeout_s=1)
        self.assertLess(time.monotonic() - started, 20)

    def test_cbc_seconds_is_capped_by_timeout(self) -> None:
        deps = mock.Mock()
        deps.path_exists.return_value = False
        paths = mock.Mock(output_file="out")
        params = {"iteration_time": 20000, "solver_timeout_hours": 1}
        command = b2.SolverAdapter(deps).prepare_command("cbc", params, paths)
        self.assertEqual(command[command.index("-seconds") + 1], "3600")


if __name__ == "__main__":
    unittest.main()
