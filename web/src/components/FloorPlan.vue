<script setup>
import { computed } from "vue";

const props = defineProps({
  temperature: Number,
  oat: Number,
  occupancy: Boolean,
  exteriorLightLevel: Number,
  interiorLightLevel: Number,
  heat: Boolean,
  airCon: Boolean,
  lights: Boolean,
  temperatureOverridden: Boolean,
  oatOverridden: Boolean,
  occupancyOverridden: Boolean,
  exteriorLightLevelOverridden: Boolean,
  interiorLightLevelOverridden: Boolean,
});

const tempColor = computed(() => {
  const t = props.temperature;
  if (t <= 16) return "#3388ff";
  if (t <= 20) return "#33aaff";
  if (t <= 22) return "#33cc88";
  if (t <= 25) return "#88cc33";
  if (t <= 28) return "#ffaa33";
  return "#ff4444";
});

const oatColor = computed(() => {
  const t = props.oat;
  if (t <= 0) return "#6688ff";
  if (t <= 10) return "#33aaff";
  if (t <= 20) return "#33cc88";
  if (t <= 30) return "#ffaa33";
  return "#ff4444";
});

const exteriorLightOpacity = computed(() => {
  // Scale more aggressively - at 2000 lux we want full brightness
  const rawOpacity = props.exteriorLightLevel / 2000;
  return Math.min(1, Math.max(0.05, Math.pow(rawOpacity, 0.5))); // Square root for brighter appearance
});

const interiorLightOpacity = computed(() => {
  const rawOpacity = props.interiorLightLevel / 800;
  return Math.min(1, Math.max(0.03, Math.pow(rawOpacity, 0.6)));
});

const sunColor = computed(() => {
  const op = exteriorLightOpacity.value;
  // Much brighter sun - use higher base RGB and stronger opacity
  return `rgba(255, 245, 120, ${Math.min(1, op * 1.5)})`;
});

// Text colors that adapt to background brightness
const exteriorTextColor = computed(() => {
  // When bright outside, use dark text; when dim, use light text
  return exteriorLightOpacity.value > 0.5 ? "#1a2a3a" : "#8899aa";
});

const interiorTextColor = computed(() => {
  // Interior background is never bright enough for dark text to work well
  // Always use light text that works on both dark and moderately lit backgrounds
  return "#c0d0e0";
});

// Temperature change over next hour (°C/hour)
// Based on THERMAL_RATE = 0.01 °C/min/°ΔT from server
const THERMAL_RATE = 0.01;
const MINUTES_PER_HOUR = 60;
const HEATER_CONTRIBUTION = 10.0;
const AC_CONTRIBUTION = 10.0;

const tempChangePerHour = computed(() => {
  let change = (props.oat - props.temperature) * THERMAL_RATE * MINUTES_PER_HOUR;
  if (props.heat) change += HEATER_CONTRIBUTION * THERMAL_RATE * MINUTES_PER_HOUR;
  if (props.airCon) change -= AC_CONTRIBUTION * THERMAL_RATE * MINUTES_PER_HOUR;
  return change;
});

const heatFlowColor = computed(() => {
  if (tempChangePerHour.value > 0.5) return "#ff6644";
  if (tempChangePerHour.value < -0.5) return "#4488ff";
  return "#556677";
});
</script>

