# Power meter

Generic IoT device.
Powercalc profiles can be used to define the self usage of the IoT device itself.

## JSON

```json
{
  "standby_power": 0.3,
  "sensor_config": {
    "power_sensor_naming": "{} Device Power",
    "energy_sensor_naming": "{} Device Energy"
  },
  "device_type": "power_meter",
  "calculation_strategy": "fixed",
  "discovery_by": "device",
  "fixed_config": {
    "power": 0.3
  }
}
```

!!! note
    Required fields are omitted in this example for brevity. For the full list of required fields see the [model structure](../structure.md)

!!! note
    The `discovery_by` field is set to `device` to prevent multiple discoveries for the same device.

Following the example above the power for this device will always be 0.3W.