import subprocess
import logging
from pathlib import Path
import json
import zipfile
import shutil
from shapely import polygons


LOGGER = logging.getLogger(__name__)


def create_process_dirs(run_out_dir):
  run_dir = Path(run_out_dir)
  run_dir.mkdir(parents=True)
  LOGGER.debug(f'Created run_dir {run_dir}')

  process_dir = Path(run_dir) / 'process'
  process_dir.mkdir()
  LOGGER.debug(f'Created process_dir {process_dir}')

  return run_dir, process_dir


def render_config(config_path, out_dir, process_dir, model_id, area):
  with open(config_path, 'r') as file:
    config = json.load(file)

  for _, output_config in config['outputdata'].items():
    if 'files' in output_config and 'path' in output_config['files']:
      output_config['files']['path'] = str(process_dir)

  config['settings']['application_field'] = model_id

  area_pol = polygons(area['coordinates'])[0]
  area_bounds = area_pol.bounds
  config['settings']['boundary']['west'] = area_bounds[0]
  config['settings']['boundary']['south'] = area_bounds[1]
  config['settings']['boundary']['east'] = area_bounds[2]
  config['settings']['boundary']['north'] = area_bounds[3]

  output_config_path = out_dir / 'config.json'
  with open(output_config_path, 'w') as file:
    json.dump(config, file, indent=2)

  LOGGER.debug(f'Rendered config to {output_config_path}')
  return output_config_path


def prepare_run(run_out_dir, config_dir, model_id, area):
  run_dir, process_dir = create_process_dirs(run_out_dir)
  rendered_config = render_config(config_dir, run_dir, process_dir, model_id, area)
  return run_dir, process_dir, rendered_config


def zip_output(out_dir, process_dir):
  zip_path = out_dir / 'output.zip'

  with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for file_path in process_dir.rglob('*'):
      if file_path.is_file():
        arcname = file_path.relative_to(process_dir)
        zipf.write(file_path, arcname)
        LOGGER.debug(f"Added {file_path} to zip as {arcname}")

  LOGGER.debug(f"Created zip file: {zip_path}")
  return zip_path


def read_zip(zip_path):
  with open(zip_path, 'rb') as f:
    data = f.read()
  LOGGER.debug(f"Read zip file: {zip_path}")
  return data


def call_udt2palm(config, exec_path):
  venv_udt2palm = '/venv_udt2palm/bin/python3'
  LOGGER.debug(f'Starting subprocess udt2palm with config {config}')
  try:
    subprocess.run(
      [
        venv_udt2palm, '-m',
        'udt2palm.main',
        '--config', str(config),
        '--log-level', 'ERROR'
        ],
      cwd=exec_path,
      capture_output=True,
      text=True,
      check=True
    )
    LOGGER.debug(f'Finished subprocess udt2palm with config {config}')
    return True
  except subprocess.CalledProcessError as e:
    LOGGER.error(f"Failed executing subprocess udt2palm with config {config}: {e.stdout}")
    return False


def remove_process_dir(process_dir):
  shutil.rmtree(process_dir)


def run_udt2palm(run_out_dir, config_dir, model_id, area, exec_path):
  run_dir, process_dir, rendered_config = prepare_run(run_out_dir, config_dir, model_id, area)
  successful_run = call_udt2palm(rendered_config, exec_path)
  if not successful_run:
    return None
  zip_path = zip_output(run_dir, process_dir)
  remove_process_dir(process_dir)
  return read_zip(zip_path)
