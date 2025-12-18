from biosero.datamodels.measurement import Concentration, Volume, Weight

class SampleInContainerSearchResult:
    def __init__(self, container_identifier, sample_identifier, concentration, net_volume, net_weight, path):
        self.container_identifier = container_identifier
        self.sample_identifier = sample_identifier
        self.concentration = Concentration(**concentration)
        self.net_volume = Volume(**net_volume)
        self.net_weight = Weight(**net_weight)
        self.path = path

    @staticmethod
    def get_ci(d: dict, key: str):
        """Case-insensitive dict lookup"""
        if key in d:
            return d[key]
        lower_key = key[:1].lower() + key[1:]
        return d.get(lower_key)

    @classmethod
    def from_dict(cls, data):
        return cls(
            container_identifier=cls.get_ci(data, 'ContainerIdentifier'),
            sample_identifier=cls.get_ci(data, 'SampleIdentifier'),
            concentration=cls.get_ci(data, 'Concentration'),
            net_volume=cls.get_ci(data, 'NetVolume'),
            net_weight=cls.get_ci(data, 'NetWeight'),
            path=cls.get_ci(data, 'Path')
        )

    

