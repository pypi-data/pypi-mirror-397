# PALM-4U-preprocessor-OAP

OGC API Process for preprocessing Palm 4U

## Publishing

The package will automatically published to PyPI, when manually pushing a tag to this repo.

Tags must follow this pattern: \d+.\d+.\d+, e.g. (0.0.2)

## Configuration

Following parameters can be adjusted in pygeoapi config.yaml:

```yaml
processor:
  name: palm_4u_preprocessor_oap.palm_4u_preprocessor.Palm4UPreprocessor
  args:
    udt2palm: # optional udt2palm configuration. All paths must be absolute. Defaults below.
      exec_path: '/app' # Path from where udt2palm should be called.
      out_dir: '/app/data/output/' # Directory in which the process outputs will be stored.
      config_path: '/app/config/config.example.json' # Path to the process config.
    models: # optional list of supported models. Defaults to ['A']
      - A
    min_area_sqm: 1000000 # optional minimum area for running process. Defaults to 1000000
    max_area_sqm: 25000000 # optional maximum area for running process. Defaults to 25000000
    restrict_to_bbox: # optional bbox in which the area must be located. Defaults below.
      xmin: 454951
      xmax: 510592
      ymin: 5718946
      ymax: 5746580
```
