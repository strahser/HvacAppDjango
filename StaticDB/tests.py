import math

"""
Описание:

Константы: Определены константы из СНиП 2.04.05-91:

SOLAR_CONSTANT: Солнечная постоянная, 1353 Вт/м2
ALPHA_EARTH: Угол наклона земной оси, 23.45°
PI: Число Пи
Функции:

declination(day_of_year): Вычисляет деклинацию солнца в градусах по номеру дня года.
hour_angle(hour, longitude): Вычисляет часовой угол в градусах по часу по местному времени и долготе.
solar_incidence_angle(latitude, declination, hour_angle, azimuth, surface_azimuth, surface_tilt): Вычисляет угол падения солнечных лучей на поверхность в градусах, учитывая широту, деклинацию, часовой угол, азимут солнца, азимут поверхности и угол наклона поверхности.
solar_radiation(latitude, longitude, day_of_year, hour, surface_azimuth, surface_tilt): Вычисляет солнечную радиацию на поверхность в Вт/м2, используя ранее определенные функции и формулы.
Пример использования:

Заданы значения широты, долготы, дня года, часа, азимута поверхности и угла наклона поверхности.
Вызывается функция solar_radiation для вычисления солнечной радиации.
Результат выводится на экран.
Важно:

В коде используется система координат, где север - 0°, восток - 90°, юг - 180°, запад - 270°.
Для более точного расчета следует учесть дополнительные факторы, такие как:
Атмосферное поглощение
Облачность
Отражение от окружающих поверхностей
"""

# Константы из СНиП 2.04.05-91
SOLAR_CONSTANT = 1353  # Вт/м2
ALPHA_EARTH = 23.45  # угол наклона земной оси
PI = 3.14159


# Функция для расчета деклинации солнца
def declination(day_of_year):
	"""Расчет деклинации солнца в градусах.

  Args:
      day_of_year: День года (от 1 до 365).

  Returns:
      Деклинация солнца в градусах.
  """
	return 23.45 * math.sin(2 * PI * (day_of_year - 81) / 365)


# Функция для расчета часового угла
def hour_angle(hour, longitude):
	"""Расчет часового угла в градусах.

  Args:
      hour: Час по местному времени (от 0 до 23).
      longitude: Долгота места (в градусах).

  Returns:
      Часовой угол в градусах.
  """
	return 15 * (hour - 12) + longitude


# Функция для расчета угла падения солнечных лучей на поверхность
def solar_incidence_angle(latitude, declination, hour_angle, azimuth, surface_azimuth, surface_tilt):
	"""Расчет угла падения солнечных лучей на поверхность в градусах.

  Args:
      latitude: Широта места (в градусах).
      declination: Деклинация солнца (в градусах).
      hour_angle: Часовой угол (в градусах).
      azimuth: Азимут солнца (в градусах).
      surface_azimuth: Азимут поверхности (в градусах).
      surface_tilt: Угол наклона поверхности (в градусах).

  Returns:
      Угол падения солнечных лучей на поверхность в градусах.
  """
	# Вычисляем угол между солнечным лучом и горизонтальной проекцией на поверхность
	gamma = math.acos(math.sin(latitude * PI / 180) * math.sin(declination * PI / 180) + \
	                  math.cos(latitude * PI / 180) * math.cos(declination * PI / 180) * math.cos(
		hour_angle * PI / 180))

	# Вычисляем угол между солнечным лучом и нормалью к поверхности
	theta = math.acos(math.cos(gamma * PI / 180) * math.cos(surface_tilt * PI / 180) + \
	                  math.sin(gamma * PI / 180) * math.sin(surface_tilt * PI / 180) * math.cos(
		(azimuth - surface_azimuth) * PI / 180))

	return theta * 180 / PI


# Функция для расчета солнечной радиации
def solar_radiation(latitude, longitude, day_of_year, hour, surface_azimuth, surface_tilt):
	"""Расчет солнечной радиации на поверхность в Вт/м2.

  Args:
      latitude: Широта места (в градусах).
      longitude: Долгота места (в градусах).
      day_of_year: День года (от 1 до 365).
      hour: Час по местному времени (от 0 до 23).
      surface_azimuth: Азимут поверхности (в градусах).
      surface_tilt: Угол наклона поверхности (в градусах).

  Returns:
      Солнечная радиация на поверхность в Вт/м2.
  """
	# Вычисляем деклинацию солнца
	declination_angle = declination(day_of_year)

	# Вычисляем часовой угол
	hour_angle_value = hour_angle(hour, longitude)
	gamma = math.acos(math.sin(latitude * PI / 180) * math.sin(declination_angle * PI / 180) + \
	                  math.cos(latitude * PI / 180) * math.cos(declination_angle * PI / 180) * math.cos(
		hour_angle_value * PI / 180))

	# Вычисляем азимут солнца
	azimuth_angle = math.acos(
		(math.sin(declination_angle * PI / 180) * math.sin(latitude * PI / 180) - math.cos(gamma * PI / 180)) / (
					math.cos(declination_angle * PI / 180) * math.cos(latitude * PI / 180))) * 180 / PI
	# !!! Нужно вычислить gamma, иначе не работает!
	gamma = math.acos(math.sin(latitude * PI / 180) * math.sin(declination_angle * PI / 180) + \
	                  math.cos(latitude * PI / 180) * math.cos(declination_angle * PI / 180) * math.cos(
		hour_angle_value * PI / 180))

	# Вычисляем угол падения солнечных лучей
	incidence_angle = solar_incidence_angle(latitude, declination_angle, hour_angle_value, azimuth_angle,
	                                        surface_azimuth, surface_tilt)

	# Вычисляем солнечную радиацию
	radiation = SOLAR_CONSTANT * math.cos(incidence_angle * PI / 180)

	return radiation


# Пример использования функции
latitude = 55.75  # Широта Москвы
longitude = 37.62  # Долгота Москвы
day_of_year = 172  # 21 июня
hour = 12  # Полдень
surface_azimuth = 0  # Южная сторона
surface_tilt = 30  # Угол наклона крыши

radiation = solar_radiation(latitude, longitude, day_of_year, hour, surface_azimuth, surface_tilt)

print(f"Солнечная радиация: {radiation} Вт/м2")
