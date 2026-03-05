<script setup>
import { useMqtt } from "./composables/useMqtt.js";
import FloorPlan from "./components/FloorPlan.vue";
import TimeControl from "./components/TimeControl.vue";
import SensorCard from "./components/SensorCard.vue";
import ActuatorSwitch from "./components/ActuatorSwitch.vue";
import PowerDisplay from "./components/PowerDisplay.vue";

const { state, connected, publish } = useMqtt();
</script>

<template>
  <div class="app">
    <header>
      <h1>BMS Simulator</h1>
      <div class="connection-status" :class="{ online: connected }">
        <span class="status-dot"></span>
        {{ connected ? "Connected" : "Disconnected" }}
      </div>
    </header>

    <main>
      <section class="floor-section">
        <FloorPlan
          :temperature="state.temperature"
          :oat="state.oat"
          :occupancy="state.occupancy"
          :exteriorLightLevel="state.exteriorLightLevel"
          :interiorLightLevel="state.interiorLightLevel"
          :heat="state.heat"
          :airCon="state.airCon"
          :lights="state.lights"
          :temperatureOverridden="state.temperatureOverridden"
          :oatOverridden="state.oatOverridden"
          :occupancyOverridden="state.occupancyOverridden"
          :exteriorLightLevelOverridden="state.exteriorLightLevelOverridden"
          :interiorLightLevelOverridden="state.interiorLightLevelOverridden"
        />
      </section>

      <section class="controls-section">
        <div class="controls-row">
          <TimeControl
            :time="state.time"
            :rate="state.timeRate"
            :overridden="state.timeOverridden"
            @publish="publish"
          />

          <div class="controls-groups">
            <div class="control-group">
              <h2 class="group-title">Sensors</h2>
              <div class="sensor-subgroup">
                <h3 class="subgroup-title">Climate</h3>
                <div class="sensor-grid">
                  <SensorCard
                    label="Outside Air Temp"
                    :value="state.oat"
                    unit="°C"
                    topic="oat"
                    :overridden="state.oatOverridden"
                    icon="🌡"
                    @publish="publish"
                  />
                  <SensorCard
                    label="Interior Temp"
                    :value="state.temperature"
                    unit="°C"
                    topic="temperature"
                    :overridden="state.temperatureOverridden"
                    icon="🏢"
                    @publish="publish"
                  />
                </div>
              </div>
              <div class="sensor-subgroup">
                <h3 class="subgroup-title">Environment</h3>
                <div class="sensor-grid">
                  <SensorCard
                    label="Occupancy"
                    :value="state.occupancy"
                    topic="occupancy"
                    :overridden="state.occupancyOverridden"
                    type="boolean"
                    icon="👤"
                    @publish="publish"
                  />
                  <SensorCard
                    label="Exterior Light"
                    :value="state.exteriorLightLevel"
                    unit="lux"
                    topic="exterior_light_level"
                    :overridden="state.exteriorLightLevelOverridden"
                    icon="☀"
                    @publish="publish"
                  />
                  <SensorCard
                    label="Interior Light"
                    :value="state.interiorLightLevel"
                    unit="lux"
                    topic="interior_light_level"
                    :overridden="state.interiorLightLevelOverridden"
                    icon="💡"
                    @publish="publish"
                  />
                </div>
              </div>
            </div>

            <div class="control-group">
              <h2 class="group-title">Actuators</h2>
              <div class="actuator-grid">
                <ActuatorSwitch
                  label="Heater"
                  :value="state.heat"
                  topic="heat"
                  icon="🔥"
                  :power-kw="800"
                  contribution="Adds 10°C to interior"
                  @publish="publish"
                />
                <ActuatorSwitch
                  label="Air Conditioner"
                  :value="state.airCon"
                  topic="air_con"
                  icon="❄️"
                  :power-kw="1000"
                  contribution="Removes 10°C from interior"
                  @publish="publish"
                />
                <ActuatorSwitch
                  label="Lights"
                  :value="state.lights"
                  topic="lights"
                  icon="💡"
                  :power-kw="80"
                  contribution="Adds 400 lux"
                  @publish="publish"
                />
              </div>
            </div>

            <div class="control-group">
              <h2 class="group-title">Power Usage</h2>
              <PowerDisplay
                :current-power="state.powerUsage"
                :cumulative-power="state.cumulativePowerUsage"
              />
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background: #0a1018;
  color: #c0c8d0;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.app {
  min-height: 100vh;
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px;
}

header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  margin-bottom: 16px;
  border-bottom: 1px solid #1a2a3a;
}

header h1 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #e0e8f0;
  letter-spacing: 1px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #ff4444;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.connection-status.online {
  color: #00ff88;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ff4444;
}

.connection-status.online .status-dot {
  background: #00ff88;
  box-shadow: 0 0 6px #00ff88;
}

main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.floor-section {
  width: 100%;
}

.controls-section {
  width: 100%;
}

.controls-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 16px;
  align-items: start;
}

.controls-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.group-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #00aaff;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin: 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #2a3a4a;
}

.sensor-subgroup {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.subgroup-title {
  font-size: 0.75rem;
  font-weight: 500;
  color: #8899aa;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin: 0;
  padding-left: 4px;
}

.sensor-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.actuator-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

@media (max-width: 968px) {
  .controls-row {
    grid-template-columns: 1fr;
  }

  .actuator-grid {
    grid-template-columns: 1fr;
  }
}
</style>
