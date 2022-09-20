from opt_algorithm import Sim_Annealing

def sol_writer(self, s_path, s_schedule):
  # Get length of all dictionaries in s_schedule
  arr_l = []
  for item in s_schedule:
    arr_l.append(len(item))
  # Write ppoi header for solution file
  f = open(s_path, 'w')
  f.write('ppoi' + ' '.join(str(l) for l in arr_l))
  # Write sched header
  f.write('sched' + '')
  # Write recurring activities
  for act in s_schedule.re_act:
    f.write('r' + '')
  # Write once-off activities
  for act in s_schedule.once_act:
    f.write('a' + '')
  # Write batteries
  for bat in s_schedule.batteries:
    f.write('c' + '')
  # Close write
  f.close()