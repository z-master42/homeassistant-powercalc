import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import (
    CONF_NAME,
    CONF_SENSOR_TYPE,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_registry import RegistryEntry
from pytest_homeassistant_custom_component.common import mock_registry

from custom_components.powercalc import SensorType
from custom_components.powercalc.config_flow import Step
from custom_components.powercalc.const import (
    CONF_CREATE_ENERGY_SENSOR,
    CONF_CREATE_UTILITY_METERS,
    CONF_GROUP_TRACKED_AUTO,
    CONF_GROUP_TRACKED_POWER_ENTITIES,
    CONF_GROUP_TYPE,
    CONF_MAIN_POWER_SENSOR,
    GroupType,
)
from tests.common import run_powercalc_setup
from tests.config_flow.common import (
    create_mock_entry,
    initialize_options_flow,
    select_menu_item,
)


async def test_config_flow(hass: HomeAssistant) -> None:
    """Test the tracked/untracked group flow."""

    await run_powercalc_setup(hass)
    mock_registry(
        hass,
        {
            "sensor.1_power": RegistryEntry(
                entity_id="sensor.1_power",
                unique_id="4444",
                platform="sensor",
                device_class=SensorDeviceClass.POWER,
                unit_of_measurement=UnitOfPower.WATT,
            ),
            "sensor.2_power": RegistryEntry(
                entity_id="sensor.2_power",
                unique_id="2222",
                platform="sensor",
                device_class=SensorDeviceClass.POWER,
                unit_of_measurement=UnitOfPower.WATT,
            ),
        },
    )

    result = await select_menu_item(hass, Step.MENU_GROUP, Step.GROUP_TRACKED_UNTRACKED)
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    user_input = {
        CONF_MAIN_POWER_SENSOR: "sensor.mains_power",
        CONF_GROUP_TRACKED_AUTO: True,
    }
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        user_input,
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert result["data"] == {
        CONF_CREATE_ENERGY_SENSOR: True,
        CONF_CREATE_UTILITY_METERS: False,
        CONF_SENSOR_TYPE: SensorType.GROUP,
        CONF_GROUP_TYPE: GroupType.TRACKED_UNTRACKED,
        CONF_NAME: "Tracked / Untracked",
        CONF_MAIN_POWER_SENSOR: "sensor.mains_power",
        CONF_GROUP_TRACKED_AUTO: True,
    }

    hass.states.async_set("sensor.mains_power", "100")
    await hass.async_block_till_done()
    hass.states.async_set("sensor.1_power", "10")
    hass.states.async_set("sensor.2_power", "20")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    tracked_power_state = hass.states.get("sensor.tracked_power")
    assert tracked_power_state
    assert tracked_power_state.state == "30.00"

    untracked_power_state = hass.states.get("sensor.untracked_power")
    assert untracked_power_state
    assert untracked_power_state.state == "70.00"


async def test_config_flow_manual(hass: HomeAssistant) -> None:
    """Test the tracked/untracked group flow."""
    await run_powercalc_setup(hass)
    mock_registry(
        hass,
        {
            "sensor.1_power": RegistryEntry(
                entity_id="sensor.1_power",
                unique_id="4444",
                platform="sensor",
                device_class=SensorDeviceClass.POWER,
                unit_of_measurement=UnitOfPower.WATT,
            ),
            "sensor.2_power": RegistryEntry(
                entity_id="sensor.2_power",
                unique_id="2222",
                platform="sensor",
                device_class=SensorDeviceClass.POWER,
                unit_of_measurement=UnitOfPower.WATT,
            ),
        },
    )

    result = await select_menu_item(hass, Step.MENU_GROUP, Step.GROUP_TRACKED_UNTRACKED)
    assert result["type"] == data_entry_flow.FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_MAIN_POWER_SENSOR: "sensor.mains_power",
            CONF_GROUP_TRACKED_AUTO: False,
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.FORM
    assert result["step_id"] == Step.GROUP_TRACKED_UNTRACKED_MANUAL

    schema_keys: list[vol.Optional] = list(result["data_schema"].schema.keys())
    assert schema_keys[schema_keys.index(CONF_GROUP_TRACKED_POWER_ENTITIES)].description == {"suggested_value": ["sensor.1_power", "sensor.2_power"]}

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            CONF_GROUP_TRACKED_POWER_ENTITIES: ["sensor.1_power", "sensor.2_power"],
        },
    )
    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY

    assert result["data"] == {
        CONF_CREATE_ENERGY_SENSOR: True,
        CONF_CREATE_UTILITY_METERS: False,
        CONF_SENSOR_TYPE: SensorType.GROUP,
        CONF_GROUP_TYPE: GroupType.TRACKED_UNTRACKED,
        CONF_NAME: "Tracked / Untracked",
        CONF_MAIN_POWER_SENSOR: "sensor.mains_power",
        CONF_GROUP_TRACKED_AUTO: False,
        CONF_GROUP_TRACKED_POWER_ENTITIES: ["sensor.1_power", "sensor.2_power"],
    }

    hass.states.async_set("sensor.mains_power", "100")
    await hass.async_block_till_done()
    hass.states.async_set("sensor.1_power", "10")
    hass.states.async_set("sensor.2_power", "20")
    await hass.async_block_till_done()
    await hass.async_block_till_done()

    tracked_power_state = hass.states.get("sensor.tracked_power")
    assert tracked_power_state
    assert tracked_power_state.state == "30.00"

    untracked_power_state = hass.states.get("sensor.untracked_power")
    assert untracked_power_state
    assert untracked_power_state.state == "70.00"


async def test_options_flow(hass: HomeAssistant) -> None:
    entry = create_mock_entry(
        hass,
        {
            CONF_SENSOR_TYPE: SensorType.GROUP,
            CONF_GROUP_TYPE: GroupType.TRACKED_UNTRACKED,
            CONF_NAME: "Tracked / Untracked",
            CONF_MAIN_POWER_SENSOR: "sensor.mains_power",
            CONF_GROUP_TRACKED_AUTO: True,
        },
    )

    result = await initialize_options_flow(hass, entry, Step.GROUP_TRACKED_UNTRACKED)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_GROUP_TRACKED_AUTO: False},
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert not entry.data[CONF_GROUP_TRACKED_AUTO]

    result = await initialize_options_flow(hass, entry, Step.GROUP_TRACKED_UNTRACKED_MANUAL)

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_GROUP_TRACKED_POWER_ENTITIES: ["sensor.1_power", "sensor.2_power"]},
    )

    assert result["type"] == data_entry_flow.FlowResultType.CREATE_ENTRY
    assert entry.data[CONF_GROUP_TRACKED_POWER_ENTITIES] == ["sensor.1_power", "sensor.2_power"]
