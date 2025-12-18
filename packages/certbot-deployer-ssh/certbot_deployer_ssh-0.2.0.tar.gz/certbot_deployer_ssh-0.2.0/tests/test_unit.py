"""Unit tests"""

import argparse

from unittest.mock import Mock, call

import pytest  # type:ignore


from certbot_deployer import CertificateBundle

# import certbot_deployer_ssh.certbot_deployer_ssh as ssh_deployer
from certbot_deployer_ssh.certbot_deployer_ssh import (
    DeploymentOperations,
    SshClient,
    SshDeployer,
)


@pytest.fixture(name="mock_ops")
def fixture_mock_ops() -> Mock:
    """Mock SshClient with spec"""
    return Mock(spec=DeploymentOperations)


@pytest.fixture(name="mock_client")
def fixture_mock_client() -> Mock:
    """Mock SshClient with spec"""
    return Mock(spec=SshClient)


class TestDeploymentOperations:
    """Tests for DeploymentOperations"""

    remote_dir = "/path/to/things"
    mode = 0o0755

    def test_ensure_remote_dir_creates_when_missing(self, mock_client: Mock) -> None:
        """test"""
        mock_client.exists.return_value = False
        ops: DeploymentOperations = DeploymentOperations(mock_client)

        ops.ensure_remote_dir(remote_dir=self.remote_dir, mode=self.mode)

        mock_client.exists.assert_called_once_with(self.remote_dir)
        mock_client.mkdir.assert_called_once_with(self.remote_dir)
        mock_client.chmod.assert_called_once_with(self.remote_dir, self.mode)

    def test_ensure_remote_dir_not_created_when_exists(self, mock_client: Mock) -> None:
        """test"""
        mock_client.exists.return_value = True
        ops: DeploymentOperations = DeploymentOperations(mock_client)

        ops.ensure_remote_dir(remote_dir=self.remote_dir, mode=self.mode)

        mock_client.exists.assert_called_once_with(self.remote_dir)
        mock_client.mkdir.assert_not_called()
        mock_client.chmod.assert_called_once_with(self.remote_dir, self.mode)

    def test_upload_bundle_all_files_in_order(
        self,
        mock_client: Mock,
        certbot_deployer_self_signed_certificate_bundle: CertificateBundle,
    ) -> None:
        """test"""
        ops: DeploymentOperations = DeploymentOperations(mock_client)

        ops.upload_bundle(
            certificate_bundle=certbot_deployer_self_signed_certificate_bundle,
            remote_dir=self.remote_dir,
        )

        expected_calls: list[tuple] = [
            call(component.path, self.remote_dir)
            for component in certbot_deployer_self_signed_certificate_bundle.components.values()
        ]
        assert mock_client.put_file.call_count == len(expected_calls)
        mock_client.put_file.assert_has_calls(expected_calls)

    def test_run_command(self, mock_client: Mock) -> None:
        """test"""
        ops: DeploymentOperations = DeploymentOperations(mock_client)
        cmd = "hack the gibson"

        ops.run_command(cmd)

        mock_client.run_command.assert_called_once_with(cmd)


def test_argparse_post() -> None:
    """
    Verify that the deployer subclass effectively requires all of its required
    args, both individually and collectively
    """
    required_args: dict[str, str] = {k: "somevalue" for k in SshDeployer.required_args}
    # If this runs with no exception, we're happy
    SshDeployer.argparse_post(args=argparse.Namespace(**required_args))

    args: dict[str, str]
    for arg in SshDeployer.required_args:
        args = dict(required_args)
        del args[arg]
        # Every call missing an arg should raise
        with pytest.raises(argparse.ArgumentTypeError):
            SshDeployer.argparse_post(args=argparse.Namespace(**args))
