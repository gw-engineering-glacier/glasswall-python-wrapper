

import inspect
import unittest

import glasswall
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

    def test_get_attributes(self):
        self.assertDictEqual(
            Policy.get_attributes({"one": "1", "@two": "2", "@three": "3"}),
            {"two": "2", "three": "3"}
        )

    def test_custom_editor_policy___switch_names_and_values_in_text(self):
        policy = glasswall.content_management.policies.Editor(
            config={
                "pdfConfig": {"a": "b"},
                "customConfig": {"customswitch": "customvalue"},
            }
        )

        self.assertTrue(policy.pdfConfig.a.value == "b")
        self.assertTrue(policy.customConfig.customswitch.value == "customvalue")

    def test_editor_custom_policy_with_attributes___attributes_set_and_not_included_as_switch(self):
        policy = glasswall.content_management.policies.Editor(
            config={
                "customConfig": {
                    "customswitch": "customvalue",
                    "@customattribute": "attributevalue",
                }
            }
        )

        # Attribute added correctly
        self.assertTrue(policy.customConfig.attributes.get("customattribute") == "attributevalue")

        # Attribute not added as switch
        self.assertTrue(not any(switch_name in policy.customConfig.get_switch_names() for switch_name in {"@customattribute", "customattribute"}))

    def test_editor_policy___getattr_missing_config_raises_AttributeError(self):
        policy = glasswall.content_management.policies.Editor(
            config={
                "customConfig": {
                    "customswitch": "customvalue",
                    "@customattribute": "attributevalue",
                }
            }
        )

        # getattr on missing config should raise AttributeError
        with self.assertRaises(AttributeError):
            policy.configNonexistant

        # getattr on missing switch should raise AttributeError
        with self.assertRaises(AttributeError):
            policy.customConfig.switchNonexistant

    def test_editor_policy___object_is_modifiable(self):
        policy = glasswall.content_management.policies.Editor(default="sanitise")

        # policy.pdfConfig.acroform.value should be sanitise
        self.assertTrue(policy.pdfConfig.acroform.value == "sanitise")

        # set policy.pdfConfig.acroform.value to allow
        policy.pdfConfig.acroform.value = "allow"

        # policy.pdfConfig.acroform.value should be allow
        self.assertTrue(policy.pdfConfig.acroform.value == "allow")

        # policy.pdfConfig.acroform.text should also be allow
        self.assertEqual(
            policy.pdfConfig.acroform.text,
            "<acroform>allow</acroform>"
        )

    def test_policies___sysconfig_default_is_not_a_switch(self):
        # 2021/08/12 - was a bug with sysConfig containing the switch `default="sanitise"`
        for policy_subclass in glasswall.content_management.policies.policy.Policy.__subclasses__():
            policy = getattr(glasswall.content_management.policies, policy_subclass.__name__)()

            if hasattr(policy, "sysConfig"):
                self.assertTrue("default" not in policy.sysConfig.get_switch_names())

    def test_policies___sysconfig_default_is_not_a_switch_after_sysConfig_modification(self):
        # 2021/09/28 - was a bug with sysConfig containing the switch `default="sanitise"` after being modified
        for policy_subclass in glasswall.content_management.policies.policy.Policy.__subclasses__():
            policy = getattr(glasswall.content_management.policies, policy_subclass.__name__)(config={"sysConfig": {"interchange_type": "sisl"}})

            if hasattr(policy, "sysConfig"):
                self.assertTrue("default" not in policy.sysConfig.get_switch_names())

    def test_archive_manager_custom_policy___attributes_and_switches_customisable(self):
        policy = glasswall.content_management.policies.ArchiveManager(
            default="sanitise",
            default_archive_manager="process",
            config={
                "archiveConfig": {
                    "@recursionDepth": 1,
                    "@customAttribute": "customValue",
                    "bmp": "no_action",
                    "doc": "discard",
                }
            }
        )

        # archiveConfig has recursionDepth attribute with value 1
        self.assertTrue(policy.archiveConfig.attributes.get("recursionDepth") == 1)

        # archiveConfig has customAttribute attribute with value customValue
        self.assertTrue(policy.archiveConfig.attributes.get("customAttribute") == "customValue")

        # archiveConfig bmp switch is set to no_action
        self.assertTrue(policy.archiveConfig.bmp.value == "no_action")

        # archiveConfig doc switch is set to discard
        self.assertTrue(policy.archiveConfig.doc.value == "discard")

    def test_word_search_custom_policy___textList_order_maintained(self):
        policy = glasswall.content_management.policies.WordSearch(
            default="allow",
            config={
                "textSearchConfig": {
                    "textList": [
                        {"name": "textItem", "switches": [
                            {"name": "text", "value": "password"},
                            {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                        ]},
                        {"name": "textItem", "switches": [
                            {"name": "text", "value": "abc"},
                            {"name": "textSetting", "@replacementChar": "!", "value": "redact"},
                        ]},
                        {"name": "textItem", "switches": [
                            {"name": "text", "value": "xyz"},
                            {"name": "textSetting", "@replacementChar": "X", "value": "redact"},
                        ]},
                    ]
                }
            }
        )

        # Order should be unchanged
        self.assertEqual(
            policy.textSearchConfig.textList.text,
            inspect.cleandoc("""
            <textList>
                <textItem>
                    <text>password</text>
                    <textSetting replacementChar="*">redact</textSetting>
                </textItem>
                <textItem>
                    <text>abc</text>
                    <textSetting replacementChar="!">redact</textSetting>
                </textItem>
                <textItem>
                    <text>xyz</text>
                    <textSetting replacementChar="X">redact</textSetting>
                </textItem>
            </textList>
            """)
        )

    def test_word_search_custom_policy___attributes_customisable(self):
        policy = glasswall.content_management.policies.WordSearch(
            default="allow",
            config={
                "textSearchConfig": {
                    "textList": [
                        {"name": "textItem", "switches": [
                            {"name": "text", "value": "password"},
                            {"name": "textSetting", "@replacementChar": "*", "value": "redact", "@customAttribute": "customValue"},
                        ]},
                    ]
                }
            }
        )

        # textSetting attributes are customisable
        self.assertTrue(policy.textSearchConfig.textList.subelements[0].switches[1].attributes.get("customAttribute") == "customValue")

        # replacementChar attribute exists
        self.assertTrue(policy.textSearchConfig.textList.subelements[0].switches[1].attributes.get("replacementChar") == "*")

    def test_policy_from_string___policy_strings_equal(self):
        policies_to_test = [
            glasswall.content_management.policies.ArchiveManager(
                default="sanitise",
                default_archive_manager="process",
                config={
                    "pdfConfig": {"embeddedImages": "disallow"},
                    "wordConfig": {"embeddedImages": "disallow"},
                    "archiveConfig": {
                        "@recursionDepth": "50",
                        "jpeg": "discard"
                    }
                }
            ),
            glasswall.content_management.policies.Editor(
                default="allow",
                config={
                    "sysConfig": {
                        "interchange_type": "sisl",
                        "interchange_pretty": "true",
                    },
                    "xlsConfig": {
                        "external_hyperlinks": "sanitise",
                        "internal_hyperlinks": "sanitise",
                    }
                },
            ),
            glasswall.content_management.policies.Rebuild(
                default="disallow",
                config={
                    "sysConfig": {
                        "interchange_type": "xml",
                        "interchange_pretty": "false",
                    },
                    "pdfConfig": {
                        "external_hyperlinks": "sanitise",
                        "internal_hyperlinks": "sanitise",
                    }
                },
            ),
            glasswall.content_management.policies.WordSearch(
                default="allow",
                config={
                    "textSearchConfig": {
                        "@libVersion": "core2",
                        "textList": [
                            {"name": "textItem", "switches": [
                                {"name": "text", "value": "password"},
                                {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                            ]},
                            {"name": "textItem", "switches": [
                                {"name": "text", "value": "email"},
                                {"name": "textSetting", "@replacementChar": "*", "value": "redact"},
                            ]},
                        ]
                    }
                }
            ),
            glasswall.content_management.policies.Policy(
                config={
                    "customConfig": {
                        "customSwitch1": "customValue1",
                        "customSwitch2": "customValue2",
                    },
                    "customConfig2": {
                        "customSwitch3": "customValue3",
                    }
                }
            )
        ]

        for policy in policies_to_test:
            # Create a new Policy object from the using the Policy.from_string method
            policy_from_string = glasswall.content_management.policies.Policy.from_string(policy.text)

            # The two policies should be equal
            self.assertTrue(policy.text == policy_from_string.text, msg=f"Policy texts not equal:\n{policy.text}\n{policy_from_string.text}")


if __name__ == "__main__":
    unittest.main()
