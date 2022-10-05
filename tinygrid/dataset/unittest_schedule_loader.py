import unittest
import os
from _schedule_loader import instance_parser, schedule_parser

class instance_parser_tests(unittest.TestCase):
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  INSTANCE_PATH = os.path.join(_BASE_DIR, "instance/")

  def setUp(self):
    self.instance_fnames = os.listdir(self.INSTANCE_PATH)

  def tearDown(self):
    pass

  def test_valid_files(self):
    for name in self.instance_fnames:
      full_path = os.path.join(self.INSTANCE_PATH, name)
      try:
        instance_parser(full_path)
      except:
        self.fail("Instance failed at " + full_path)

class schedule_parser_tests(unittest.TestCase):
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  INSTANCE_SAMPLE_SOLUTION_PATH = os.path.join(_BASE_DIR, "instance_sample_solution/")

  def setUp(self):
    self.instance_sol_fnames = os.listdir(self.INSTANCE_SAMPLE_SOLUTION_PATH)

  def tearDown(self):
    pass

  def test_valid_files(self):
    for name in self.instance_sol_fnames:
      full_path = os.path.join(self.INSTANCE_SAMPLE_SOLUTION_PATH, name)
      try:
        schedule_parser(full_path)
      except:
        self.fail("Instance solution failed at " + full_path)

  def test_incorrect_f_names(self):
    f_paths = ['qwerty#/asd\n','/e-sf/\n', '\n']
    for f_path in f_paths:
      self.assertRaises(Exception, schedule_parser, f_path)

  def test_only_newlines_file(self):
    f = open("test.txt", "w")
    for i in range(3):
      f.write("\n")
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")
    
  def test_empty_file(self):
    f = open("test.txt", "w")
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_different_tags(self):
    f = open("test.txt", "w")
    tags = ['p\n','adsas\n','&\n']
    for i in range(len(tags)):
      f.write(tags[i])
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")
  
  def test_no_ppoi(self):
    f = open("test.txt", "w")
    lines = ['sched 3 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_no_sched(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_wrong_sched(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 2 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  """ Battery tests """
  def test_bat_incorrect_decision(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 10 10\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_bat_incorrect_data_type(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', '1 0 10 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 10 b\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 f 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  """ Battery tests """

  """ Recurring activity tests """
  def test_re_act_incorrect_data_range(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 2 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_re_act_incorrect_data_type(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','1 0 98 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0','r 0 f 3 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 f 0 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 f 1 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 f 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")
  
  """ Recurring activity tests """
  
  """ Once-off activity tests """
  def test_once_off_incorrect_data_range(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','r 0 98 3 0 2 1\n','r 1 204 1 0\n','r 2 478 3 0 1 1\n', 'r 0 98 3 0 2 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  def test_once_off_incorrect_data_type(self):
    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','1 0 98 3 0 1 1\n','a 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','a 0 f 3 0 1 1\n','a 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','a 0 98 f 0 1 1\n','a 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','a 0 98 3 f 1 1\n','a 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

    f = open("test.txt", "w")
    lines = ['ppoi 6 6 2 50 20\n', 'sched 3 0\n','a 0 98 3 0 f 1\n','a 1 204 1 0\n','r 2 478 3 0 1 1\n', 'c 0 0 0\n', 'c 0 0 0\n']
    for line in lines:
      f.write(line)
    f.close()
    self.assertRaises(Exception, schedule_parser, "test.txt")
    os.remove("test.txt")

  """ Once-off activity tests """


if __name__ == '__main__':
    unittest.main()