from functools import lru_cache
from pathlib import Path
from typing import Literal

import environ

from leaguemanager.lib.toolbox import module_to_os_path

MODULE_NAME = "leaguemanager"
HOST_APP_DIR = module_to_os_path(MODULE_NAME)


def set_to_cwd_if_none(value: str) -> Path:
    """Set the user app directory."""
    if not value:
        return Path.cwd()
    try:
        return Path(value).resolve()
    except ValueError as e:
        raise ValueError(f"Invalid path for app_dir: {value}") from e


# As of environ-config 21.1.0, prefix is supposed to default to None, but it seems to not.
@environ.config(prefix="")
class HostApplication:
    app_name: str = MODULE_NAME
    app_dir: Path = environ.var(default=HOST_APP_DIR)
    root_dir: Path = environ.var(default=HOST_APP_DIR.parent.parent.resolve())
    db_services_dir: Path = environ.var(default=HOST_APP_DIR / "services")
    template_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "template_loader")
    schedule_loader_dir: Path = environ.var(default=HOST_APP_DIR / "services" / "scheduling")
    synth_data_dir: Path = environ.var(default=HOST_APP_DIR / "data" / "synthetic_data")
    excel_template_dir: Path = environ.var(default=HOST_APP_DIR / "data" / "importer_templates" / "excel")

    @environ.config
    class UserApplication:
        """User application settings."""

        app_name: str = environ.var(default=None)
        app_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        root_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_services_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)
        db_config_dir: Path = environ.var(default=None, converter=set_to_cwd_if_none)

    @environ.config
    class SecurityConfig:
        """Security configuration settings."""

        def _str_to_list(value: str | list[str]) -> list[str]:
            if isinstance(value, str):
                return [value]
            return value

        crypt_schemes: str | list[str] = environ.var(default=["argon2"], converter=_str_to_list)

    @environ.config
    class DatabaseConfig:
        """
        Database settings configuration.
        """

        sync_url: str | None = environ.var(default=None)
        async_url: str | None = environ.var(default=None)

        commit_type: Literal["autocommit", "autocommit_include_redirects"] = environ.var(default=None)

        echo: bool = environ.bool_var(default=False)
        echo_pool: bool = environ.bool_var(default=False)
        pool_size: int = environ.var(default=5, converter=int)
        pool_max_overflow: int = environ.var(default=10, converter=int)
        pool_timeout: int = environ.var(default=30, converter=int)
        pool_recycle: int = environ.var(default=500, converter=int)
        pool_pre_ping: bool = environ.bool_var(default=False)

        sqlite_data_directory: Path = environ.var(default=Path.cwd() / "data_league_db", converter=Path)
        sqlite_db_name: str = environ.var(default="lm_data.db")

    @environ.config
    class AlembicConfig:
        """Configuration for Alembic migrations."""

        migration_path: Path = environ.var(default=None)
        config_file_path: Path = environ.var(default=None)
        template_path: Path = environ.var(default=HOST_APP_DIR / "db/alembic_templates")

    @environ.config
    class RoleConfig:
        """Role configuration settings."""

        default_user: str = environ.var(default="user")
        athlete: str = environ.var(default="athlete")
        team_manager: str = environ.var(default="team_manager")
        official: str = environ.var(default="official")
        organization_admin: str = environ.var(default="admin")
        superuser: str = environ.var(default="superuser")

    @environ.config
    class EmailConfig:
        """Email configuration settings."""

        enabled: bool = environ.var(default=True)
        smtp_host: str = environ.var(default="localhost")
        smtp_port: int = environ.var(default=587)
        smtp_user: str = environ.var(default=None)
        smtp_password: str = environ.var(default=None)
        from_email: str = environ.var(default="noreply@example.com")
        from_name: str = environ.var(default="League Manager App")
        use_tls: bool = environ.var(default=True)
        use_ssl: bool = environ.var(default=False)
        timeout: int = environ.var(default=10)

    @environ.config
    class KeysConfig:
        """Keys configuration settings."""

        league_manager: str = environ.var(default="league_manager")
        svcs_registry: str = environ.var(default="lm_registry")
        svcs_container: str = environ.var(default="lm")
        db_sync_service: str = environ.var(default="db_sync_service")
        db_async_service: str = environ.var(default="db_async_service")
        session_scope: str = environ.var(default="_lm_sqlalchemy_db_session")

    user_app: UserApplication = environ.group(UserApplication)
    db: DatabaseConfig = environ.group(DatabaseConfig)
    alembic: AlembicConfig = environ.group(AlembicConfig)
    sec: SecurityConfig = environ.group(SecurityConfig)
    role: RoleConfig = environ.group(RoleConfig)
    email: EmailConfig = environ.group(EmailConfig)
    keys: KeysConfig = environ.group(KeysConfig)


@lru_cache(maxsize=1)
def get_settings() -> HostApplication:
    """Get the settings for the host application."""
    return environ.to_config(HostApplication)
