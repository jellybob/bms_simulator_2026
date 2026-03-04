<script setup>
import { computed } from "vue";

const props = defineProps({
  temperature: Number,
  oat: Number,
  occupancy: Boolean,
  lightLevel: Number,
  temperatureOverridden: Boolean,
  oatOverridden: Boolean,
  occupancyOverridden: Boolean,
  lightLevelOverridden: Boolean,
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

const lightOpacity = computed(() => {
  return Math.min(1, Math.max(0.05, props.lightLevel / 1000));
});

const lightFill = computed(() => {
  const op = lightOpacity.value;
  return `rgba(255, 255, 180, ${op * 0.3})`;
});
</script>

<template>
  <div class="floor-plan">
    <svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">
      <!-- Building outline -->
      <rect
        x="80" y="40" width="440" height="320"
        rx="4" fill="none" stroke="#2a3a4a" stroke-width="2"
      />

      <!-- Light level ambient fill over whole interior -->
      <rect
        x="81" y="41" width="438" height="318"
        rx="3" :fill="lightFill"
        class="light-ambient"
      />

      <!-- Reception / Lobby -->
      <rect x="80" y="260" width="160" height="100" fill="none" stroke="#2a3a4a" stroke-width="1" />
      <text x="160" y="295" text-anchor="middle" class="room-label">Reception</text>

      <!-- Meeting Room -->
      <rect x="80" y="40" width="160" height="120" fill="none" stroke="#2a3a4a" stroke-width="1" />
      <text x="160" y="85" text-anchor="middle" class="room-label">Meeting Room</text>

      <!-- Open Office -->
      <rect x="240" y="40" width="280" height="220" fill="none" stroke="#2a3a4a" stroke-width="1" />
      <text x="380" y="85" text-anchor="middle" class="room-label">Open Office</text>

      <!-- Kitchen -->
      <rect x="240" y="260" width="140" height="100" fill="none" stroke="#2a3a4a" stroke-width="1" />
      <text x="310" y="295" text-anchor="middle" class="room-label">Kitchen</text>

      <!-- Server Room -->
      <rect x="380" y="260" width="140" height="100" fill="none" stroke="#2a3a4a" stroke-width="1" />
      <text x="450" y="295" text-anchor="middle" class="room-label">Server Room</text>

      <!-- Corridor -->
      <rect x="80" y="160" width="160" height="100" fill="none" stroke="#2a3a4a" stroke-width="1" stroke-dasharray="4 2" />
      <text x="160" y="215" text-anchor="middle" class="room-label" style="font-size: 9px">Corridor</text>

      <!-- === Sensor Indicators === -->

      <!-- Interior Temperature indicator (open office) -->
      <circle
        cx="380" cy="160" r="32"
        :fill="tempColor" fill-opacity="0.2"
        :stroke="tempColor" stroke-width="3"
        class="sensor-indicator"
      />
      <text x="380" y="155" text-anchor="middle" class="sensor-value-text" :fill="tempColor">
        {{ temperature.toFixed(1) }}
      </text>
      <text x="380" y="172" text-anchor="middle" class="sensor-unit-text">&#176;C</text>
      <circle v-if="temperatureOverridden" cx="405" cy="132" r="6" fill="#ffaa00" />

      <!-- Occupancy indicator (meeting room) -->
      <g :class="{ active: occupancy }" class="occupancy-indicator">
        <!-- Person icon -->
        <circle cx="160" cy="112" r="6" :fill="occupancy ? '#00ff88' : '#334455'" />
        <line x1="160" y1="118" x2="160" y2="132" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2" />
        <line x1="152" y1="124" x2="168" y2="124" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2" />
        <line x1="160" y1="132" x2="154" y2="142" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2" />
        <line x1="160" y1="132" x2="166" y2="142" :stroke="occupancy ? '#00ff88' : '#334455'" stroke-width="2" />
        <text x="160" y="155" text-anchor="middle" class="sensor-label-text">
          {{ occupancy ? "OCCUPIED" : "VACANT" }}
        </text>
      </g>
      <circle v-if="occupancyOverridden" cx="175" cy="108" r="5" fill="#ffaa00" />

      <!-- Light Level indicator (corridor) -->
      <g class="light-indicator">
        <!-- Light bulb icon -->
        <circle cx="160" cy="192" r="10" :fill="'rgba(255,255,100,' + lightOpacity + ')'" stroke="#556677" stroke-width="1" />
        <line x1="156" y1="203" x2="164" y2="203" stroke="#556677" stroke-width="1.5" />
        <line x1="157" y1="206" x2="163" y2="206" stroke="#556677" stroke-width="1.5" />
        <!-- Rays -->
        <line v-if="lightLevel > 100" x1="160" y1="178" x2="160" y2="174" stroke="#ffff66" stroke-width="1" opacity="0.6" />
        <line v-if="lightLevel > 100" x1="172" y1="185" x2="175" y2="182" stroke="#ffff66" stroke-width="1" opacity="0.6" />
        <line v-if="lightLevel > 100" x1="148" y1="185" x2="145" y2="182" stroke="#ffff66" stroke-width="1" opacity="0.6" />
        <text x="160" y="220" text-anchor="middle" class="sensor-value-small">{{ lightLevel.toFixed(0) }} lux</text>
      </g>
      <circle v-if="lightLevelOverridden" cx="175" cy="185" r="5" fill="#ffaa00" />

      <!-- OAT indicator (outside the building) -->
      <g class="oat-indicator">
        <!-- Thermometer body -->
        <rect x="32" y="100" width="10" height="50" rx="5" fill="none" :stroke="oatColor" stroke-width="1.5" />
        <rect
          x="34" :y="150 - (Math.min(40, Math.max(0, oat + 10)) / 50 * 44)"
          width="6"
          :height="Math.min(40, Math.max(0, oat + 10)) / 50 * 44"
          rx="3" :fill="oatColor"
        />
        <circle cx="37" cy="160" r="8" :fill="oatColor" fill-opacity="0.3" :stroke="oatColor" stroke-width="1.5" />
        <text x="37" y="180" text-anchor="middle" class="sensor-value-small" :fill="oatColor">
          {{ oat.toFixed(1) }}&#176;C
        </text>
        <text x="37" y="92" text-anchor="middle" class="sensor-label-text">OAT</text>
      </g>
      <circle v-if="oatOverridden" cx="52" cy="95" r="5" fill="#ffaa00" />

      <!-- Outside label -->
      <text x="37" y="60" text-anchor="middle" class="room-label" style="font-size: 9px">Outside</text>

      <!-- Door indicators -->
      <rect x="200" y="196" width="40" height="4" rx="2" fill="#2a3a4a" />
      <rect x="200" y="305" width="40" height="4" rx="2" fill="#2a3a4a" />
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

.room-label {
  fill: #445566;
  font-size: 16px;
  font-family: sans-serif;
}

.sensor-value-text {
  font-family: "Courier New", monospace;
  font-size: 20px;
  font-weight: bold;
}

.sensor-unit-text {
  fill: #556677;
  font-size: 14px;
  font-family: sans-serif;
}

.sensor-value-small {
  fill: #8899aa;
  font-family: "Courier New", monospace;
  font-size: 14px;
}

.sensor-label-text {
  fill: #556677;
  font-size: 13px;
  font-family: sans-serif;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.sensor-indicator {
  transition: fill 0.5s, stroke 0.5s;
}

.light-ambient {
  transition: fill 1s;
  pointer-events: none;
}

.occupancy-indicator.active text {
  fill: #00ff88;
}
</style>
