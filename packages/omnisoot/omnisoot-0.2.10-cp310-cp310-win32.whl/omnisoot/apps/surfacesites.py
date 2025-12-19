from ..lib._omnisoot import CConstantSites, CEvolvingSites
from .plugins import register

SURFACESITES_MODELS = [];

@register(SURFACESITES_MODELS)
class ConstantSites(CConstantSites):
    serialized_name = "ConstantSites"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);


@register(SURFACESITES_MODELS)
class EvolvingSites(CEvolvingSites):
    serialized_name = "EvolvingSites"
    def __init__(self, soot_gas):
        super().__init__(soot_gas);