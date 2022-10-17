import unittest
import datetime
import numpy as np
import math

from tinygrid.utils import mase, Const
from tinygrid.dataset import IEEE_CISMixin

class TestMetrics(unittest.TestCase):
  def test_mase_type_checking(self):
    pred, true, training = 0, 0, 0
    with self.assertRaises(TypeError):
      mase(pred, true, training)

  @unittest.skip("skip this test im not done writing it yet!")
  def test_mase_nan(self):
    pass

  # TODO: Compare mase output with the sample_submission.csv
  def test_mase(self):
    # These values are generated from the given mase calc from the competition.
    sample_ans = {
        "Building0":3.111075,  
        "Building1":4.589733, 
        "Building3":4.1218123,
        "Building4":2.966333, 
        "Building5":1.720494,
        "Building6":10.558116,
        "Solar0":   3.355351,
        "Solar1":   1.543332,
        "Solar2":   1.748193,
        "Solar3":   2.043440,
        "Solar4":   1.851925,
        "Solar5":   2.839265}

    start = datetime.datetime(day=31, month=8, year=2020, hour=23, minute=59, second=59, tzinfo=Const.UTC)
    end = datetime.datetime(day=30, month=9, year=2020, hour=23, minute=59, second=59, tzinfo=Const.UTC)
    diff = 0.00001
    energy = IEEE_CISMixin._load_energy_data()

    pred = np.zeros(2880)
    for col in energy.keys():
      data = energy[col]
      training = np.array(data[:start]['energy'].values)
      true = np.array(data[start:end]['energy'].values)
      r_mase = mase(pred, true, training)
      sa = sample_ans[col]

      with self.subTest(msg=col):
        self.assertTrue(math.isclose(r_mase, sa, rel_tol=diff), 
                        f"{r_mase} != {sa} with difference {diff}")



if __name__ == "__main__":
  unittest.main()
