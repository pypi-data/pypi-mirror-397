import pytest

from src.montagu_deploy.config import MontaguConfig


def test_config_basic():
    cfg = MontaguConfig("config/basic")
    assert cfg.network == "montagu-network"
    assert cfg.volumes["db"] == "db_volume"
    assert cfg.volumes["emails"] == "emails"
    assert cfg.volumes["burden_estimates"] == "burden_estimate_files"
    assert cfg.volumes["guidance"] == "guidance_volume"
    assert cfg.volumes["templates"] == "template_volume"
    assert cfg.volumes["mq"] == "mq"
    assert cfg.container_prefix == "montagu"

    assert len(cfg.containers) == 10

    assert cfg.containers["api"] == "api"
    assert cfg.containers["db"] == "db"
    assert cfg.containers["admin"] == "admin"
    assert cfg.containers["contrib"] == "contrib"
    assert cfg.containers["proxy"] == "proxy"
    assert cfg.containers["metrics"] == "proxy-metrics"
    assert cfg.containers["mq"] == "mq"
    assert cfg.containers["flower"] == "flower"
    assert cfg.containers["task_queue"] == "task-queue"
    assert cfg.containers["fake_smtp"] == "fake-smtp"

    assert len(cfg.images) == 12

    assert str(cfg.images["db"]) == "ghcr.io/vimc/montagu-db:main"
    assert str(cfg.images["api"]) == "ghcr.io/vimc/montagu-api:main"
    assert str(cfg.images["admin"]) == "ghcr.io/vimc/montagu-admin-portal:main"
    assert str(cfg.images["api_admin"]) == "ghcr.io/vimc/montagu-cli:main"
    assert str(cfg.images["contrib"]) == "ghcr.io/vimc/montagu-contrib-portal:main"
    assert str(cfg.images["proxy"]) == "ghcr.io/vimc/montagu-proxy:main"
    assert str(cfg.images["mq"]) == "docker.io/redis:latest"
    assert str(cfg.images["flower"]) == "mher/flower:0.9.5"
    assert str(cfg.images["task_queue"]) == "ghcr.io/vimc/task-queue-worker:main"
    assert str(cfg.images["metrics"]) == "nginx/nginx-prometheus-exporter:1.3.0"
    assert str(cfg.images["db_migrate"]) == "ghcr.io/vimc/montagu-migrate:main"
    assert str(cfg.images["fake_smtp"]) == "reachfive/fake-smtp-server:latest"

    assert cfg.mq_port == 6379
    assert cfg.flower_port == 5555

    assert cfg.protect_data is False
    assert cfg.ssl_mode == "self-signed"

    assert cfg.db_root_user == "vimc"
    assert len(cfg.db_root_password) == 50
    assert cfg.db_users == {
        "api": {"password": "apipassword", "permissions": "all"},
        "import": {"password": "importpassword", "permissions": "all"},
        "orderly": {"password": "orderlypassword", "permissions": "all"},
        "readonly": {"password": "readonlypassword", "permissions": "readonly"},
    }
    assert len(cfg.db_protected_tables) == 12
    assert cfg.db_protected_tables[0] == "gavi_support_level"

    assert cfg.proxy_port_metrics == 9000


def test_config_email():
    cfg = MontaguConfig("config/basic")
    assert not cfg.real_emails

    options = {"api": {"email": {"password": "changeme"}}}
    with pytest.raises(Exception, match="flow_url"):
        MontaguConfig("config/basic", options=options)

    cfg = MontaguConfig("config/complete")
    assert cfg.real_emails
    assert cfg.email_password == "changeme"
    assert cfg.email_flow_url == "fakeurl"


def test_config_acme():
    cfg = MontaguConfig("config/acme")
    assert cfg.ssl_mode == "acme"
    acme_cfg = cfg.acme_config
    assert acme_cfg.email == "admin@montagu.org"


def test_config_generates_root_db_password():
    cfg = MontaguConfig("config/complete")
    assert cfg.db_root_password == "changeme"
    cfg = MontaguConfig("config/basic")
    assert cfg.db_root_password != "changeme"
    assert len(cfg.db_root_password) == 50


def test_config_streaming_replication():
    cfg = MontaguConfig("config/basic")
    assert not cfg.enable_streaming_replication
    cfg = MontaguConfig("config/complete")
    assert cfg.enable_streaming_replication
    assert cfg.db_users["barman"] == {"password": "barmanpassword", "option": "superuser"}
    assert cfg.db_users["streaming_barman"] == {"password": "streamingpassword", "option": "replication"}


def test_config_validates_db_user_permissions():
    options = {"db": {"users": {"api": {"permissions": "bad", "password": "pw"}}}}
    with pytest.raises(Exception, match="Invalid database permissions for 'api'"):
        MontaguConfig("config/basic", options=options)
