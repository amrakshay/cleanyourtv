"""tools/disable.sh must keep the packages that drive projector hardware.

Keystone correction, autofocus, the ToF or gyro sensor behind "auto keystone" and lamp, fan or lens
motor control are ordinary-looking vendor packages. A TV list has no reason to think about them, and
the projectors already in examples/ carry them as DO-NOT-DISABLE comments, which only helps someone
who read that list first. Disable one and the picture is crooked or soft with nothing in the menus
to put it right.

Run from the repository root: python3 -m unittest discover -s tests -v
"""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
# One of each shape the guard has to catch: a long keyword anywhere in the name, and a short word
# that only counts as a whole dot-separated segment.
KEYSTONE = "com.xgimi.autokst"
TOF = "com.xgimi.tof"
# Real package names that contain "fan" and "lens" and have nothing to do with a projector. The
# guard must leave these alone, or it starts costing TV owners entries in their lists.
FANCODE = "com.fancode.tv"
LENS = "com.google.android.apps.lens"


class ProjectorGuardTest(unittest.TestCase):
    def run_disable(self, listed, extra_env=None):
        """Run the real disable.sh against a fake tv.py client and return (batch, stderr).

        The fake answers the other guards the way a working TV would, so only this one is in play.
        """
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            tools = repo / "tools"
            tools.mkdir(parents=True)
            shutil.copy2(ROOT / "tools" / "disable.sh", tools / "disable.sh")
            client = tools / "venv" / "bin" / "python"
            client.parent.mkdir(parents=True)
            client.write_text(
                "#!/bin/sh\n"
                'case "$*" in\n'
                # No package on this TV drives an input, so the HDMI guard skips nothing.
                "  *TV_INPUT_HARDWARE*) true ;;\n"
                '  *resolve-activity*) echo "com.google.android.tvlauncher/.MainActivity" ;;\n'
                '  *query-activities*) echo "  com.google.android.tvlauncher/.MainActivity" ;;\n'
                '  *getprop*) echo 1 ;;\n'
                '  *) cat > "$CAPTURE" ;;\n'
                "esac\n")
            client.chmod(0o755)
            (repo / "debloat.txt").write_text("# A projector\n" + "".join(f"{n}\n" for n in listed))
            capture = Path(tmp) / "commands.txt"
            env = dict(os.environ, CAPTURE=str(capture), **(extra_env or {}))
            result = subprocess.run(["bash", str(tools / "disable.sh"), "debloat.txt"], cwd=repo,
                                    env=env, capture_output=True, text=True,
                                    stdin=subprocess.DEVNULL)
            self.assertEqual(result.returncode, 0, result.stderr)
            commands = capture.read_text().splitlines() if capture.exists() else []
            return commands, result.stderr

    def test_keystone_and_sensor_are_skipped(self):
        commands, stderr = self.run_disable(["com.example.store", KEYSTONE, TOF, "com.example.demo"])
        self.assertEqual(commands, ["pm disable-user --user 0 com.example.store",
                                    "pm disable-user --user 0 com.example.demo",
                                    "pm list packages -d"])
        self.assertIn(f"Skipping {KEYSTONE}", stderr)
        self.assertIn(f"Skipping {TOF}", stderr)
        self.assertIn("PROJECTOR_ALLOW=1", stderr)

    def test_the_message_says_it_may_be_a_false_positive_on_a_tv(self):
        # The test is the package name, which is a guess. Whoever is reading has to be told that.
        _, stderr = self.run_disable([KEYSTONE])
        self.assertIn("false positive", stderr)

    def test_short_words_only_match_a_whole_segment(self):
        # "fan" inside fancode is not projector hardware, and com.google.android.apps.lens ends in a
        # whole "lens" segment and still is not: a lens motor is named lensmotor or focus, so "lens"
        # is left out of the pattern. A guard that caught either would quietly drop lines from lists
        # that have been working for a year.
        commands, stderr = self.run_disable([FANCODE, LENS])
        self.assertEqual(commands, [f"pm disable-user --user 0 {FANCODE}",
                                    f"pm disable-user --user 0 {LENS}",
                                    "pm list packages -d"])
        self.assertNotIn("Skipping", stderr)

    def test_force(self):
        commands, stderr = self.run_disable([KEYSTONE], {"PROJECTOR_ALLOW": "1"})
        self.assertEqual(commands, [f"pm disable-user --user 0 {KEYSTONE}", "pm list packages -d"])
        self.assertNotIn("Skipping", stderr)

    def test_a_tv_list_is_untouched(self):
        commands, stderr = self.run_disable(["com.google.android.feedback", "com.android.bips",
                                             "com.google.android.partnersetup"])
        self.assertNotIn("Skipping", stderr)
        self.assertEqual(len(commands), 4)


class ExampleListsTest(unittest.TestCase):
    """The guard must not change what any list in examples/ already does.

    Every one of those was applied to a real set and lived with, so a name the guard catches there is
    a false positive by definition — either the pattern is too broad or that list has been disabling
    something it should not.
    """

    PATTERN = re.compile(r"(keyston|autokst|autofocus|trapezoid|correction|projection|gsensor|gyro|lensmotor)"
                         r"|(^|\.)(tof|lamp|fan|motor|focus|thermal|kst)(\.|$)", re.I)

    def test_no_listed_package_is_caught(self):
        caught = []
        for path in sorted((ROOT / "examples").glob("*/debloat.txt")):
            for raw in path.read_text(encoding="utf-8-sig").splitlines():
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                name = line.split("#", 1)[0].split()[0]
                if self.PATTERN.search(name):
                    caught.append(f"{path.parent.name}: {name}")
        self.assertEqual(caught, [], "the projector guard would now skip these listed packages")

    def test_the_pattern_matches_the_names_the_projector_lists_say_to_keep(self):
        # The guard earns its place only if it catches the ones already known to be dangerous.
        for name in ("com.xgimi.autokst", "com.xgimi.tof", "com.jmgo.autofocus",
                     "com.jmgo.autokeystone", "com.sdt.projectionservice",
                     "com.droidlogic.keystone",
                     # Found on a real unit: an Amlogic TV box firmware on a projector, whose
                     # keystone is "T correction" and says nothing about keystone in its name.
                     "com.softwinner.tcorrection"):
            with self.subTest(name=name):
                self.assertTrue(self.PATTERN.search(name))


if __name__ == "__main__":
    unittest.main()
