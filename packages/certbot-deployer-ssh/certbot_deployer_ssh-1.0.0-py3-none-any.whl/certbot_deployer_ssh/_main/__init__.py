"""
main
"""

import sys

from certbot_deployer import main as framework_main
from ..certbot_deployer_ssh import SshDeployer


def main(
    argv: list = sys.argv[1:],
) -> None:
    """
    main
    """
    new_argv = [SshDeployer.subcommand] + argv
    framework_main(deployers=[SshDeployer], argv=new_argv)
