from unittest import TestCase, mock

from longitude.core.common.config import EnvironmentConfiguration as Config


class TestConfigurationDictionary(TestCase):

    def test_existing_values_return_strings_or_integers(self):
        fake_environment = {
            'LONGITUDE__PARENT__CHILD__VALUE_A': '42',
            'LONGITUDE__PARENT__CHILD__VALUE_B': 'wut',
            'LONGITUDE__VALUE_A': '8008',
            'LONGITUDE__BOOL_VALUE': '1',
            'LONGITUDE__FLOAT_VALUE': '3.1416',
            'LONGITUDE__BOOL_STRING_1': 'true',
            'LONGITUDE__BOOL_STRING_2': 'False',
            'LONGITUDE__BOOL_STRING_3': 'yes',
            'LONGITUDE__BOOL_STRING_4': 'no',
            'LONGITUDE__BOOL_STRING_5': 'Y',
            'LONGITUDE__BOOL_STRING_6': 'n',
        }
        with mock.patch.dict('longitude.core.common.config.os.environ', fake_environment):
            Config.config = None  # To ensure that environment will be loaded

            root_config = Config.get()
            root_config['custom'] = {
                'custom_value': 'you can add me!'
            }

            with self.assertLogs(level='WARNING') as test_log:
                self.assertEqual('you can add me!', Config.get('custom.custom_value'))
                self.assertEqual(42, Config.get('PARENT.child.value_a', default=2))
                self.assertEqual('42', Config.get('PARENT.child.value_a'))
                self.assertEqual('wut', Config.get('parent.CHILD.value_b'))
                self.assertEqual(8008, Config.get('value_A', default=0))
                self.assertEqual(True, Config.get('BOOL_VALUE', default=False))
                self.assertEqual(3.1416, Config.get('float_VALUE', default=0.0))
                self.assertTrue(Config.get('bool_string_1'))
                self.assertFalse(False, Config.get('bool_string_2'))
                self.assertTrue(Config.get('bool_string_3'))
                self.assertFalse(False, Config.get('bool_string_4'))
                self.assertTrue(Config.get('bool_string_5'))
                self.assertFalse(False, Config.get('bool_string_6'))

                self.assertEqual(None, Config.get('wrong_value'))
                self.assertEqual(None, Config.get('wrong_parent.child.value'))
                self.assertEqual(None, Config.get('parent.wrong_child.value'))
                self.assertEqual(None, Config.get('parent.child.wrong_value'))
                self.assertEqual(None, Config.get('parent.wrong_child'))
                self.assertEqual('default value', Config.get('tomato.melon.strawberry', default='default value'))

                log_prefix = 'WARNING:longitude.core.common.config:'
                expected_log = [
                    'Config key wrong_value not found and no default has been defined.',
                    'Config key wrong_parent.child.value not found and no default has been defined.',
                    'Config key parent.wrong_child.value not found and no default has been defined.',
                    'Config key parent.child.wrong_value not found and no default has been defined.',
                    'Config key parent.wrong_child not found and no default has been defined.',
                    'Using default value for config key tomato.melon.strawberry'
                ]
                expected_log = [log_prefix + l for l in expected_log]

                self.assertEqual(expected_log, test_log.output)

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
