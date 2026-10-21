DOMAIN = "imou_robot"
DEFAULT_URL = "https://openapi-fk.easy4ip.com"
# Thing-model refs of the RV-L11-A
P_STATUS, P_BATTERY, P_FAN, P_WATER, P_DOCK = "12300", "11600", "1027", "1028", "1019"
P_AREA, P_TIME, P_MOP = "1020", "1021", "1029"
PROP_REFS = [P_STATUS, P_BATTERY, P_FAN, P_WATER, P_DOCK, P_AREA, P_TIME, P_MOP]
# work_status enum -> activity
STATUS = {
    0: "idle", 1: "paused", 2: "returning", 3: "docked", 4: "cleaning", 5: "cleaning",
    6: "error", 7: "cleaning", 8: "cleaning", 9: "cleaning", 10: "cleaning",
    11: "docked", 12: "cleaning", 13: "paused",
}
