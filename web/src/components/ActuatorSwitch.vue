<script setup>
const props = defineProps({
  label: String,
  value: Boolean,
  topic: String,
  icon: String,
  powerKw: Number,
  contribution: String,
});

const emit = defineEmits(["publish"]);

function toggle() {
  const newValue = !props.value;
  emit("publish", `${props.topic}/set`, newValue ? "true" : "false");
}
</script>

<template>
  <div class="actuator-card" :class="{ active: value }">
    <div class="actuator-header">
      <span class="actuator-icon">{{ icon }}</span>
      <span class="actuator-label">{{ label }}</span>
      <button class="toggle-switch" :class="{ on: value }" @click="toggle">
        <span class="switch-slider"></span>
      </button>
    </div>

    <div class="actuator-status">
      <span class="status-text" :class="{ on: value }">
        {{ value ? "ON" : "OFF" }}
      </span>
    </div>

    <div class="actuator-info">
      <div class="info-row">
        <span class="info-label">Power:</span>
        <span class="info-value" :class="{ active: value }">
          {{ value ? powerKw.toLocaleString() : "0" }} kW
        </span>
      </div>
      <div class="info-row contribution">
        <span class="contribution-text">{{ contribution }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.actuator-card {
  background: #1a2332;
  border: 1px solid #2a3a4a;
  border-radius: 8px;
  padding: 14px;
  transition: all 0.3s;
}

.actuator-card.active {
  border-color: #00aaff;
  background: #1d2838;
}

.actuator-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.actuator-icon {
  font-size: 1.4rem;
}

.actuator-label {
  color: #8899aa;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 1px;
  flex: 1;
}

.toggle-switch {
  width: 50px;
  height: 26px;
  background: #2a3a4a;
  border: 1px solid #3a4a5a;
  border-radius: 13px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s;
  padding: 0;
}

.toggle-switch:hover {
  border-color: #4a5a6a;
}

.toggle-switch.on {
  background: #00aaff;
  border-color: #00aaff;
}

.switch-slider {
  position: absolute;
  width: 20px;
  height: 20px;
  background: #e0e8f0;
  border-radius: 50%;
  top: 2px;
  left: 2px;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.toggle-switch.on .switch-slider {
  left: 26px;
}

.actuator-status {
  margin-bottom: 10px;
}

.status-text {
  font-family: "Courier New", monospace;
  font-size: 1.4rem;
  font-weight: bold;
  color: #556677;
  transition: color 0.3s;
}

.status-text.on {
  color: #00ff88;
}

.actuator-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 10px;
  border-top: 1px solid #2a3a4a;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-label {
  color: #8899aa;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-family: "Courier New", monospace;
  font-size: 0.9rem;
  color: #556677;
  font-weight: bold;
  transition: color 0.3s;
}

.info-value.active {
  color: #ffaa00;
}

.info-row.contribution {
  margin-top: 4px;
}

.contribution-text {
  color: #6a7a8a;
  font-size: 0.7rem;
  font-style: italic;
  line-height: 1.3;
}
</style>
