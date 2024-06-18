import numpy as np

from StaticDB.StaticData.StaticCoefficientStructures import StaticCoefficientStructures
from StaticDB.StaticData.StructureTypeData import StructureTypeData


def get_normative_thermal_resistence_coefficient(gsop) -> dict[str, float]:
	return {
		StructureTypeData.Wall.name: 0.00035 * gsop + 1.4,
		StructureTypeData.Door.name: (0.00035 * gsop + 1.4)*0.55,
		StructureTypeData.Window.name: np.interp(gsop,
		                            StaticCoefficientStructures.normal_window_gsop_base,
		                            StaticCoefficientStructures.normal_thermal_coefficient_window_base
		                                         ),
		StructureTypeData.Floor.name: 0.0005 * gsop + 2.2,
		StructureTypeData.Roof.name: 0.00045 * gsop + 1.9,
		StructureTypeData.Skylight.name: 0.000025 * gsop + 0.25,
	}




