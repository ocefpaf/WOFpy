from __future__ import (absolute_import, division, print_function)

import io
import os
import unittest

from lxml import etree, objectify

from test_dao_1_1 import TestDao

from wof import WOF_1_1 as WOF
import wof.vocabularies

TEST_CONFIG_FILE = 'test_config.cfg'
TEST_XML_DIR = 'test_xml'

NSDEF = 'xmlns:gml="http://www.opengis.net/gml" \
    xmlns:xlink="http://www.w3.org/1999/xlink" \
    xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
    xmlns:wtr="http://www.cuahsi.org/waterML/" \
    xmlns="http://www.cuahsi.org/waterML/1.1/"'


class TestWOF(unittest.TestCase):
    """
    Tests wof response generation methods for validation against
    the WaterML 1.1 schema.
    """

    def setUp(self):
        dao = TestDao()
        testConfig = os.path.join(os.path.dirname(__file__), TEST_CONFIG_FILE)
        self.wof_inst = WOF(dao, testConfig)

        if not os.path.exists(os.path.join(os.path.abspath(os.path.curdir), 'watermlcvs.json')):
            wof.vocabularies.update_watermlcvs()

        waterml_schema_path = os.path.join(
            os.path.dirname(__file__),
            'cuahsiTimeSeries_v1_1.xsd'
        )
        waterml_schema_doc = etree.parse(waterml_schema_path)
        self.waterml_schema = etree.XMLSchema(waterml_schema_doc)

    def response_to_StringIO(self, response, root_name):
        """
        Converts WOF method response to StringIO object.
        """
        response_output = io.StringIO()
        response.export(response_output, 0, name_=root_name,
                        namespacedef_=NSDEF)

        return response_output.getvalue()

    def save_response(self, response, filename, root_name):
        f = open(filename, 'w')
        response.export(f, 0, name_=root_name,
                        namespacedef_=NSDEF)
        f.close()

    # Preserved in case in the future will do xml comparison test for WaterML 1.1.
    # def compare_output_to_known_xml(self,
    #                                 response_stringIO,
    #                                 known_xml_filename):
    #     """
    #     Make sure response output is as expected. This tests that a
    #     response contains the same XML as in the known XML file.
    #     """
    #     known_file_path = os.path.join(os.path.dirname(__file__),
    #                                    TEST_XML_DIR, known_xml_filename)
    #     # Use objectify and etree to remove whitespace from XML for comparison
    #     response_tree = objectify.fromstring(response_stringIO)
    #     print('---------------------')
    #     try:
    #         print(response_tree.queryInfo.creationTime)
    #         response_tree.queryInfo.creationTime = 'dateTime'
    #     except:
    #         pass
    #     known_tree = objectify.parse(known_file_path)
    #     response_string = etree.tostring(response_tree)
    #     known_string = etree.tostring(known_tree)
    #     # print(response_string)
    #     assert response_string == known_string

    def test_get_all_sites(self):
        response = self.wof_inst.create_get_site_response()
        response_string = self.response_to_StringIO(response,
                                                    'sitesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_all_sites_1_1.xml')

    def test_get_one_site(self):
        response = self.wof_inst.create_get_site_response(
            'TEST:SITE_A')
        response_string = self.response_to_StringIO(response,
                                                    'sitesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_one_site_1_1.xml')

    def test_get_multiple_sites(self):
        response = self.wof_inst.create_get_site_response(
            'TEST:SITE_A,TEST:SITE_B')
        response_string = self.response_to_StringIO(response,
                                                    'sitesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_multiple_sites_1_1.xml')

    def test_get_all_variables(self):
        response = self.wof_inst.create_get_variable_info_response()
        response_string = self.response_to_StringIO(response,
                                                    'variablesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_all_variables_1_1.xml')

    def test_get_one_variable(self):
        response = self.wof_inst.create_get_variable_info_response(
            'TESTVocab:Temp')
        response_string = self.response_to_StringIO(response,
                                                    'variablesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_one_variable_1_1.xml')

    def test_get_multiple_variables(self):
        response = self.wof_inst.create_get_variable_info_response(
            'TESTVocab:Flow,TESTVocab:TP')
        response_string = self.response_to_StringIO(response,
                                                    'variablesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_multiple_variables_1_1.xml')

    def test_get_site_info_novar(self):
        response = self.wof_inst.create_get_site_info_response('TEST:SITE_A')
        response_string = self.response_to_StringIO(response,
                                                    'sitesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_siteinfo_novar_1_1.xml')

    def test_get_site_info_withvar(self):
        response = self.wof_inst.create_get_site_info_response(
            'TEST:SITE_B',
            'TESTVocab:TP')
        response_string = self.response_to_StringIO(response,
                                                    'sitesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_siteinfo_withvar_1_1.xml')

    def test_get_values_encloses_por(self):
        response = self.wof_inst.create_get_values_response(
            'TEST:SITE_A',
            'TESTVocab:Temp',
            startDateTime='2007-03-05 00:00',
            endDateTime='2007-05-06 00:00')
        response_string = self.response_to_StringIO(response,
                                                    'timeSeriesResponse')

        assert response_string != None
        # self.compare_output_to_known_xml(response_string,
        #                                  'get_values_encloses_por_1_1.xml')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestWOF))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