<template>
  <div class="floor-plan">
    <svg viewBox="0 0 800 320" xmlns="http://www.w3.org/2000/svg">

      <!-- ===== OUTSIDE ZONE (x: 0-170) ===== -->

      <!-- Sky background tinted by exterior light -->
      <rect
        x="0" y="0" width="170" height="320"
        :fill="`rgba(120, 180, 255, ${0.2 + exteriorLightOpacity * 0.8})`"
        class="transition-fill"
      />

      <!-- Ground line -->
      <line x1="0" y1="260" x2="170" y2="260" stroke="#2a3a4a" stroke-width="1" />
      <rect x="0" y="260" width="170" height="60" fill="#1a2520" />

      <!-- Sun icon -->
      <g class="transition-fill">
        <circle cx="85" cy="60" r="22" :fill="sunColor" />
        <!-- Sun rays -->
        <line v-for="i in 8" :key="'ray'+i"
          :x1="85 + 28 * Math.cos(i * Math.PI / 4)"
          :y1="60 + 28 * Math.sin(i * Math.PI / 4)"
          :x2="85 + 36 * Math.cos(i * Math.PI / 4)"
          :y2="60 + 36 * Math.sin(i * Math.PI / 4)"
          :stroke="sunColor" stroke-width="2" stroke-linecap="round"
        />
        <text x="85" y="110" text-anchor="middle" class="sensor-value-small" :fill="exteriorTextColor">
          {{ exteriorLightLevel.toFixed(0) }} lux
        </text>
      </g>
      <circle v-if="exteriorLightLevelOverridden" cx="115" cy="45" r="5" fill="#ffaa00" />

      <!-- OAT thermometer -->
      <g class="oat-indicator">
        <rect x="62" y="150" width="10" height="50" rx="5" fill="none" :stroke="oatColor" stroke-width="1.5" />
        <rect
          x="64" :y="200 - (Math.min(40, Math.max(0, oat + 10)) / 50 * 44)"
          width="6"
          :height="Math.min(40, Math.max(0, oat + 10)) / 50 * 44"
          rx="3" :fill="oatColor"
        />
        <circle cx="67" cy="210" r="8" :fill="oatColor" fill-opacity="0.3" :stroke="oatColor" stroke-width="1.5" />
        <text x="95" y="185" text-anchor="start" class="sensor-value-small" :fill="oatColor">
          {{ oat.toFixed(1) }}&#176;C
        </text>
        <text x="85" y="140" text-anchor="middle" class="sensor-label-text" :fill="exteriorTextColor">OAT</text>
      </g>
      <circle v-if="oatOverridden" cx="80" cy="145" r="5" fill="#ffaa00" />

      <text x="85" y="16" text-anchor="middle" class="zone-label" :fill="exteriorTextColor">OUTSIDE</text>

      <!-- ===== WALL (x: 170-200) ===== -->

      <rect x="170" y="0" width="30" height="320" fill="#2a3a4a" />
      <!-- Window -->
      <rect x="174" y="70" width="22" height="60" rx="2" fill="#1a2a3a" stroke="#445566" stroke-width="1" />
      <!-- Window glass with light transmission -->
      <rect
        x="176" y="72" width="18" height="56" rx="1"
        :fill="`rgba(180, 220, 255, ${exteriorLightOpacity * 0.15})`"
        class="transition-fill"
      />
      <!-- Window crossbar -->
      <line x1="185" y1="72" x2="185" y2="128" stroke="#445566" stroke-width="0.5" />
      <line x1="176" y1="100" x2="194" y2="100" stroke="#445566" stroke-width="0.5" />

      <!-- ===== HEAT FLOW ZONE (x: 200-380) ===== -->

      <rect x="200" y="0" width="180" height="320" fill="#0d1520" />
      <text x="290" y="16" text-anchor="middle" class="zone-label">HEAT FLOW</text>

      <!-- Heater icon (top) -->
      <g>
        <rect x="220" y="40" width="60" height="40" rx="4"
          :fill="heat ? '#331a10' : '#151d28'"
          :stroke="heat ? '#ff6644' : '#2a3a4a'" stroke-width="1.5"
        />
        <text x="250" y="55" text-anchor="middle" class="actuator-label">HEATER</text>
        <!-- Flame icons when on -->
        <g v-if="heat">
          <path d="M240,72 Q240,65 244,68 Q248,62 248,72" fill="#ff6644" opacity="0.8" />
          <path d="M250,72 Q250,63 254,67 Q258,60 258,72" fill="#ff8844" opacity="0.7" />
        </g>
        <text x="250" y="65" text-anchor="middle" class="actuator-state" :fill="heat ? '#ff6644' : '#334455'">
          {{ heat ? "ON" : "OFF" }}
        </text>
        <!-- Arrow showing heat contribution -->
        <line v-if="heat" x1="285" y1="60" x2="340" y2="60"
          stroke="#ff6644" stroke-width="2" stroke-dasharray="4 3" opacity="0.7" />
        <polygon v-if="heat" points="340,55 350,60 340,65" fill="#ff6644" opacity="0.7" />
        <text v-if="heat" x="315" y="52" text-anchor="middle" class="heat-label" fill="#ff6644">+10&#176;C</text>
      </g>

      <!-- AC icon (bottom) -->
      <g>
        <rect x="220" y="110" width="60" height="40" rx="4"
          :fill="airCon ? '#101a33' : '#151d28'"
          :stroke="airCon ? '#4488ff' : '#2a3a4a'" stroke-width="1.5"
        />
        <text x="250" y="125" text-anchor="middle" class="actuator-label">A/C</text>
        <text x="250" y="137" text-anchor="middle" class="actuator-state" :fill="airCon ? '#4488ff' : '#334455'">
          {{ airCon ? "ON" : "OFF" }}
        </text>
        <!-- Arrow showing cooling -->
        <line v-if="airCon" x1="285" y1="130" x2="340" y2="130"
          stroke="#4488ff" stroke-width="2" stroke-dasharray="4 3" opacity="0.7" />
        <polygon v-if="airCon" points="340,125 350,130 340,135" fill="#4488ff" opacity="0.7" />
        <text v-if="airCon" x="315" y="122" text-anchor="middle" class="heat-label" fill="#4488ff">-10&#176;C</text>
      </g>

      <!-- OAT contribution arrow -->
      <g>
        <line x1="200" y1="185" x2="340" y2="185"
          :stroke="oatColor" stroke-width="1.5" stroke-dasharray="4 3" opacity="0.5" />
        <polygon :points="(oat >= temperature) ? '340,180 350,185 340,190' : '210,180 200,185 210,190'"
          :fill="oatColor" opacity="0.5" />
        <text x="270" y="200" text-anchor="middle" class="sensor-value-small" :fill="oatColor">
          OAT drift
        </text>
      </g>

      <!-- Temperature change forecast -->
      <rect x="220" y="220" width="140" height="50" rx="6"
        fill="none" :stroke="heatFlowColor" stroke-width="1.5" stroke-dasharray="3 2"
      />
      <text x="290" y="240" text-anchor="middle" class="sensor-label-text" :fill="heatFlowColor">
        NEXT HOUR
      </text>
      <text x="290" y="258" text-anchor="middle" class="sensor-value-text" :fill="heatFlowColor">
        {{ tempChangePerHour > 0 ? "+" : "" }}{{ tempChangePerHour.toFixed(1) }}&#176;C
      </text>

      <!-- ===== OFFICE INTERIOR (x: 380-800) ===== -->

      <!-- Room background tinted by interior light -->
      <rect
        x="380" y="0" width="420" height="320"
        :fill="`rgba(255, 250, 220, ${interiorLightOpacity * 0.25})`"
        class="transition-fill"
      />

      <!-- Floor -->
      <line x1="380" y1="260" x2="800" y2="260" stroke="#2a3a4a" stroke-width="1" />
      <rect x="380" y="260" width="420" height="60" fill="#151a20" />

      <!-- Ceiling -->
      <line x1="380" y1="30" x2="800" y2="30" stroke="#2a3a4a" stroke-width="1" />

      <text x="590" y="16" text-anchor="middle" class="zone-label" :fill="interiorTextColor">OFFICE INTERIOR</text>

      <!-- Ceiling light fixture -->
      <g class="light-fixture">
        <!-- Fixture base -->
        <rect x="565" y="30" width="50" height="6" rx="2" fill="#2a3a4a" />
        <!-- Light cone when on -->
        <polygon v-if="lights"
          points="565,36 600,36 640,120 525,120"
          fill="rgba(255, 255, 180, 0.06)"
        />
        <!-- Bulb -->
        <circle cx="590" cy="44" r="8"
          :fill="lights ? 'rgba(255,255,120,0.9)' : '#1a2530'"
          :stroke="lights ? '#ffff88' : '#334455'" stroke-width="1"
        />
        <!-- Rays when on -->
        <g v-if="lights" opacity="0.5">
          <line x1="590" y1="56" x2="590" y2="64" stroke="#ffff66" stroke-width="1" />
          <line x1="600" y1="50" x2="606" y2="56" stroke="#ffff66" stroke-width="1" />
          <line x1="580" y1="50" x2="574" y2="56" stroke="#ffff66" stroke-width="1" />
        </g>
        <text x="590" y="80" text-anchor="middle" class="actuator-state"
          :fill="lights ? '#ffff88' : '#334455'">
          {{ lights ? "ON" : "OFF" }}
        </text>
      </g>

      <!-- Interior temperature indicator -->
      <circle
        cx="490" cy="160" r="36"
        :fill="tempColor" fill-opacity="0.15"
        :stroke="tempColor" stroke-width="3"
        class="sensor-indicator"
      />
      <text x="490" y="155" text-anchor="middle" class="sensor-value-text" :fill="tempColor">
        {{ temperature.toFixed(1) }}
      </text>
      <text x="490" y="175" text-anchor="middle" class="sensor-unit-text">&#176;C</text>
      <text x="490" y="210" text-anchor="middle" class="sensor-label-text" :fill="interiorTextColor">INTERIOR</text>
      <circle v-if="temperatureOverridden" cx="520" cy="128" r="5" fill="#ffaa00" />

      <!-- Occupancy indicator -->
      <g :class="{ active: occupancy }" class="occupancy-indicator">
        <circle cx="690" cy="185" r="8" :fill="occupancy ? '#00ff88' : '#334455'" />
        <line x1="690" y1="193" x2="690" y2="212" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2.5" />
        <line x1="680" y1="200" x2="700" y2="200" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2.5" />
        <line x1="690" y1="212" x2="683" y2="228" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2.5" />
        <line x1="690" y1="212" x2="697" y2="228" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2.5" />
        <text x="690" y="245" text-anchor="middle" class="sensor-label-text" :fill="interiorTextColor">
          {{ occupancy ? "OCCUPIED" : "VACANT" }}
        </text>
      </g>
      <circle v-if="occupancyOverridden" cx="708" cy="180" r="5" fill="#ffaa00" />

      <!-- Interior light level reading -->
      <text x="590" y="280" text-anchor="middle" class="sensor-value-small" :fill="interiorTextColor">
        {{ interiorLightLevel.toFixed(0) }} lux
      </text>
      <circle v-if="interiorLightLevelOverridden" cx="635" cy="276" r="5" fill="#ffaa00" />

    </svg>
  </div>
