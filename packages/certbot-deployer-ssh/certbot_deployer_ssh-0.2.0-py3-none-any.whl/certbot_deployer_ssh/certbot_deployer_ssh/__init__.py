"""
SSH Deployer
"""

import argparse
import logging
import os
import textwrap

from typing import ClassVar, Dict, List, Optional, Protocol

import fabric  # type:ignore
import paramiko  # type:ignore

from certbot_deployer import Deployer, CertificateBundle, CertificateComponent
from certbot_deployer import CERT, INTERMEDIATES, KEY
from certbot_deployer import CERT_FILENAME, INTERMEDIATES_FILENAME, KEY_FILENAME
from certbot_deployer_ssh.meta import __description__, __version__


class SshClient:
    """
    Simple wrapper around Fabric
    """

    def __init__(self, host: str) -> None:
        logging.debug("Creating fabric connection (lazy)...")
        self.conn: fabric.Connection = fabric.Connection(host)
        self._sftp: Optional[paramiko.sftp_client.SFTPClient] = None

    @property
    def sftp(self) -> paramiko.sftp_client.SFTPClient:
        """Lazy-load SFTP client"""
        if self._sftp is None:
            logging.debug("Creating active connection for SFTP...")
            self._sftp = self.conn.sftp()
        return self._sftp

    def mkdir(self, path: str) -> None:
        """Make remote dir"""
        logging.debug("SFTP mkdir: `%s`", path)
        self.sftp.mkdir(path)

    def chmod(self, path: str, mode: int) -> None:
        """Change mode on a remote file"""
        logging.debug("SFTP chmod: `%s`, `%s`", path, oct(mode))
        self.sftp.chmod(path, mode)

    def exists(self, path: str) -> bool:
        """Check whether remote file exists"""
        logging.debug("SFTP check if remote directory `%s` exists...", path)
        try:
            self.sftp.listdir(path)
            logging.debug("SFTP remote directory `%s` exists.", path)
            return True
        except FileNotFoundError:
            logging.debug("SFTP remote directory `%s` does not exist.", path)
            return False

    def put_file(self, local: str, remote: str) -> None:
        """Upload file"""
        logging.debug("SFTP put file `%s` to `%s`...", local, remote)
        self.conn.put(local, remote)

    def run_command(self, cmd: str) -> None:
        """Run command on remote"""
        logging.debug("SFTP run command: `%s`", cmd)
        self.conn.run(cmd)


class DeploymentOperations:
    """
    High-level certificate deployment operations

    Delegates primitives to SshClient
    """

    def __init__(self, client: SshClient):
        self.client: SshClient = client

    def ensure_remote_dir(self, *, remote_dir: str, mode: int) -> None:
        """
        Ensure remote path exists
        """
        logging.debug("Ensuring remote directory `%s` exists...", remote_dir)
        if not self.client.exists(remote_dir):
            self.client.mkdir(remote_dir)
        self.client.chmod(remote_dir, mode)

    def upload_bundle(
        self, *, certificate_bundle: CertificateBundle, remote_dir: str
    ) -> None:
        """
        Upload bundle file by file
        """
        logging.debug("Uploading each certificate component...")
        for component in certificate_bundle.keys():
            self.client.put_file(certificate_bundle[component].path, remote_dir)

    def run_command(self, cmd: str) -> None:
        """Run commands"""
        self.client.run_command(cmd)


class SshDeployer(Deployer):
    """
    SSH deployer
    """

    subcommand: ClassVar[str] = "ssh"
    version: ClassVar[str] = __version__
    required_args: List[str] = ["host"]

    @staticmethod
    def register_args(*, parser: argparse.ArgumentParser) -> None:
        """
        Register command-line arguments
        """
        parser.description = __description__
        parser.formatter_class = argparse.RawDescriptionHelpFormatter
        parser.description = f"""BIG-IP subcommand
        {__description__}
        """
        parser.epilog = textwrap.dedent(
            """
            This tool expects to run as a Certbot deploy hook, and for the
            environment variable `RENEWED_LINEAGE` to point to the live
            certificate directory just updated/created by Certbot.

            Any existing certificate bundle under the same Common Name on the
            remote will be overwritten.

            # Credentials

            SSH credentials should be determined by the user's SSH config, e.g.:

                # /home/user/.ssh/config
                Host host.domain.tld
                    user deploy_user
                    IdentityFile /path/to/key

            See the Fabric library's documentation on SSH configuration for more:

                https://docs.fabfile.org/en/latest/concepts/configuration.html

            # Usage Examples:

            ## Deposit the certificate bundle directory into a remote path on a host

            %(prog)s --host host.domain.tld --destination-path=/path/to/wherever

            ## Upload the certificate bundle directory
                and run arbitrary commands before and after

            %(prog)s --pre-cmd "touch /some/file" --host host.domain.tld \\
                --post-cmd "chown user:grp /path/to/file"

            """
        )

        parser.add_argument(
            "--host",
            "-H",
            help=("SSH host to target"),
            type=str,
        )

        parser.add_argument(
            "--remote-dir",
            "-d",
            default="",
            help=(
                "Remote destination path in which to drop the certificate "
                "bundle directory. This tool will not attempt to create the "
                "path if it does not exist. If not provided, it will be up to "
                "the server - that usually ends up being the user's home "
                "directory."
            ),
            type=str,
        )

        parser.add_argument(
            "--pre-cmd",
            action="append",
            default=[],
            dest="pre_cmds",
            help=(
                "A command to run before uploading the certificate bundle. Can be "
                "passed multiple times."
            ),
            metavar="PRE_CMD",
            type=str,
        )

        parser.add_argument(
            "--post-cmd",
            action="append",
            default=[],
            dest="post_cmds",
            help=(
                "A command to run after uploading the certificate bundle. Can be "
                "passed multiple times."
            ),
            metavar="POST_CMD",
            type=str,
        )

        parser.add_argument(
            "--mode",
            "-m",
            default=0o700,
            help=(
                "Mode to apply to the remote certificate bundle directory on "
                "upload. Defaults to `0700`."
            ),
            type=lambda i: int(i, 8),
        )

    @staticmethod
    def argparse_post(*, args: argparse.Namespace) -> None:
        """
        Verify required args present
        """
        for arg in SshDeployer.required_args:
            if arg not in args:
                raise argparse.ArgumentTypeError(
                    f"Argument `{arg}` is required either in the configuration file "
                    "or on the command-line"
                )

    @staticmethod
    def entrypoint(
        *,
        args: argparse.Namespace,
        certificate_bundle: CertificateBundle,
        client: Optional[SshClient] = None,
        ops: Optional[DeploymentOperations] = None,
    ) -> None:
        """
        Execute the deployment process.

        1. Determine remote dir if None
        1. Run pre_cmds
        1. Upload cert bundle
        1. Run post_cmds
        """
        logging.debug("Args passed to deployer entrypoint: `%s`", args)
        if client is None:
            client = SshClient(args.host)
        if ops is None:
            ops = DeploymentOperations(client)
        for cmd in args.pre_cmds:
            ops.run_command(cmd)
        remote_dir: str = os.path.join(
            args.remote_dir,
            certificate_bundle.common_name,
        )
        logging.info("Using remote diretory `%s`...", remote_dir)
        ops.ensure_remote_dir(remote_dir=remote_dir, mode=args.mode)
        ops.upload_bundle(
            certificate_bundle=certificate_bundle,
            remote_dir=remote_dir,
        )
        for cmd in args.post_cmds:
            ops.run_command(cmd)
