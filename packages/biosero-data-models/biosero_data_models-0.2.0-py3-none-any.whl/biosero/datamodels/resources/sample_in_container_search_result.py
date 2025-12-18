from biosero.datamodels.measurement import Concentration, Volume, Weight


class SampleInContainerSearchResult:
    def __init__(
        self,
        containerIdentifier=None,
        sampleIdentifier=None,
        concentration=None,
        netVolume=None,
        netWeight=None,
        path=None,
        **kwargs
    ):
        """
        Constructor matches API wire format (camelCase keys).
        Extra fields are safely ignored via **kwargs.
        """

        self.container_identifier = containerIdentifier
        self.sample_identifier = sampleIdentifier

        self.concentration = (
            Concentration(**concentration) if isinstance(concentration, dict) else None
        )
        self.net_volume = (
            Volume(**netVolume) if isinstance(netVolume, dict) else None
        )
        self.net_weight = (
            Weight(**netWeight) if isinstance(netWeight, dict) else None
        )

        self.path = path

    # -------------------------
    # Case-insensitive helpers
    # -------------------------

    @staticmethod
    def get_ci(d: dict, key: str):
        """Case-insensitive dict lookup with camelCase fallback."""
        if key in d:
            return d[key]
        camel_key = key[:1].lower() + key[1:]
        return d.get(camel_key)

    # -------------------------
    # Optional explicit factory
    # -------------------------

    @classmethod
    def from_dict(cls, data: dict):
        """
        Explicit constructor when you control object creation.
        Not used by the SDK, but useful elsewhere.
        """
        return cls(
            containerIdentifier=cls.get_ci(data, "ContainerIdentifier"),
            sampleIdentifier=cls.get_ci(data, "SampleIdentifier"),
            concentration=cls.get_ci(data, "Concentration"),
            netVolume=cls.get_ci(data, "NetVolume"),
            netWeight=cls.get_ci(data, "NetWeight"),
            path=cls.get_ci(data, "Path"),
        )
