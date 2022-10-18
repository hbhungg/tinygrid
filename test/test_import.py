import unittest


class TestImport(unittest.TestCase):
  # Import of all of the user functionality
  def test_import_mase(self):
    try: from tinygrid.utils import mase
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_Const(self):
    try: from tinygrid.utils import Const
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_dataset(self):
    try: from tinygrid.dataset import IEEE_CIS
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_generate_solar_data(self):
    try: from tinygrid.forecaster import generate_solar_data
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_generate_building_data(self):
    try: from tinygrid.forecaster import generate_building_data
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)
    
  def test_import_Forecaster(self):
    try: from tinygrid.forecaster import Forecaster
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_optimizer(self):
    try: from tinygrid.optimizer import optimizer
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_save_schedule(self):
    try: from tinygrid.optimizer import save_schedule
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  # Private function
  def test_import_date_range(self):
    try: from tinygrid.utils import date_range
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_weekday_range(self):
    try: from tinygrid.utils import weekday_range
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_weekday_range(self):
    try: from tinygrid.utils import weekday_range
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

  def test_import_first_dow(self):
    try: from tinygrid.utils import first_dow
    except ModuleNotFoundError as e: self.fail(e)
    except ImportError as e: self.fail(e)

if __name__ == "__main__":
  unittest.main()
