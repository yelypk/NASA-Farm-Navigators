# Minimal, inline manifests. You can replace with JSON files later.
CROPS = {
    # base_yield (t/ha), water_need (0..1), salt_tol (0..1), ndvi_peak (0..1)
    "fallow": {"yield": 0.0, "water": 0.2, "salt": 1.0, "ndvi_peak": 0.15, "price": 0.0},
    "wheat":  {"yield": 3.5, "water": 0.5, "salt": 0.5, "ndvi_peak": 0.75, "price": 220.0},
    "maize":  {"yield": 6.0, "water": 0.7, "salt": 0.4, "ndvi_peak": 0.80, "price": 210.0},
    "cotton": {"yield": 2.0, "water": 0.8, "salt": 0.6, "ndvi_peak": 0.70, "price": 300.0},
    "alfalfa":{"yield": 10.0, "water": 0.6, "salt": 0.7, "ndvi_peak": 0.85, "price": 180.0},
    "millet": {"yield": 1.5, "water": 0.35,"salt": 0.8, "ndvi_peak": 0.60, "price": 170.0},
}

REGIONS = {
    "california": {
        "display": "California (water-limited orchards)",
        "seasonal_rain": {"spring":0.35,"summer":0.1,"autumn":0.25,"winter":0.5},
        "seasonal_temp": {"spring":0.6,"summer":0.9,"autumn":0.6,"winter":0.3}
    },
    "amu_darya": {
        "display": "Amu Darya / Khorezm (salinity & drainage)",
        "seasonal_rain": {"spring":0.25,"summer":0.15,"autumn":0.2,"winter":0.3},
        "seasonal_temp": {"spring":0.5,"summer":0.85,"autumn":0.55,"winter":0.25}
    },
    "sahel": {
        "display": "Sahel (rain-fed, erosion risk)",
        "seasonal_rain": {"spring":0.1,"summer":0.55,"autumn":0.25,"winter":0.05},
        "seasonal_temp": {"spring":0.7,"summer":0.9,"autumn":0.7,"winter":0.6}
    }
}
