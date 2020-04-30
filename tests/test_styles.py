# -*- coding: utf-8 -*-

""" Test functions in styles.py.

License:
    Copyright 2020 The Cytoscape Consortium

    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
    documentation files (the "Software"), to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
    and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies or substantial portions
    of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
    WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
    OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import unittest
import re
from requests import RequestException

from test_utils import *


class StylesTests(unittest.TestCase):
    def setUp(self):
        try:
            py4cytoscape.delete_all_networks()
        except:
            pass

    def tearDown(self):
        pass

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_copy_visual_style(self):
        # Initialization
        load_test_session()

        # Verify that a new style can be added
        original_style_list = py4cytoscape.get_visual_style_names()
        res = py4cytoscape.copy_visual_style('Solid', 'SolidCopy')
        self.assertIsInstance(res, str)
        self.assertEqual(res, '')
        self.assertSetEqual(set(original_style_list) | {'SolidCopy'}, set(py4cytoscape.get_visual_style_names()))

        # Verify that the new style is the same as the old style
        original_style_props = py4cytoscape.get_style_all_mappings('Solid')
        new_style_props = py4cytoscape.get_style_all_mappings('Solid')
        self.assertListEqual(original_style_props, new_style_props)
        # TODO: Remember to compare defaults and dependencies, too

        # Verify that an invalid style name is caught
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.copy_visual_style, 'bogusStyle', 'bogusStyleCopy')
        self.assertRaises(RequestException, py4cytoscape.copy_visual_style, 'Solid', '')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_create_visual_style(self):
        # Initialization
        load_test_session()

        def check_new_style(style_name):
            new_style_props = py4cytoscape.get_style_all_mappings(style_name)
            indexed_properties = {prop['visualProperty']: prop for prop in new_style_props}
            self._check_property(indexed_properties['NODE_LABEL'], 'NODE_LABEL', 'COMMON', 'String', 'passthrough')
            self._check_property(indexed_properties['NODE_FILL_COLOR'], 'NODE_FILL_COLOR', 'Degree', 'Integer',
                                 'discrete', [{'key': '1', 'value': '#FF9900'}, {'key': '2', 'value': '#66AAAA'}])
            self._check_property(indexed_properties['EDGE_TARGET_ARROW_SHAPE'], 'EDGE_TARGET_ARROW_SHAPE',
                                 'interaction', 'String', 'discrete',
                                 [{'key': 'pp', 'value': 'ARROW'}, {'key': 'pd', 'value': 'T'}])
            self._check_property(indexed_properties['EDGE_WIDTH'], 'EDGE_WIDTH', 'EdgeBetweenness', 'Double',
                                 'passthrough')

        # Verify that creating a new style reports success
        defaults = {'NODE_SHAPE': 'diamond', 'NODE_SIZE': 30, 'EDGE_TRANSPARENCY': 120,
                    'NODE_LABEL_POSITION': 'W,E,c,0.00,0.00'}
        node_labels = py4cytoscape.map_visual_property('node label', 'COMMON', 'p')
        node_fills = py4cytoscape.map_visual_property('node fill color', 'Degree', 'd', ['1', '2'],
                                                      ['#FF9900', '#66AAAA'])
        arrow_shapes = py4cytoscape.map_visual_property('Edge Target Arrow Shape', 'interaction', 'd', ['pp', 'pd'],
                                                        ['Arrow', 'T'])
        edge_width = py4cytoscape.map_visual_property('edge width', 'EdgeBetweenness', 'p')
        res = py4cytoscape.create_visual_style('NewStyle', defaults=defaults,
                                               mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyle'})

        # Verify that the properties are correct
        check_new_style('NewStyle')

        # Verify that creating the same style again gives the same results, except a different name
        res = py4cytoscape.create_visual_style('NewStyle', defaults=defaults,
                                               mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyle_0'})
        check_new_style('NewStyle_0')

        # Create another style that has no defaults
        res = py4cytoscape.create_visual_style('NewStyleNoDefaults',
                                               mappings=[node_labels, node_fills, arrow_shapes, edge_width])
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyleNoDefaults'})
        check_new_style('NewStyleNoDefaults')

        # Create another style that has no defaults or mappings
        res = py4cytoscape.create_visual_style('NewStyleEmpty')
        self.assertIsInstance(res, dict)
        self.assertDictEqual(res, {'title': 'NewStyleEmpty'})
        self.assertListEqual(py4cytoscape.get_style_all_mappings('NewStyleEmpty'), [])

        # Verify that creating an invalid style returns an error
        node_fills = py4cytoscape.map_visual_property('node fill color', 'Degree', 'd', [1, 2], ['#FF9900', '#66AAAA'])
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.create_visual_style, 'BogusStyle', defaults=defaults,
                          mappings=[node_labels, node_fills, arrow_shapes, edge_width])

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_delete_visual_style(self):
        # Initialization
        load_test_session()

        # Verify that a new style can be added
        original_style_list = py4cytoscape.get_visual_style_names()
        self.assertEqual(py4cytoscape.copy_visual_style('Solid', 'SolidCopy'), '')
        self.assertSetEqual(set(original_style_list) | {'SolidCopy'}, set(py4cytoscape.get_visual_style_names()))

        # Verify that deleting the style results in the original style list
        self.assertEqual(py4cytoscape.delete_visual_style('SolidCopy'), '')
        self.assertSetEqual(set(original_style_list), set(py4cytoscape.get_visual_style_names()))

        # Verify that trying to delete a non-existent style fails
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.delete_visual_style, 'SolidCopy')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_export_import_visual_styles(self):
        # Initialization
        load_test_session()
        STYLE_FILE = 'test'
        STYLE_SUFFIX = ".xml"
        STYLE_SUFFIX_ALT = '.json'

        def check_write(style_file, style_suffix, use_file=True, use_suffix=True, type='XML'):
            full_file = style_file + style_suffix

            if not use_file:
                file = None
            elif use_suffix:
                file = full_file
            else:
                file = style_file

            if os.path.exists(full_file): os.remove(full_file)
            res = py4cytoscape.export_visual_styles(file, type=type)
            self.assertIsInstance(res, dict)
            self.assertIn('file', res)
            self.assertIsNotNone(re.search(style_suffix + '$', res['file'].lower()))
            self.assertTrue(os.path.exists(full_file))
            os.remove(res['file'])

        # Verify that a file name is assume if none is provided
        check_write('styles', STYLE_SUFFIX, use_file=False, use_suffix=False)

        # Verify that a file suffix is added if none is provided for a style file
        check_write(STYLE_FILE, STYLE_SUFFIX, use_suffix=False)

        # Verify that specifying a file suffix causes the file to be created
        check_write(STYLE_FILE, STYLE_SUFFIX, use_suffix=True)

        # Verify that specifying a file suffix causes the file to be created
        check_write(STYLE_FILE, STYLE_SUFFIX_ALT, use_suffix=False, type='json')
        check_write(STYLE_FILE, STYLE_SUFFIX_ALT, use_suffix=True, type='json')

        # TODO: Revisit this once Cytoscape fixes the 'styles=' parameter so it allows multiple styles
        # Create a file containing the default style (i.e., galFiltered Style)
        style_name_list = py4cytoscape.get_visual_style_names()
        self.assertIsInstance(style_name_list, list)
        res = py4cytoscape.export_visual_styles()
        all_file_name = res['file']

        # Verify that importing filters results in the expected filters ... first, remove all filters
        for style_name in set(py4cytoscape.get_visual_style_names()) - {'default'}:
            self.assertEqual(py4cytoscape.delete_visual_style(style_name), '')
        self.assertSetEqual(set(py4cytoscape.get_visual_style_names()), {'default'})
        self.assertListEqual(py4cytoscape.import_visual_styles(all_file_name), ['galFiltered Style'])
        self.assertSetEqual(set(py4cytoscape.get_visual_style_names()), {'default', 'galFiltered Style'})

        os.remove(all_file_name)

        # Verify that bogus files generate an exception
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.export_visual_styles, '\\impos:*sible\\path\\bogus')
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.import_visual_styles, '\\impos:*sible\\path\\bogus')

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_get_visual_style_names(self):
        # Initialization
        load_test_session()

        self.assertSetEqual(set(py4cytoscape.get_visual_style_names()),
                            {'Universe', 'Marquee', 'Big Labels', 'BioPAX_SIF', 'Ripple', 'Metallic', 'default black',
                             'galFiltered Style', 'Nested Network Style', 'Minimal', 'BioPAX', 'Solid', 'default',
                             'Custom Graphics Style', 'Directed', 'Sample1', 'Box'})

    #    @py4cytoscape.skip
    @py4cytoscape.print_entry_exit
    def test_set_visual_style(self):
        # Initialization
        load_test_session()

        # Verify that valid styles can be set
        self.assertDictEqual(py4cytoscape.set_visual_style('default'), {'message': 'Visual Style applied.'})
        self.assertDictEqual(py4cytoscape.set_visual_style('galFiltered Style'), {'message': 'Visual Style applied.'})

        # Verify that an error occurs for an invalid style
        self.assertRaises(py4cytoscape.CyError, py4cytoscape.set_visual_style, 'bogus style')

        self.assertRaises(py4cytoscape.CyError, py4cytoscape.set_visual_style, 'default', network='bogus network')


    def _check_property(self, cy_property, expected_property, expected_column, expected_column_type, expected_type,
                        expected_cargo=None):
        self.assertIsInstance(cy_property, dict)
        self.assertEqual(cy_property['mappingType'], expected_type)
        self.assertEqual(cy_property['mappingColumn'], expected_column)
        self.assertEqual(cy_property['mappingColumnType'], expected_column_type)
        self.assertEqual(cy_property['visualProperty'], expected_property)
        if expected_type == 'discrete':
            self.assertIsInstance(cy_property['map'], type(expected_cargo))
            self.assertListEqual(cy_property['map'], expected_cargo)
        elif expected_type == 'continuous':
            self.assertIsInstance(cy_property['points'], type(expected_cargo))
            self.assertListEqual(cy_property['points'], expected_cargo)
        else:
            self.assertEqual(len(cy_property), 4)  # passthrough or unknown


if __name__ == '__main__':
    unittest.main()