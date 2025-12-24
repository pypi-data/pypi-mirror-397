#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import datetime
import tempfile
import os.path

from lxml import etree

import snowprofile.io.mf_bdclim

_here = os.path.dirname(os.path.realpath(__file__))

try:
    from snowprofile.io.mf_bdclim import _mf_conn
    _c = _mf_conn(connect_timeout=1)
    _c.close()
    SKIP = False
except Exception:
    SKIP = True


class TestIOMFBdClim(unittest.TestCase):

    @unittest.skipIf(SKIP, 'Database not available')
    def test_search_mf_bdclim_dates(self):
        l_dates = snowprofile.io.mf_bdclim.search_mf_bdclim_dates('38472401', '2023', '2024')
        assert len(l_dates) > 0
        last_year = str(datetime.datetime.now().year - 1)
        l_dates = snowprofile.io.mf_bdclim.search_mf_bdclim_dates('38472401', last_year)

    @unittest.skipIf(SKIP, 'Database not available')
    def test_read_mf_bdclim(self):
        x = snowprofile.io.mf_bdclim.read_mf_bdclim('38472401', date=datetime.datetime(2024, 12, 18, 10, 30))
        assert x.profile_depth == 0.37
        assert x.weather.air_temperature == 12.8
        assert len(x.stratigraphy_profile.data) == 6

        # case of non-existing observation
        try:
            x = snowprofile.io.mf_bdclim.read_mf_bdclim('38472401', date=datetime.datetime(2024, 12, 18, 10, 0))
        except ValueError as e:
            assert str(e) == 'Could not find data at date 2024-12-18 10:00:00'

    @unittest.skipIf(SKIP, 'Database not available')
    def test_write_caaml6_xml_example4_v605(self):
        """
        Test Profile 4: A profile with exotic things not present in test 3
        Write in CAAML 6.0.5 version
        """
        sp = snowprofile.io.mf_bdclim.read_mf_bdclim('38472401', date=datetime.datetime(2025, 1, 14, 12, 0))

        with tempfile.TemporaryDirectory(prefix='snowprofiletests') as dirname:
            filename = os.path.join(dirname, 'testcaaml.caaml')
            snowprofile.io.write_caaml6_xml(sp, filename, version='6.0.5')

            # Test CAAML6 validity
            xmlschema_path = os.path.join(_here, 'resources', 'CAAMLv6.0.5_SnowProfileIACS.xsd')
            xmlschema_doc = etree.parse(xmlschema_path)
            xmlschema = etree.XMLSchema(xmlschema_doc)

            xml_doc = etree.parse(filename)
            result = xmlschema.validate(xml_doc)
            assert result, f'Invalid CAAML output:\n{xmlschema.error_log}'

            # Reread written CAAML6 file
            sp_reread = snowprofile.io.read_caaml6_xml(filename)


if __name__ == "__main__":
    unittest.main()
