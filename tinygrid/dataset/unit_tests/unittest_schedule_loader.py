import unittest
import os
from _schedule_loader import instance_parser, schedule_parser, Schedule, Instance

class schedule_parser_tests(unittest.TestCase):
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  INSTANCE_SAMPLE_SOLUTION_PATH = os.path.join(_BASE_DIR, "instance_sample_solution/")

  def setUp(self):
    self.instance_sol_fnames = os.listdir(self.INSTANCE_SAMPLE_SOLUTION_PATH)

  def tearDown(self):
    pass

  def valid_files_test(self):
    for name in self.instance_sol_fnames:
      full_path = os.path.join(self.INSTANCE_SAMPLE_SOLUTION_PATH, name)
      instance_data = schedule_parser(full_path)

  def incorrect_f_names_test(self):
    f_paths = ['qwerty#/asd','/e-sf/', '']
    for f_path in f_paths:
      self.assertRaises("file path " + f_path + " does not exist.", schedule_parser(f_path))

  def only_newlines_file_test(self):
    f = open("test.txt", "w")
    for i in range(len(3)):
      f.write("\n")
    f.close()
    self.assertRaises("file does not contain lines", schedule_parser("test.txt"))
    os.remove("test.txt")
    
  def empty_file_test(self):
    f = open("test.txt", "w")
    f.close()
    self.assertRaises("file does not contain lines", schedule_parser("test.txt"))
    os.remove("test.txt")

  def different_tags_test(self):
    pass
  
  def no_ppoi(self):
    pass

  def wrong_ppoi(self):
    pass

  def no_sched(self):
    pass

  def wrong_sched(self):
    pass

  """ Battery tests """
  def bat_incorrect_data_range_test(self):
    pass

  def bat_incorrect_data_type_test(self):
    pass
  
  def bat_correct_data_type_test(self):
    pass

  def bat_correct_data_range_test(self):
    pass
  """ Battery tests """

  """ Recurring activity tests """
  def re_act_incorrect_data_range_test(self):
    pass

  def re_act_incorrect_data_type_test(self):
    pass
  
  def re_act_correct_data_type_test(self):
    pass

  def re_act_correct_data_range_test(self):
    pass
  """ Recurring activity tests """
  
  """ Once-off activity tests """
  def once_off_incorrect_data_range_test(self):
    pass

  def once_off_incorrect_data_type_test(self):
    pass
  
  def once_off_correct_data_type_test(self):
    pass

  def once_off_correct_data_range_test(self):
    pass
  """ Once-off activity tests """


class instance_parser_tests(unittest.TestCase):
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  INSTANCE_DATA_PATH = os.path.join(_BASE_DIR, "instance/")

  def setUp(self):
    self.instance_fnames = os.listdir(self.INSTANCE_DATA_PATH)

  def tearDown(self):
    pass

  def valid_files_test(self):
    for name in self.instance_fnames:
      full_path = os.path.join(self.INSTANCE_DATA_PATH, name)
      instance_data = instance_parser(full_path)
  
  def incorrect_f_names_test(self):
    f_names = ['qwerty/asd','/esf/', '']

  def only_newlines_file_test(self):
    pass

  def empty_file_test(self):
    pass

