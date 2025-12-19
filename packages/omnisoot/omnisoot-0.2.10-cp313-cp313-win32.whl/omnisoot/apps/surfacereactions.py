from ..lib._omnisoot import CFrenklachHACA, CFrenklachHACAModified, CBlanquartHACA
from .plugins import register

SURFACEREACTIONS_MODELS = [];

# temporary mixin classes for backward compatibility
# these will be removed in future releases
class SurfaceReactionsMixin():
    @property
    def surface_reactivity_model_type(self):
        if (
            self.soot_wrapper.surface_sites_model_type == "ConstantSites" and self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type == "constant"
        ):
            return "constant";
        elif (
            self.soot_wrapper.surface_sites_model_type == "ConstantSites" and self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type == "appell.et.al"
        ):
            return "empirical"
        elif (
            self.soot_wrapper.surface_sites_model_type == "ConstantSites" and self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type == "HtoC"
        ):
            return "composition"
        elif (
            self.soot_wrapper.surface_sites_model_type == "EvolvingSites"
        ):
            return "evolving"        
        else:
            raise ValueError("Invalid surface reactivity model type!");

    @surface_reactivity_model_type.setter
    def surface_reactivity_model_type(self, name):
        if (name == "constant"):
            self.soot_wrapper.surface_sites_model_type = "ConstantSites";
            self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type = "constant";
        elif (name == "empirical"):
            self.soot_wrapper.surface_sites_model_type = "ConstantSites";
            self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type = "appell.et.al";
        elif (name == "composition"):
            self.soot_wrapper.surface_sites_model_type = "ConstantSites";
            self.soot_wrapper.surface_sites_model.surface_reactivity_steric_factor_type = "HtoC";
        elif (name == "evolving"):
            self.soot_wrapper.surface_sites_model_type = "EvolvingSites";
        else:
            raise ValueError("Invalid surface reactivity model type!");


@register(SURFACEREACTIONS_MODELS)
class FrenklachHACA(SurfaceReactionsMixin, CFrenklachHACA):
    serialized_name = "FrenklachHACA"
    def __init__(self, soot_wrapper):
        super().__init__(soot_wrapper);


@register(SURFACEREACTIONS_MODELS)
class FrenklachHACAModified(SurfaceReactionsMixin, CFrenklachHACAModified):
    serialized_name = "FrenklachHACAModified"
    def __init__(self, soot_wrapper):
        super().__init__(soot_wrapper);


@register(SURFACEREACTIONS_MODELS)
class BlanquartHACA(SurfaceReactionsMixin, CBlanquartHACA):
    serialized_name = "BlanquartHACA"
    def __init__(self, soot_wrapper):
        super().__init__(soot_wrapper);

