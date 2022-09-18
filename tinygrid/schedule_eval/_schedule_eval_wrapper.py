import os
from subprocess import check_output, CalledProcessError

def schedule_eval_wrapper(instance_path: str, schedule_path: str, phase: int) -> float:
  """
  Simple Python wrapper around the Java optim_eval.
  Warning, high recommended to pass in the full path instead of relative path for instance and schedule.
  Params:
    instance_path: path to the instance file
    schedule_path: path to the schedule file (solution)
    phase: which phase we want to evaluate
  Return:
    Optimization score (Objective function score)
  """
  # Have to use full path since this function will be called by different places.
  _BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  # Shell command
  move_to_dir = f"cd {_BASE_DIR}/bin"
  java_optim_eval = "java edu.monash.ppoi.EvaluateSchedule"
  command = f"({move_to_dir} && {java_optim_eval} {instance_path} {schedule_path} {phase})"

  try:
    output = check_output(command, shell=True)
    return float(output.decode("UTF-8"))
  except CalledProcessError as e:
    return_code = e.returncode
    return {"assertion_errors": 0, "run_errors": 1}

