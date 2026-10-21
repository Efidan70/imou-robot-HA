DOMAIN = "imou_robot"
DEFAULT_URL = "https://openapi-fk.easy4ip.com"
DATACENTERS = {
    "fk": "https://openapi-fk.easy4ip.com",   # Frankfurt (Europe)
    "sg": "https://openapi-sg.easy4ip.com",   # Singapore (Asia)
    "or": "https://openapi-or.easy4ip.com",   # Oregon (Americas)
}
CONF_IDLE, CONF_ACTIVE = "idle_interval", "active_interval"
DEFAULT_IDLE, DEFAULT_ACTIVE = 120, 30
# Thing-model refs of the Imou RV-L11-A
P_STATUS, P_BATTERY, P_FAN, P_WATER, P_DOCK = "12300", "11600", "1027", "1028", "1019"
P_AREA, P_TIME, P_MOP = "1020", "1021", "1029"
P_HOME = "11500"   # home_switch: start/stop button of the app home screen
P_WIFI, P_LIGHT, P_KEEP, P_DUST, P_RUG, P_VOLUME = "11300", "11400", "11700", "11800", "11900", "12000"
P_LIFE, P_DND, P_ERR = "12200", "40200", "40500"
PROP_REFS = [P_HOME, P_STATUS, P_BATTERY, P_FAN, P_WATER, P_DOCK, P_AREA, P_TIME, P_MOP, P_WIFI,
             P_LIGHT, P_KEEP, P_DUST, P_RUG, P_VOLUME, P_LIFE, P_DND, P_ERR]
STATUS = {
    0: "idle", 1: "paused", 2: "returning", 3: "docked", 4: "cleaning", 5: "cleaning",
    6: "error", 7: "cleaning", 8: "cleaning", 9: "cleaning", 10: "cleaning",
    11: "docked", 12: "cleaning", 13: "paused",
}
STATUS_TEXT = {0: "Standby", 1: "Paused", 2: "Returning to dock", 3: "Charging", 4: "Locating",
               5: "Remote control", 6: "Error", 7: "Room cleaning", 8: "Zone cleaning",
               9: "Spot cleaning", 10: "Go to point", 11: "Emptying dust", 12: "Whole-home cleaning",
               13: "Return paused"}
WIFI_TEXT = {0: "Abnormal", 1: "No network", 2: "Poor", 3: "Fair", 4: "Good"}
ACTIVE = {2, 4, 5, 7, 8, 9, 10, 11, 12}
