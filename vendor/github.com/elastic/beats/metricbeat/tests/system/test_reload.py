import re
import sys
import unittest
import metricbeat
import os
import time


# Further tests:
# * Mix full config modules with reloading modules
# * Load empty file
# * Add remove module
# * enabled / disable module
# * multiple files
# * Test empty file

class Test(metricbeat.BaseTest):

    @unittest.skipUnless(re.match("(?i)win|linux|darwin|freebsd|openbsd", sys.platform), "os")
    def test_reload(self):
        """
        Test basic reload
        """
        self.render_config_template(
            reload=True,
            reload_path=self.working_dir + "/configs/*.yml",
        )
        proc = self.start_beat()

        os.mkdir(self.working_dir + "/configs/")

        systemConfig = """
- module: system
  metricsets: ["cpu"]
  period: 1s
"""

        with open(self.working_dir + "/configs/system.yml", 'w') as f:
            f.write(systemConfig)

        self.wait_until(lambda: self.output_lines() > 0)
        proc.check_kill_and_wait()

    @unittest.skipUnless(re.match("(?i)win|linux|darwin|freebsd|openbsd", sys.platform), "os")
    def test_start_stop(self):
        """
        Test if module is properly started and stoppped
        """
        self.render_config_template(
            reload=True,
            reload_path=self.working_dir + "/configs/*.yml",
        )
        os.mkdir(self.working_dir + "/configs/")

        config_path = self.working_dir + "/configs/system.yml"
        proc = self.start_beat()

        systemConfig = """
- module: system
  metricsets: ["cpu"]
  period: 1s
"""

        with open(config_path, 'w') as f:
            f.write(systemConfig)

        # Wait until offset for new line is updated
        self.wait_until(
            lambda: self.log_contains("Starting 1 modules"),
            max_timeout=10)

        self.wait_until(lambda: self.output_lines() > 0)

        # Remove config again
        os.remove(config_path)

        # Wait until offset for new line is updated
        self.wait_until(
            lambda: self.log_contains("Module stopped:"),
            max_timeout=10)

        lines = self.output_lines()

        time.sleep(1)

        # Make sure no new lines were added since stopping
        assert lines == self.output_lines()

        proc.check_kill_and_wait()
