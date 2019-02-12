from unittest import TestCase, mock

from longitude.core.common.config import EnvironmentConfiguration as Config


class TestConfigurationDictionary(TestCase):

    def test_existing_values_return_strings_or_integers(self):
        fake_environment = {
            'LONGITUDE__PARENT__CHILD__VALUE_A': '42',
            'LONGITUDE__PARENT__CHILD__VALUE_B': 'wut',
            'LONGITUDE__VALUE_A': '8008'
        }
        with mock.patch.dict('longitude.core.common.config.os.environ', fake_environment):
            Config.config = None  # To ensure that environment will be loaded
            self.assertEqual(42, Config.get('parent.child.value_a'))
            self.assertEqual('wut', Config.get('parent.child.value_b'))
            self.assertEqual(8008, Config.get('value_a'))
            self.assertEqual(None, Config.get('wrong_value'))
            self.assertEqual(None, Config.get('wrong_parent.child.value'))
            self.assertEqual(None, Config.get('parent.wrong_child.value'))
            self.assertEqual(None, Config.get('parent.child.wrong_value'))
            self.assertEqual(None, Config.get('parent.wrong_child'))

    def test_existing_nested_values_return_dictionaries(self):
        fake_config = {
            'parent':
                {'child':
                    {
                        'value_a': 42,
                        'value_b': 'wut'
                    }
                },
            'value_a': 8008
        }
        with mock.patch('longitude.core.common.config.EnvironmentConfiguration.config', fake_config):
            self.assertEqual(42, Config.get('parent.child.value_a'))
