import json
from collections import defaultdict
from shapely.geometry import Polygon, MultiPoint, LineString
import plotly.graph_objects as go

def find_outer_walls(room_data):
    """
    Находит отрезки (стены) из полигонов комнат, которые совпадают с
    минимально выпуклую оболочкой для каждого уровня (этажа).

    Args:
        room_data: Словарь с данными помещений, где ключ - идентификатор помещения,
                   а значение - словарь с координатами полигона.

    Returns:
        Словарь, где ключ - уровень (этаж),
        а значение - список отрезков (стен), совпадающих с конвексным корпусом.
    """

    outer_walls_by_level = defaultdict(list)

    for room_id, room_coords in room_data.items():
        level = room_coords['pz'][0]  # Получаем уровень (этаж)
        room_polygon = Polygon(zip(room_coords['px'], room_coords['py']))

        # Создаем список всех линий, составляющих полигон помещения
        lines = [
            LineString([(room_coords['px'][i], room_coords['py'][i]), (room_coords['px'][i + 1], room_coords['py'][i + 1])])
            for i in range(len(room_coords['px']) - 1)
        ]

        # Находим конвексный корпус для этого уровня
        building_polygon = find_building_polygon(room_data, level)

        # Проверяем, совпадают ли отрезки с конвексным корпусом
        for line in lines:
            if line.intersection(building_polygon.exterior).length == line.length:
                outer_walls_by_level[level].append(line)

    return outer_walls_by_level

def find_building_polygon(room_data, level):
    """
    Находит минимально выпуклую оболочку (конвексный корпус) здания
    для указанного уровня (этажа).

    Args:
        room_data: Словарь с данными помещений.
        level: Уровень (этаж).

    Returns:
        Объект shapely.geometry.Polygon, представляющий конвексный корпус.
    """

    all_points = []
    for room_id, room_coords in room_data.items():
        if room_coords['pz'][0] == level:  # Проверяем уровень
            all_points.extend(zip(room_coords['px'], room_coords['py']))

    # Создаем объект MultiPoint из всех точек
    multi_point = MultiPoint(all_points)

    # Находим конвексный корпус
    building_polygon = multi_point.convex_hull

    return building_polygon

def plot_outer_walls(outer_walls_by_level):
    """
    Отображает наружные стены помещений на графике Plotly,
    сгруппированные по уровням (этажам).

    Args:
        outer_walls_by_level: Словарь, где ключ - уровень (этаж),
                              а значение - список наружных стен.
    """

    for level, walls in outer_walls_by_level.items():
        fig = go.Figure()
        for wall in walls:
            fig.add_trace(go.Scatter(
                x=list(wall.coords.xy[0]),
                y=list(wall.coords.xy[1]),
                mode='lines',
                line=dict(color='blue', width=2)
            ))

        fig.update_layout(
            title=f'Наружные стены помещений на уровне {level}',
            xaxis_title='X',
            yaxis_title='Y'
        )
        fig.show()


# Чтение данных из JSON
with open(r'd:\Yandex\YandexDisk\ProjectCoding\InputDataStreamlit\InputFiles\polygon_data_file.json', 'r') as f:
    room_data = json.load(f)

# Получаем список уникальных этажей
levels = set(room_coords['pz'][0] for room_id, room_coords in room_data.items())

# Отображаем наружные стены для каждого этажа
for level in levels:
    # Фильтруем данные помещений по текущему уровню
    room_data_level = {
        room_id: room_coords
        for room_id, room_coords in room_data.items()
        if room_coords['pz'][0] == level
    }

    outer_walls_by_level = find_outer_walls(room_data_level)
    plot_outer_walls(outer_walls_by_level)