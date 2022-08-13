from dataset import IEEE_CIS

m = IEEE_CIS()
#schedule_data_paths_P1 = m.helper_schedule_data_paths(1, m.base_dir)
#schedule_data_paths_P2 = m.helper_schedule_data_paths(2, m.base_dir)
#multiple_files = m.load_schedule_data(schedule_data_paths_P1, schedule_data_paths_P2)

single_file = m.helper_schedule_reader(1, "/Users/harrisperdis/Documents/GitHub/tinygrid/dataset/schedule/phase1_instance_large_0.txt")



def constructGraph(data_model):
  pass