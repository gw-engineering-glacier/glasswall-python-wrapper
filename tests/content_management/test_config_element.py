

import inspect
import unittest

from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.switches.switch import Switch


class TestConfigElement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.config_element_pdfConfig = ConfigElement(
            name="pdfConfig",
            switches=[
                Switch(
                    name="embedded_files",
                    value="disallow",
                ),
                Switch(
                    name="embedded_images",
                    value="allow",
                ),
            ]
        )

        self.config_element_pdfConfig_duplicates = ConfigElement(
            name="pdfConfig",
            switches=[
                Switch(
                    name="embedded_files",
                    value="disallow",
                ),
                Switch(
                    name="embedded_images",
                    value="allow",
                ),
                Switch(
                    name="embedded_images",
                    value="allow",
                ),
            ]
        )

        self.config_element_textSearchConfig = ConfigElement(
            name="textSearchConfig",
            attributes={"libVersion": "core2"},
            subelements=[
                ConfigElement(
                    name="textList",
                    subelements=[
                        ConfigElement(
                            name="textItem",
                            switches=[
                                Switch(name="text", value="generic"),
                                Switch(name="textSetting", attributes={"replacementChar": "*"}, value="redact")
                            ]
                        ),
                    ]
                )
            ]
        )

    def tearDown(self):
        pass

    def test_text___config_element_pdfConfig___text_matches_expected(self):
        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
                <embedded_images>allow</embedded_images>
            </pdfConfig>
            """)
        )

    def test_text___with_attributes_and_subelements___text_matches_expected(self):
        self.assertEqual(
            self.config_element_textSearchConfig.text,
            inspect.cleandoc("""
            <textSearchConfig libVersion="core2">
                <textList>
                    <textItem>
                        <text>generic</text>
                        <textSetting replacementChar="*">redact</textSetting>
                    </textItem>
                </textList>
            </textSearchConfig>
            """)
        )

    def test_repr___config_element_pdfConfig___matches_expected(self):
        self.assertEqual(
            repr(self.config_element_pdfConfig),
            'ConfigElement("pdfConfig")'
        )

    def test_lt___sort_list_of_configs___ordered_by_name_then_switches(self):
        L = [
            ConfigElement(
                name="a",
                switches=[
                    Switch(
                        name="b",
                        value="allow",
                    )
                ],
            ),
            ConfigElement(
                name="a",
                switches=[
                    Switch(
                        name="c",
                        value="allow",
                    )
                ],
            ),
            ConfigElement(
                name="d",
                switches=[
                    Switch(
                        name="a",
                        value="allow",
                    )
                ],
            )
        ]

        L.sort()

        self.assertEqual(
            str(L),
            '[ConfigElement("a"), ConfigElement("a"), ConfigElement("d")]'
        )

        # First ConfigElement in list should be the one that contains a switch with the name 'b'
        self.assertTrue(
            L[0].switches[0].name == "b"
        )

    def test_get_switch_names___no_duplicates___list_matches_expected(self):
        self.assertListEqual(
            self.config_element_pdfConfig.get_switch_names(),
            ["embedded_files", "embedded_images"]
        )

    def test_get_switch_names___with_duplicates___list_matches_expected(self):
        # Duplicate names not repeated
        self.assertListEqual(
            self.config_element_pdfConfig_duplicates.get_switch_names(),
            ["embedded_files", "embedded_images"]
        )

    def test_remove_switch___by_str_name___switch_removed(self):
        self.config_element_pdfConfig.remove_switch("embedded_images")

        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
            </pdfConfig>
            """)
        )

    def test_remove_switch___by_str_name_multiple___multiple_switches_removed(self):
        # Removes both switches named "embedded_files"
        self.config_element_pdfConfig_duplicates.remove_switch("embedded_images")

        self.assertEqual(
            self.config_element_pdfConfig_duplicates.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
            </pdfConfig>
            """)
        )

    def test_remove_switch___by_instance___switch_removed(self):
        switch_embedded_files = self.config_element_pdfConfig.switches[0]
        self.config_element_pdfConfig.remove_switch(switch_embedded_files)

        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_images>allow</embedded_images>
            </pdfConfig>
            """)
        )

    def test_remove_switch___by_str_switch_not_in_switches_list___raises_SwitchNotFound(self):
        with self.assertRaises(SwitchNotFound):
            self.config_element_pdfConfig.remove_switch(switch="macros")

    def test_remove_switch___by_instance_switch_not_in_switches_list___raises_SwitchNotFound(self):
        s = Switch(name="a", value="b")

        with self.assertRaises(SwitchNotFound):
            self.config_element_pdfConfig.remove_switch(switch=s)

    def test_add_switch___switch_added(self):
        self.config_element_pdfConfig.add_switch(switch=Switch(name="macros", value="disallow"))

        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
                <embedded_images>allow</embedded_images>
                <macros>disallow</macros>
            </pdfConfig>
            """)
        )

    def test_add_switch___add_duplicate___switch_added_and_replaced(self):
        self.config_element_pdfConfig.add_switch(switch=Switch(name="embedded_files", value="disallow"))

        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
                <embedded_images>allow</embedded_images>
            </pdfConfig>
            """)
        )

    def test_add_switch___with_duplicate_and_replace_False___duplicate_switch_added(self):
        # Useful for adding multiple textItem ConfigElement's for textSearchConfig
        self.config_element_pdfConfig.add_switch(switch=Switch(name="macros", value="disallow"), replace=False)
        self.config_element_pdfConfig.add_switch(switch=Switch(name="macros", value="disallow"), replace=False)
        self.config_element_pdfConfig.add_switch(switch=Switch(name="macros", value="disallow"), replace=False)

        self.assertEqual(
            self.config_element_pdfConfig.text,
            inspect.cleandoc("""
            <pdfConfig>
                <embedded_files>disallow</embedded_files>
                <embedded_images>allow</embedded_images>
                <macros>disallow</macros>
                <macros>disallow</macros>
                <macros>disallow</macros>
            </pdfConfig>
            """)
        )


if __name__ == "__main__":
    unittest.main()
