from opt_algorithm import Sim_Annealing

def sol_writer(self, s_path, s_schedual):
  # Get length of all dictionaries in s_schedual
  arr_l = []
  for item in s_schedual:
    arr_l.append(len(item))
  # Write ppoi header for solution file
  f = open(s_path, 'w')
  f.write('ppoi' + ' '.join(str(l) for l in arr_l))
  # Write sched header
  f.write('sched' + '')
  # Write recurring activities
  for act in s_schedual.re_act:
    f.write('r' + '')
  # Write once-off activities
  for act in s_schedual.once_act:
    f.write('a' + '')
  # Write batteries
  for bat in s_schedual.batteries:
    f.write('c' + '')
  # Close write
  f.close()