from dataclasses import dataclass
from django.db.models import F
from Config.models import Building
from HeatBalance.Models.HeatLoadData.HeatLoad import TotalHeat
from Spaces.models import SpaceData
import pandas as pd
from Systems.models import FancoilSystem


@dataclass
class HeatModel:
	S_ID: str
	total_lighting_load: float
	total_human_load: float
	total_radiation_load: float
	total_equipment_load: float
	additional_load: float
	total_heat_load: float


class HeatLoadUtility:

	@staticmethod
	def calculate_heat_balance_query() -> pd.DataFrame:
		qs = SpaceData.objects \
			.values("S_ID", "S_Number") \
			.annotate(lighting_load=F("space_category__lighting") * F("S_area")) \
			.annotate(total_human_load=F("space_category__human_heat") * F("human_number"))
		df = pd.DataFrame(qs)
		return df

	@staticmethod
	def create_filter_fancoil_system(df:pd.DataFrame)->None:
		fancoil_systems_data = FancoilSystem.objects.all()
		fancoil_systems = fancoil_systems_data.values_list("space_data__S_ID", flat=True)
		df_filter = df[df['S_ID'].isin(fancoil_systems)]
		for _idx, row in df_filter.iterrows():
			system = fancoil_systems_data.filter(pk=row['S_ID'])
			system.update(system_flow=row['total_heat_load'])

	@staticmethod
	def calculate_total_heat_load():
		spaces = SpaceData.objects.all()
		climate_data = Building.objects.filter(spacedata=spaces[0]).first().climate_data.sun_radiation
		heat_balance_list = []
		for space in spaces.select_related("space_category", ):
			total_heat = TotalHeat(space, climate_data)
			heat_model = HeatModel(
				S_ID=space.S_ID,
				total_human_load=total_heat.total_human_load(),
				total_lighting_load=total_heat.total_lighting_load(),
				total_equipment_load=total_heat.total_equipment_load(),
				total_radiation_load=total_heat.total_radiation_load(),
				additional_load=total_heat.additional_load(),
				total_heat_load=total_heat.total_heat_load()
			)
			heat_balance_list.append(heat_model)
		df = pd.DataFrame(heat_balance_list)
		return df