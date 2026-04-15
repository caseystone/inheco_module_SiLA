import dataclasses
import collections.abc
from importlib.metadata import version

from unitelabs.cdk import Connector, ConnectorBaseConfig, SiLAServerConfig

# from unitelabs.cdk import sila

from .features.door_controller import DoorController

__version__ = version("unitelabs-inheco-test-connector")


DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {"simple": {"format": "{asctime} [{levelname!s:<8}] {message!s}", "style": "{"}},
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {"root": {"level": "INFO", "handlers": ["stdout", "stderr"]}},
}


@dataclasses.dataclass
class InhecoTestConnectorConfig(ConnectorBaseConfig):
    """Configuration for the Inheco Test Connector."""

    sila_server: SiLAServerConfig = dataclasses.field(
        default_factory=lambda: SiLAServerConfig(
            name="Inheco Test Connector",
            type="Example",
            description=(
                """
                A connector for the Inheco Test Connector built with the UniteLabs CDK.
                """
            ),
            version=str(__version__),
            vendor_url="https://unitelabs.io/",
        )
    )
    logging: dict = dataclasses.field(default_factory=lambda: DEFAULT_LOGGING_CONFIG)



async def create_app(config: InhecoTestConnectorConfig) -> collections.abc.AsyncGenerator[Connector, None]:
    """Create the connector application."""
    app = Connector(config)

    app.register(DoorController())

    yield app
