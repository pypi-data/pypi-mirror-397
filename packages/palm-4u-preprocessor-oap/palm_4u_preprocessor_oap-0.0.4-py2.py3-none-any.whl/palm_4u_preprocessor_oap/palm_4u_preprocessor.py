import logging
from datetime import datetime, timezone
from shapely import polygons, Polygon
from shapely.geometry import shape
from pygeoapi.process.base import BaseProcessor, ProcessorExecuteError
from .udt2palm_runner import run_udt2palm

LOGGER = logging.getLogger(__name__)

PROCESS_METADATA = {
    'version': '0.0.1',
    'id': 'palm4u_preprocessor',
    'title': {
        'en': 'Palm4U Preprocessor',
    },
    'description': {
        'en': 'Palm4U Preprocessor',
    },
    'jobControlOptions': ['sync-execute', 'async-execute'],
    'keywords': ['palm4u'],
    'links': [{
        'type': 'text/html',
        'rel': 'about',
        'title': 'information',
        'href': 'https://example.org/process',
        'hreflang': 'en-US'
    }],
    'inputs': {
        'area': {
            'title': 'Input Polygon',
            'description': 'The input polygon as a GeoJSON polygon geometry (type "Polygon") in UTM32.',
            'schema': {
                'type': 'object',
                'contentMediaType': 'application/geo+json'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'keywords': ['geometry']
        },
        'model_id': {
            'title': 'Model ID',
            'description': 'The ID of the Palm4U model to use.',
            'schema': {
                'type': 'string'
            },
            'minOccurs': 1,
            'maxOccurs': 1,
            'keywords': ['model']
        }
    },
    'outputs': {
        'resultZip': {
            'title': 'Result ZIP',
            'description': 'A ZIP file containing all output files.',
            'schema': {
                'type': 'string',
                'contentMediaType': 'application/zip'
            },
        },
    },
    'example': {
        'inputs': {
            'area': {
                'coordinates': [
                    [
                        [
                            481796.562881476,
                            5729013.938524413
                        ],
                        [
                            483209.4371185239,
                            5729013.938524413
                        ],
                        [
                            483209.4371185239,
                            5730252.187855759
                        ],
                        [
                            481796.562881476,
                            5730252.187855759
                        ],
                        [
                            481796.562881476,
                            5729013.938524413
                        ]
                    ]
                ],
                'type': 'Polygon'
            },
            'model_id': 'example_model_id'
        }
    }
}

class Palm4UPreprocessor(BaseProcessor):
    """Palm4U Preprocessor
    Configuration:
      processor:
        name: palm_4u_preprocessor_oap.palm_4u_preprocessor.Palm4UPreprocessor
        args:
          udt2palm: # optional udt2palm configuration. All paths must be absolute. Defaults below.
            exec_path: '/app' # Path from where udt2palm should be called.
            out_dir: '/app/data/output/' # Directory in which the process outputs will be stored.
            config_path: '/app/config/config.example.json' # Path to the process config.
          models: # optional list of supported models. Defaults to ['A']
            - A
          min_area_sqm: 1000000 # minimum area for running process. Defaults to 1000000
          max_area_sqm: 25000000 # maximum area for running process. Defaults to 25000000
          restrict_to: # GeoJSON (Multi-)Polygon in which the area must be located.
    """

    def __init__(self, processor_def, outputs=None):
        super().__init__(processor_def, PROCESS_METADATA)
        self.udt2palm = processor_def.get('args', {}).get('udt2palm', {
            'exec_path': '/app',
            'out_dir': '/app/data/output/',
            'config_path': '/app/config/config.example.json'
        })
        self.models = processor_def.get('args', {}).get('models', ['A'])
        self.min_area_sqm = processor_def.get('args', {}).get('min_area_sqm', 1000000)
        self.max_area_sqm = processor_def.get('args', {}).get('max_area_sqm', 25000000)
        self.restrict_to = processor_def.get('args', {}).get('restrict_to')

    def execute(self, data, outputs=None):
        """
        :param data: JSON input data that includes geometry.
        :returns: Tuple (mimetype, produced_outputs)
        """
        mime_type = 'application/zip'
        LOGGER.info("producing udt2palm output")

        self.validate_input(data)
        timestamp = datetime.now(timezone.utc).timestamp()
        output_dir = f'{self.udt2palm.get('out_dir').rstrip('/')}/{str(int(timestamp * 1000))}'
        config_dir = self.udt2palm.get('config_path')
        model_id = data.get('model_id')
        area = data.get('area')
        produced_outputs = run_udt2palm(output_dir, config_dir, model_id, area, self.udt2palm.get('exec_path'))

        if produced_outputs is None:
            raise ProcessorExecuteError("Execution failed.")

        return mime_type, produced_outputs

    def __repr__(self):
        return f'<Palm4UPreprocessor> {self.name}'

    def validate_input(self, data):
        model_id = data.get('model_id')
        self.validate_model_id(model_id)
        area = data.get('area')
        self.validate_area(area)

    def validate_model_id(self, model_id):
        if not model_id:
            raise ProcessorExecuteError("Required input parameter 'model_id' missing.")
        if not model_id in self.models:
            raise ProcessorExecuteError(f"Invalid value for input parameter 'model_id': {model_id}. Supported models: {str(self.models)}.")

    def validate_area(self, area):
        if not area:
            raise ProcessorExecuteError("Required input parameter 'area' missing.")

        area_pol = polygons(area.get('coordinates'))[0]
        if not isinstance(area_pol, Polygon):
            raise ProcessorExecuteError("Invalid geometry: area must be a Polygon.")

        if not area_pol.is_valid:
            raise ProcessorExecuteError("Invalid geometry.")

        area_bbox = area_pol.bounds
        area_bbox_pol = Polygon.from_bounds(*area_bbox)
        if not area_pol.equals(area_bbox_pol):
            raise ProcessorExecuteError("Invalid geometry: area must be a rectangle.")

        if area_pol.area < self.min_area_sqm:
            raise ProcessorExecuteError(f"Area too small: {area_pol.area} sqm. Minimum: {self.min_area_sqm} sqm.")

        if area_pol.area > self.max_area_sqm:
            raise ProcessorExecuteError(f"Area too large: {area_pol.area} sqm. Maximum: {self.max_area_sqm} sqm.")

        if self.restrict_to is not None:
          restricted_area = shape(self.restrict_to)
          if not area_pol.within(restricted_area):
              raise ProcessorExecuteError(f"Invalid geometry: area must lie within {str(self.restrict_to)}")
