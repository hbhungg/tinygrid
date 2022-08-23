import unittest
import datetime
import numpy as np
import math

from tinygrid.utils import mase
from tinygrid.dataloader import DataUtils

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
    with open("sample_mase_data.txt") as f:
      sample_ans = [i.split() for i in f.readlines()]
    sample_ans = [float(i[2]) for i in sample_ans[:-2]]

    start = datetime.datetime(day=31, month=8, year=2020, hour=23, minute=59, second=59)
    end = datetime.datetime(day=30, month=9, year=2020, hour=23, minute=59, second=59)

    pred = np.zeros(2880)

    du = DataUtils()
    cols = du.cols
    diff = 0.0001
    for col, sa in zip(cols, sample_ans):
      data, _ = du.load_data_helper(col)
      training = np.array(data[:start]['energy'].values)
      true = np.array(data[start:end]['energy'].values)

      r_mase = mase(pred, true, training)
      with self.subTest(msg=col):
        self.assertTrue(math.isclose(r_mase, sa, rel_tol=diff), 
                        f"{r_mase} != {sa} with difference {diff}")



if __name__ == "__main__":
  unittest.main()
