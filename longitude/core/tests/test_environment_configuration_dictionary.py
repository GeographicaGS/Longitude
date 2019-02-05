from unittest import TestCase, mock
from longitude.core.common.config import EnvironmentConfiguration as Config

fake_environment = {
    'LONGITUDE__PARENT__CHILD__VALUE_A': '42',
    'LONGITUDE__PARENT__CHILD__VALUE_B': 'wut',
    'LONGITUDE__VALUE_A': '8008'
}


@mock.patch.dict('longitude.core.common.config.os.environ', fake_environment)
class TestConfigurationDictionary(TestCase):

    def test_existing_values_return_strings_or_integers(self):
        self.assertEqual(42, Config.get('parent.child.value_a'))
        self.assertEqual('wut', Config.get('parent.child.value_b'))
        self.assertEqual(8008, Config.get('value_a'))

    def test_non_existing_values_return_none(self):
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
        self.assertEqual(fake_config, Config.get())
        self.assertEqual(fake_config['parent']['child'], Config.get('parent.child'))
