# NASA Farm Navigators — Frontend (Phaser + Vite)

Этот фронтенд подключается к вашему FastAPI-бэкенду и визуализирует «псевдо‑спутниковые» слои региона/фермы.

## Запуск
```bash
npm i
npm run dev
# по умолчанию http://localhost:5173
```
В верхней панели введите адрес API (например, `http://localhost:8000`) и нажмите **Load Layer**. Кнопкой **Simulate Season (Tick)** вы запускаете сезонную симуляцию.

## Горячие клавиши
- На региональной карте: `1..5` переключают слои (NDVI, Rain, Soil, Temp, Landuse), `SPACE` — Tick, `F` — ферма.
- На ферме: `A/D` — уменьшить/увеличить полив, `C/M` — включить Cover/Mulch, `R` — Tick, `ESC` — назад.

## Переменные окружения
Вы можете задать базовый URL API через `VITE_API_BASE`:
```bash
VITE_API_BASE=http://localhost:8000 npm run dev
```

## Структура
- `src/scenes/RegionScene.js` — региональная карта, загрузка слоя из `/region/{id}/layer?layer=...`
- `src/scenes/FarmScene.js` — ферма 1×1, план сезона и визуализация `/farm/{id}/raster`
- `src/api/client.js` — вызовы API
- `public/assets/legend_ndvi.png` — легенда (пример)
