

import inspect
import unittest

from glasswall.content_management.config_elements.config_element import ConfigElement
from glasswall.content_management.errors.config_elements import ConfigElementNotFound
from glasswall.content_management.errors.switches import SwitchNotFound
from glasswall.content_management.policies.policy import Policy
from glasswall.content_management.switches.switch import Switch


class TestPolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.custom_policy = Policy(
            config_elements=[
                ConfigElement(
                    name="a",
                    switches=[
                        Switch(
                            name="b",
                            value="c",
                        ),
                        Switch(
                            name="d",
                            value="e",
                            attributes={"f": "g"},
                        )
                    ],
                ),
                ConfigElement(
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
                    ],
                ),
            ]
        )

        self.custom_policy_duplicates = Policy(
            config_elements=[
                ConfigElement(
                    name="a",
                    switches=[
                        Switch(
                            name="b",
                            value="c",
                        ),
                        Switch(
                            name="d",
                            value="e",
                            attributes={"f": "g"},
                        )
                    ],
                ),
                ConfigElement(
                    name="a",
                    switches=[
                        Switch(
                            name="b",
                            value="c",
                        ),
                        Switch(
                            name="embedded_images",
                            value="allow",
                        ),
                    ],
                ),
                ConfigElement(
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
                    ],
                ),
            ]
        )

    def tearDown(self):
        pass

    def test_text___custom_policy___text_matches_expected(self):
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_text___custom_policy_duplicates___text_matches_expected(self):
        self.assertEqual(
            self.custom_policy_duplicates.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <a>
                    <b>c</b>
                    <embedded_images>allow</embedded_images>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_encoded___return_matches_expected(self):
        self.assertEqual(
            self.custom_policy.encode(),
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """).encode("utf-8")
        )

    def test_get_config_element_names___no_duplicates___list_matches_expected(self):
        self.assertListEqual(
            self.custom_policy.get_config_element_names(),
            ["a", "pdfConfig"]
        )

    def test_get_config_element_names___with_duplicates___list_matches_expected(self):
        # Duplicate names not repeated
        self.assertListEqual(
            self.custom_policy_duplicates.get_config_element_names(),
            ["a", "pdfConfig"]
        )

    def test_remove_switch___config_element_not_found___raise_ConfigElementNotFound(self):
        with self.assertRaises(ConfigElementNotFound):
            self.custom_policy.remove_switch(config_element="splat", switch="asd")

    def test_remove_switch___switch_not_found___raise_SwitchNotFound(self):
        with self.assertRaises(SwitchNotFound):
            self.custom_policy.remove_switch(config_element="pdfConfig", switch="splat")

    def test_remove_switch___config_element_by_str_switch_by_str___switch_removed(self):
        self.custom_policy.remove_switch(config_element="pdfConfig", switch="embedded_images")

        # embedded_images no longer in config element "pdfConfig" switches
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_switch___config_element_by_str_switch_by_instance___switch_removed(self):
        switch_embedded_images = self.custom_policy.config_elements[1].switches[1]
        self.custom_policy.remove_switch(config_element="pdfConfig", switch=switch_embedded_images)

        # embedded_images no longer in config element "pdfConfig" switches
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_switch___config_element_by_instance_switch_by_str___switch_removed(self):
        config_element_pdfConfig = self.custom_policy.config_elements[1]
        self.custom_policy.remove_switch(config_element=config_element_pdfConfig, switch="embedded_images")

        # embedded_images no longer in config element "pdfConfig" switches
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_switch___config_element_by_instance_switch_by_instance___switch_removed(self):
        config_element_pdfConfig = self.custom_policy.config_elements[1]
        switch_embedded_images = self.custom_policy.config_elements[1].switches[1]
        self.custom_policy.remove_switch(config_element=config_element_pdfConfig, switch=switch_embedded_images)

        # embedded_images no longer in config element "pdfConfig" switches
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_switch___config_element_by_str_switch_by_str_with_duplicates___duplicates_switches_removed(self):
        # remove switch "embedded_images" from all config "a"
        self.custom_policy_duplicates.remove_switch(config_element="a", switch="embedded_images")

        # all config "a" no longer contain switch "embedded_images"
        self.assertEqual(
            self.custom_policy_duplicates.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <a>
                    <b>c</b>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_add_switch___config_element_by_str_not_found___raise_SwitchNotFound(self):
        # Try to add a switch to a ConfigElement with a .name of "splat" that does not exist in the custom policy
        with self.assertRaises(ConfigElementNotFound):
            self.custom_policy.add_switch(config_element="splat", switch=Switch(name="name", value="value"))

    def test_add_switch___config_element_by_instance_not_found___raise_SwitchNotFound(self):
        # Try to add a switch to a ConfigElement instance that does not exist in the custom policy
        with self.assertRaises(ConfigElementNotFound):
            self.custom_policy.add_switch(config_element=ConfigElement(name="name"), switch=Switch(name="name", value="value"))

    def test_add_switch___config_element_by_str___switch_added(self):
        self.custom_policy.add_switch(
            config_element="pdfConfig",
            switch=Switch(name="embedded_files", value="sanitise")
        )

        # The embedded_files switch has been added, and has overwritten the previous switches value of "disallow"
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>sanitise</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_add_switch___config_element_by_str_replace_False___switch_added(self):
        self.custom_policy.add_switch(
            config_element="pdfConfig",
            switch=Switch(name="embedded_files", value="sanitise"),
            replace=False
        )

        # The embedded_files switch has been appended, and has not overwritten the previous switch with a value of "disallow"
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_files>sanitise</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_add_switch___config_element_by_instance___switch_added(self):
        config_element_pdfConfig = self.custom_policy.config_elements[1]
        self.custom_policy.add_switch(
            config_element=config_element_pdfConfig,
            switch=Switch(name="embedded_files", value="sanitise")
        )

        # The embedded_files switch has been added, and has overwritten the previous switches value of "disallow"
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>sanitise</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_add_switch___config_element_by_instance_replace_False___switch_added(self):
        config_element_pdfConfig = self.custom_policy.config_elements[1]
        self.custom_policy.add_switch(
            config_element=config_element_pdfConfig,
            switch=Switch(name="embedded_files", value="sanitise"),
            replace=False
        )

        # The embedded_files switch has been appended, and has not overwritten the previous switch with a value of "disallow"
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_files>sanitise</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_config_element___config_element_by_str_config_element_not_found___raises_ConfigElementNotFound(self):
        # Try to remove a config element with a .name of "splat" that does not exist in the custom policy
        with self.assertRaises(ConfigElementNotFound):
            self.custom_policy.remove_config_element(config_element="splat")

    def test_remove_config_element___config_element_by_instance_config_element_not_found___raises_ConfigElementNotFound(self):
        # Try to remove a config element instance that does not exist in the custom policy
        with self.assertRaises(ConfigElementNotFound):
            self.custom_policy.remove_config_element(config_element=ConfigElement(name="splat"))

    def test_remove_config_element___config_element_by_str___config_element_removed(self):
        self.custom_policy.remove_config_element(config_element="pdfConfig")

        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
            </config>
            """)
        )

    def test_remove_config_element___config_element_by_str_with_duplicates___duplicate_config_element_removed(self):
        self.custom_policy_duplicates.remove_config_element(config_element="a")

        self.assertEqual(
            self.custom_policy_duplicates.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_remove_config_element___config_element_by_instance___config_element_removed(self):
        config_element_pdfConfig = self.custom_policy.config_elements[1]
        self.custom_policy.remove_config_element(config_element=config_element_pdfConfig)

        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
            </config>
            """)
        )

    def test_add_config_element___replace_True___config_element_added(self):
        self.custom_policy.add_config_element(config_element=ConfigElement(name="pdfConfig"))

        # The empty pdfConfig config element has been added, and has overwritten the previous pdfConfig config element
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                </pdfConfig>
            </config>
            """)
        )

    def test_add_config_element___replace_False___config_element_added(self):
        self.custom_policy.add_config_element(config_element=ConfigElement(name="pdfConfig"), replace=False)

        # The empty pdfConfig config element has been appended, and has not overwritten the previous pdfConfig config element
        self.assertEqual(
            self.custom_policy.text,
            inspect.cleandoc("""
            <?xml version="1.0" encoding="utf-8"?>
            <config>
                <a>
                    <b>c</b>
                    <d f="g">e</d>
                </a>
                <pdfConfig>
                </pdfConfig>
                <pdfConfig>
                    <embedded_files>disallow</embedded_files>
                    <embedded_images>allow</embedded_images>
                </pdfConfig>
            </config>
            """)
        )

    def test_get_attributes_from_dictionary(self):
        self.assertDictEqual(
            Policy.get_attributes_from_dictionary({"one": "1", "@two": "2", "@three": "3"}),
            {"two": "2", "three": "3"}
        )


if __name__ == "__main__":
    unittest.main()
