import unittest
from tinygrid.dataset import IEEE_CIS

class load_ERA5_weather_data_tests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CIS
  def tearDown(self):
    pass
  def test_call(self):
    try:
      self.cl.load_ERA5_weather_data()
    except:
      self.fail("Instance failed at _load_ERA5_weather_data")

class load_AEMO_price_datatests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CIS
  def tearDown(self):
    pass
  def test_call(self):
    try:
      self.cl.load_AEMO_price_data()
    except:
      self.fail("Instance failed at _load_AEMO_price_data")

class load_energy_data_tests(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CIS
  def tearDown(self):
    pass  
  def test_call(self):
    try:
      self.cl.load_energy_data()
    except:
      self.fail("Instance failed at _load_energy_data")

class load_instance_data(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CISMixin
  def test_call(self):
    try:
      self.cl._load_instance_data()
    except:
      self.fail("Instance failed at _load_instance_data")

class load_instance_sample_solution_data(unittest.TestCase):
  def setUp(self):
    self.cl = IEEE_CISMixin
  def test_call(self):
    try:
      self.cl._load_instance_sample_solution_data()
    except:
      self.fail("Instance failed at _load_instance_sample_solution_data")

if __name__ == '__main__':
    unittest.main()
