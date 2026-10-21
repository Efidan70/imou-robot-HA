import sys, pathlib
from types import SimpleNamespace
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

ENTRY = SimpleNamespace(data={"device_id": "SERIAL123", "name": "Test robot", "model": "RV-L11-A"})
DATA = {"12300": 3, "11600": -100, "1027": 50, "1028": 40, "1020": 37, "1021": 36, "1029": 1, "11300": 4,
        "11400": True, "12202": 5, "40201": False, "40501": 0, "_status": "online"}


def coord():
    return SimpleNamespace(data=DATA, last_update_success=True)


def test_sensors_and_binary():
    from custom_components.imou_robot import sensor, binary_sensor
    c = coord()
    bat = sensor.ImouSensor(c, None, ENTRY, "battery", "Battery", "11600", "%", None,
                            lambda v: abs(sensor._int(v)))
    assert bat.native_value == 100 and bat.unique_id == "imou_SERIAL123_battery"
    assert bat.device_info["identifiers"] == {("imou_robot", "SERIAL123")}
    st = sensor.ImouSensor(c, None, ENTRY, "status", "Status", "12300", None, None,
                           lambda v: sensor.STATUS_TEXT.get(sensor._int(v), v))
    assert st.native_value == "Charging"
    assert binary_sensor.Charging(c, None, ENTRY).is_on is True       # negative battery = charging
    assert binary_sensor.Mop(c, None, ENTRY).is_on is True
    assert binary_sensor.Online(c, None, ENTRY).is_on is True


def test_switch_number_vacuum():
    from custom_components.imou_robot import switch, number, vacuum
    c = coord()
    assert switch.ImouSwitch(c, None, ENTRY, "light", "Light", "11400", "11400", "mdi:led-on").is_on is True
    assert switch.ImouSwitch(c, None, ENTRY, "dnd", "DND", "40201", "40200", "mdi:sleep", struct="40201").is_on is False
    assert number.ImouNumber(c, None, ENTRY, "water", "Water", "1028", "mdi:water").native_value == 40
    v = vacuum.ImouVacuum(c, None, ENTRY)
    assert v.unique_id == "imou_SERIAL123" and v.fan_speed == "standard"
    assert v._st() == "docked"


def test_sign_vector():
    from custom_components.imou_robot.api import calc_sign
    assert calc_sign(1706511734, "f5a1ae2d-c09c-4d39-a744-83a5c2c653c2",
                     "test123456789test123456789") == "xjhCQBoJ9hRDsCjyDcHjtDNzRZ3ZJezcawsfWeiaoxU="
