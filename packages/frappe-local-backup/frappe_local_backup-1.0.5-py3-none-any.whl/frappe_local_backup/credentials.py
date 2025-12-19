"""Secure credential management using keyring."""

import logging
from dataclasses import dataclass
from typing import Optional

import keyring
from keyring.errors import KeyringError

logger = logging.getLogger(__name__)

KEYRING_SERVICE = "frappe-local-backup"


@dataclass
class TeamCredentials:
    api_key: str
    api_secret: str


class CredentialManager:
    """Manage credentials securely using keyring."""

    def __init__(self, service_name: str = KEYRING_SERVICE):
        self.service_name = service_name
        logger.debug(
            "Using keyring backend: %s",
            keyring.get_keyring().__class__.__name__,
        )

    def _get_key_name(self, team_name: str, key_type: str) -> str:
        return f"{team_name}:{key_type}"

    def store_credentials(self, team_name: str, api_key: str, api_secret: str) -> None:
        try:
            keyring.set_password(
                self.service_name,
                self._get_key_name(team_name, "api_key"),
                api_key,
            )
            keyring.set_password(
                self.service_name,
                self._get_key_name(team_name, "api_secret"),
                api_secret,
            )
            logger.info("Stored credentials for team '%s'", team_name)

        except KeyringError as e:
            logger.error("Keyring backend failure: %s", e)
            raise RuntimeError(
                "Failed to store credentials securely.\n\n"
                "If you are running on a server, KDE, or CI environment, "
                "use the encrypted file backend:\n\n"
                "  export PYTHON_KEYRING_BACKEND=keyrings.alt.file.EncryptedKeyring\n"
            ) from e

    def get_credentials(self, team_name: str) -> Optional[TeamCredentials]:
        try:
            api_key = keyring.get_password(
                self.service_name,
                self._get_key_name(team_name, "api_key"),
            )
            api_secret = keyring.get_password(
                self.service_name,
                self._get_key_name(team_name, "api_secret"),
            )

            if api_key and api_secret:
                return TeamCredentials(api_key=api_key, api_secret=api_secret)
            return None

        except KeyringError as e:
            logger.error("Failed to retrieve credentials: %s", e)
            return None

    def delete_credentials(self, team_name: str) -> bool:
        try:
            keyring.delete_password(
                self.service_name,
                self._get_key_name(team_name, "api_key"),
            )
            keyring.delete_password(
                self.service_name,
                self._get_key_name(team_name, "api_secret"),
            )
            logger.info("Deleted credentials for team '%s'", team_name)
            return True

        except KeyringError as e:
            logger.warning("Failed to delete credentials: %s", e)
            return False

    def credentials_exist(self, team_name: str) -> bool:
        return self.get_credentials(team_name) is not None


_credential_manager: Optional[CredentialManager] = None


def get_credential_manager() -> CredentialManager:
    global _credential_manager
    if _credential_manager is None:
        _credential_manager = CredentialManager()
    return _credential_manager
