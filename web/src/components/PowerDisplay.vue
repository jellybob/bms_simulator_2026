<script setup>
import { computed } from "vue";

const props = defineProps({
  currentPower: Number,
  cumulativePower: Number,
});

const powerLevel = computed(() => {
  // Calculate intensity based on max possible power (all actuators on = 1880 kW)
  const maxPower = 1880;
  return Math.min(props.currentPower / maxPower, 1);
});

const powerColor = computed(() => {
  if (props.currentPower === 0) return "#2a3a4a";
  if (props.currentPower < 500) return "#00ff88";
  if (props.currentPower < 1000) return "#ffaa00";
  return "#ff4444";
});
</script>

<template>
  <div class="power-display">
    <div class="power-section current">
      <div class="power-header">
        <span class="power-icon">⚡</span>
        <span class="power-label">Current Power Draw</span>
      </div>
      <div class="power-value-container">
        <div
          class="power-bar"
          :style="{
            width: `${powerLevel * 100}%`,
            background: powerColor,
          }"
        ></div>
        <div class="power-value">
          <span class="value">{{ currentPower.toFixed(1) }}</span>
          <span class="unit">kW</span>
        </div>
      </div>
    </div>

    <div class="power-section cumulative">
      <div class="power-header">
        <span class="power-icon">📊</span>
        <span class="power-label">Daily Total</span>
      </div>
      <div class="power-value">
        <span class="value">{{ cumulativePower.toFixed(2) }}</span>
        <span class="unit">kWh</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.power-display {
  background: #1a2332;
  border: 1px solid #2a3a4a;
  border-radius: 8px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.power-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.power-section.current {
  padding-bottom: 16px;
  border-bottom: 1px solid #2a3a4a;
}

.power-header {
  display: flex;
  align-items: center;
  gap: 8px;
}

.power-icon {
  font-size: 1.2rem;
}

.power-label {
  color: #8899aa;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.power-value-container {
  position: relative;
  background: #0d1520;
  border-radius: 6px;
  overflow: hidden;
  padding: 12px;
  min-height: 60px;
}

.power-bar {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  transition: all 0.3s ease;
  opacity: 0.2;
}

.power-value {
  position: relative;
  display: flex;
  align-items: baseline;
  gap: 6px;
  z-index: 1;
}

.power-section.cumulative .power-value {
  padding-left: 4px;
}

.value {
  font-family: "Courier New", monospace;
  font-size: 2rem;
  font-weight: bold;
  color: #e0e8f0;
}

.power-section.cumulative .value {
  font-size: 1.6rem;
}

.unit {
  color: #556677;
  font-size: 1rem;
  font-weight: normal;
}

.power-section.cumulative .unit {
  font-size: 0.9rem;
}
</style>
