class schedual_model:
    def __init__(self, phase, path) -> None:
        self.ppoi = {}
        self.buildings = []
        self.solars = []
        self.batteries = []
        self.f_path = path

        # activites
        self.acts = []
        self.once_off_acts = []

        # Phase in competition
        self.phase = phase

    def add_ppoi(self, line_arr):
        self.ppoi = {
            "buildings": int(line_arr[1]),
            "solar": int(line_arr[2]),
            "battery": int(line_arr[3]),
            "recurring": int(line_arr[4]),
            "once-off": int(line_arr[5])
        }

    def add_building(self, line_arr):
        temp = {
            "building_id": line_arr[1],
            "small_rooms": int(line_arr[2]),
            "large_rooms": int(line_arr[3])
        }
        self.buildings.append(temp)
    
    def add_solar(self, line_arr):
        temp = {
            "solar_id": line_arr[1],
            "building_id": line_arr[2]
        }
        self.solars.append(temp)

    def add_battery(self, line_arr):
        temp = {
            "building_id": line_arr[1],
            "capacity_kWh": int(line_arr[2]),
            "max_power_kW": int(line_arr[3]),
            "efficiency": float(line_arr[4])
        }
        self.batteries.append(temp)

    def add_act(self, line_arr):
        pass
    
    def add_once_off_act(self, line_arr):
        pass