</template>

<style scoped>
.floor-plan {
  background: #0d1520;
  border: 1px solid #2a3a4a;
  border-radius: 8px;
  padding: 12px;
}

svg {
  width: 100%;
  height: auto;
}

.zone-label {
  font-size: 11px;
  font-family: sans-serif;
  text-transform: uppercase;
  letter-spacing: 2px;
}

.sensor-value-text {
  font-family: "Courier New", monospace;
  font-size: 22px;
  font-weight: bold;
}

.sensor-unit-text {
  fill: #556677;
  font-size: 14px;
  font-family: sans-serif;
}

.sensor-value-small {
  font-family: "Courier New", monospace;
  font-size: 13px;
}

.sensor-label-text {
  font-size: 11px;
  font-family: sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.actuator-label {
  fill: #667788;
  font-size: 10px;
  font-family: sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.actuator-state {
  font-family: "Courier New", monospace;
  font-size: 12px;
  font-weight: bold;
}

.heat-label {
  font-family: "Courier New", monospace;
  font-size: 11px;
  font-weight: bold;
}

.sensor-indicator {
  transition: fill 0.5s, stroke 0.5s;
}

.transition-fill {
  transition: fill 1s;
}

.occupancy-indicator.active text {
  fill: #00ff88;
}
</style>
