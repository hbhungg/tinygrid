from dataset import IEEE_CIS
import os

m = IEEE_CIS()
schedule_data_paths_P1 = m.helper_schedule_data_paths(1)
schedule_data_paths_P2 = m.helper_schedule_data_paths(2)
multiple_files = m.load_schedule_data(schedule_data_paths_P1, schedule_data_paths_P2)

phase1_instance_large_0_path = os.path.join(m.base_dir, "schedule/" + "phase1_instance_large_0.txt") 
single_file = m.helper_schedule_reader(1, phase1_instance_large_0_path)
price = m.load_AEMO_nov_price_data()

print(single_file.add_graph_act())