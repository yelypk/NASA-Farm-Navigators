from dataclasses import dataclass

@dataclass
class Scale:
    vmin: float
    vmax: float

# Пресеты нормирования: подберём базово, можно потом заменить данными из readme_for_model.md
SCALES = {
    "ndvi": Scale(0.0, 1.0),     # NDVI 0..1
    "rain": Scale(0.0, 400.0),   # мм за сезон (регион-зависимо, калибруем)
    "dry":  Scale(0.0, 1.0),     # 1-SMAP 0..1
    "temp": Scale(-3.0, 3.0),    # аномалии, ±3°C ~ разумный предел
}
