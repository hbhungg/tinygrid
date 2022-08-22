import unittest
from tinygrid.utils import mase

class TestMetrics(unittest.TestCase):
  def test_mase_type_checking(self):
    pred = 0
    true = 0
    training = 0
    with self.assertRaises(TypeError):
      mase(pred, true, training)

  def test_mase_nan(self):
    pass

  # TODO: Compare mase output with the sample_submission.csv
  def test_mase(self):
    pass


if __name__ == "__main__":
  unittest.main()
