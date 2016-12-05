from amazonbeat import BaseTest

import os


class Test(BaseTest):

    def test_base(self):
        """
        Basic test with exiting Amazonbeat normally
        """
        self.render_config_template(
                path=os.path.abspath(self.working_dir) + "/log/*"
        )

        amazonbeat_proc = self.start_beat()
        self.wait_until( lambda: self.log_contains("amazonbeat is running"))
        exit_code = amazonbeat_proc.kill_and_wait()
        assert exit_code == 0
