from unittest import TestCase, mock
from longitude.core.common.config import EnvironmentConfiguration

fake_environment = {
    'PATATUELA_RULES': 'my_root_value'
}


class TestConfigurationDictionary(TestCase):

    @mock.patch.dict('longitude.core.common.config.os.environ', fake_environment)
    def test_base(self):
        d = EnvironmentConfiguration({
            'root_patatuela': '=PATATUELA_RULES',
            'patata': 'patata value',
            'potato': 'potato value',
            'potatoes': [
                'potato A', 'poteito B'
            ],
            'potato_sack': {
                'colour': 'meh',
                'taste': 'buah',
                'texture': {
                    'external': 'oh no',
                    'internal': 'omg',
                    'bumpiness': '=SOME_VALUE_FOR_BUMPINESS'
                }
            }
        })

        self.assertEqual('my_root_value', d['root_patatuela'])
        self.assertEqual('=SOME_VALUE_FOR_BUMPINESS [NOT FOUND]', d['potato_sack']['texture']['bumpiness'])
