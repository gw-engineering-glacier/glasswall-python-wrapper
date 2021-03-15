

import unittest

from glasswall.content_management.errors.switches import RestrictedValue
from glasswall.content_management.switches.switch import Switch


class TestSwitch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.switch_embedded_images_allow = Switch(
            name="embedded_images",
            value="allow",
            restrict_values=["allow", "disallow", "sanitise"]
        )

        self.switch_custom_with_attributes = Switch(
            name="custom",
            value="sanitise",
            attributes={"a": "1", "b": "2"}
        )

    def tearDown(self):
        pass

    def test_text___no_attributes___text_matches_expected(self):
        self.assertEqual(
            self.switch_embedded_images_allow.text,
            '<embedded_images>allow</embedded_images>'
        )

    def test_text___with_attributes___text_matches_expected(self):
        # text writes attributes in alphabetical order, lowercase (key, value)
        self.assertEqual(
            self.switch_custom_with_attributes.text,
            '<custom a="1" b="2">sanitise</custom>'
        )

    def test_value___change_value_to_disallow___text_shows_value_as_disallow(self):
        self.switch_custom_with_attributes.value = "disallow"
        self.assertEqual(
            self.switch_custom_with_attributes.text,
            '<custom a="1" b="2">disallow</custom>'
        )

    def test_restrict_values___change_value_within_restrict_values___text_shows_value_as_disallow(self):
        self.switch_embedded_images_allow.value = "disallow"
        self.assertEqual(
            self.switch_embedded_images_allow.text,
            '<embedded_images>disallow</embedded_images>'
        )

    def test_restrict_values___change_value_outside_restrict_values___raises_RestrictedValue(self):
        with self.assertRaises(RestrictedValue):
            self.switch_embedded_images_allow.value = "splat"

    def test_repr___matches_expected(self):
        self.assertEqual(
            repr(self.switch_embedded_images_allow),
            'Switch("embedded_images", "allow")'
        )

    def test_lt___sort_list_of_switches___ordered_by_name_then_value(self):
        L = [
            Switch(
                name="b",
                value="allow",
            ),
            Switch(
                name="c",
                value="allow",
            ),
            Switch(
                name="c",
                value="sanitise",
            ),
            Switch(
                name="a",
                value="disallow",
            ),
            Switch(
                name="B",
                value="disallow",
            ),
        ]

        L.sort()

        self.assertEqual(
            str(L),
            '[Switch("a", "disallow"), Switch("b", "allow"), Switch("B", "disallow"), Switch("c", "allow"), Switch("c", "sanitise")]'
        )


if __name__ == "__main__":
    unittest.main()
