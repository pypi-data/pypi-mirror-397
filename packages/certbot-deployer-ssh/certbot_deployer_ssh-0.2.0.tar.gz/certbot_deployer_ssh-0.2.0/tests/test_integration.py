"""test"""

import argparse
import os

from unittest.mock import Mock, call
from typing import Optional, Type

import pytest  # type:ignore


from certbot_deployer import CertificateBundle, Deployer
import certbot_deployer_ssh._main as plugin_main

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


# pylint: disable-next=too-few-public-methods
class TestDeploymentIntegration:
    """test"""

    @pytest.mark.parametrize(
        "remote_dir",
        ["", "/some/remote/path"],
        ids=["(remote_dir not provided)", "(remote_dir provided)"],
    )
    @pytest.mark.parametrize(
        "pre_cmds",
        [["/one/command"], ["precmd1", "precmd2", "precmd3"]],
        ids=["(one pre-command)", "(multiple pre-commands)"],
    )
    @pytest.mark.parametrize(
        "post_cmds",
        [["/one/command"], ["postcmd1", "postcmd2", "postcmd3"]],
        ids=["(one post-command)", "(multiple post-commands)"],
    )
    # pylint: disable-next=too-many-positional-arguments,too-many-arguments
    def test_full_deployment_ops_calls_in_order(
        self,
        mock_client: Mock,
        mock_ops: Mock,
        certbot_deployer_self_signed_certificate_bundle: CertificateBundle,
        remote_dir: Optional[str],
        pre_cmds: list[str],
        post_cmds: list[str],
    ) -> None:
        """test"""
        args: argparse.Namespace = argparse.Namespace(
            host="anyhost.domain.tld",
            remote_dir=remote_dir,
            pre_cmds=pre_cmds,
            post_cmds=post_cmds,
            mode=0o0755,
        )
        SshDeployer.entrypoint(
            args=args,
            certificate_bundle=certbot_deployer_self_signed_certificate_bundle,
            client=mock_client,
            ops=mock_ops,
        )
        expected_remote_dir: str = os.path.join(
            args.remote_dir, certbot_deployer_self_signed_certificate_bundle.common_name
        )
        expected_calls: list[tuple] = []
        expected_calls.extend([call.run_command(cmd) for cmd in args.pre_cmds])
        expected_calls.extend(
            [call.ensure_remote_dir(remote_dir=expected_remote_dir, mode=args.mode)]
        )
        expected_calls.extend(
            [
                call.upload_bundle(
                    certificate_bundle=certbot_deployer_self_signed_certificate_bundle,
                    remote_dir=expected_remote_dir,
                )
            ]
        )
        expected_calls.extend([call.run_command(cmd) for cmd in args.post_cmds])
        assert mock_ops.method_calls == expected_calls


def test_main_delegation(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Verify that our `main()` hands control off to the framework when called
    directly by mocking the framework's `main()` and comparing the passed
    args/deployers
    """
    called_argv: list = []
    called_deployers: Optional[list[Type[Deployer]]]

    def fake_framework_main(
        argv: list, deployers: Optional[list[Type[Deployer]]] = None
    ) -> None:
        nonlocal called_argv
        nonlocal called_deployers
        called_argv = argv
        called_deployers = deployers

    argv: list[str] = ["-h"]
    expected_argv: list[str] = [SshDeployer.subcommand, "-h"]
    expected_deployers: Optional[list[Type[Deployer]]] = [SshDeployer]

    monkeypatch.setattr(
        plugin_main,
        "framework_main",
        fake_framework_main,
    )
    plugin_main.main(argv=argv)
    assert called_argv == expected_argv
    assert called_deployers == expected_deployers
