# NASA Farm Navigators (MVP)

**An educational, single-player web strategy game that helps farmers and students explore how satellite data and on-farm choices shape long-term resilience.**

## TL;DR
Manage a 20-year farm campaign across contrasting regions (California’s San Joaquin, Khorezm/Amu Darya, Sahel). Each season you **Plan → Execute → Monitor → Adapt**, balancing short-term profits against long-term soil, water, and ecological health.

---

## Key Features

### Core Gameplay Loop
1. **Plan** seasonal crops/pastures, select tools (irrigation, drainage, soil protection), and set a financial plan (credit/insurance/subsidies).
2. **Execute** field operations and build/maintain infrastructure.
3. **Monitor** with maps and indicators (precipitation, soil moisture, NDVI, temperature, dust).
4. **Adapt** by rebalancing budget, switching tools, and adjusting rotations.

### Entities
- **Field tiles** (e.g., 25×25 m aggregates) with states: Crop / Fallow / Cover crop / Pasture / Infrastructure.
- **Crops** (region-specific sets) with water demand, salinity/heat tolerance, growth length, and soil effects.
- **Livestock** (optional by region) with rotational grazing that can increase fertility but risks overgrazing.
- **Infrastructure**: irrigation, drainage, soil protection, water storage/harvesting, monitoring devices.
- **Policies & Finance**: credit lines, weather/crop insurance, targeted subsidies, eco-fines for degradation.

### Region “Scenario Packs” (contrast by design)
- **California - San Joaquin (water-limited, orchards):** sustainable tools (drip + sensors, reservoirs, cover crops) vs. quick/risky (furrow flooding, aggressive groundwater pumping, no covers).
- **Uzbekistan - Khorezm/Amu Darya (salinity/waterlogging):** sustainable (subsurface drainage + leaching, gypsum on sodic soils, canal modernization) vs. quick/risky (“just add more water”, cotton monoculture, remove windbreaks).
- **Niger - Sahel (rainfed, erosion/dust):** sustainable (FMNR, zai pits, stone/earth bunds, agroforestry; compost/manure) vs. quick/risky (bare tillage, sowing without water capture, only mineral NPK).

### Indicators & Models (simplified for games)
- **Water balance** and **Water Debt** (quotas/allocations vs. use).
- **Soil salinity** dynamics (irrigation EC, leaching, drainage).
- **Soil fertility** trajectory (cover crops, mulch, manure, erosion, rotation).
- **NDVI & stress** from water/heat/salinity/pests.
- **Events**: historical (region-specific) and procedural triggers (e.g., low NDVI, high salinity, heatwaves, rain anomalies).

### Telemetry & NASA data
Back end connects to **GPM** (precipitation), **SMAP** (soil moisture), **HLS/NDVI**, and optionally **VIIRS** (night lights/activity).

### Difficulty & Tuning
Balanced around meaningful trade-offs: “sustainable long-term” vs. “fast/cheap now.” Presets (Easy/Default/Hard) adjust penalties, risk weights, subsidies, event probabilities, and price volatility.

---

## Score (MVP)
The final score blends economy and sustainability:
```text
Score = 0.40 * Economic Outcome
      + 0.40 * Eco Sustainability   # fertility↑, salinity↓, water debt↓, NDVI vs baseline↑
      + 0.15 * Risk Management      # insurance, buffers, diversification
      + 0.05 * Resource Efficiency  # water productivity, energy efficiency
