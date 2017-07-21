from __future__ import (absolute_import, division, print_function)

import datetime
import json
import logging
import pytz
import os


from lxml import objectify
from suds.client import Client


def parse_xml(xml):
    termarr = []
    root = objectify.XML(xml)
    for r in root.Records.getchildren():
        if root.tag == 'GetSpatialReferencesResponse':
            termarr.append(r.SRSName.text)
        elif root.tag == 'GetUnitsResponse':
            termarr.append(r.UnitsType.text)
        else:
            termarr.append(r.Term.text)

    return list(set(termarr))


def update_watermlcvs():
    WSDL_URL = 'http://his.cuahsi.org/odmcv_1_1/odmcv_1_1.asmx?WSDL'

    work_dir = os.path.abspath(os.path.curdir)

    try:
        CLIENT = Client(url=WSDL_URL)

        watermlcvs = {
            'updated': datetime.datetime.now(pytz.utc).isoformat(),
            'controlled_vocab': {
                'datatype': parse_xml(CLIENT.service.GetDataTypeCV()),
                'unitstype': parse_xml(CLIENT.service.GetUnits()),
                'samplemedium': parse_xml(CLIENT.service.GetSampleMediumCV()),
                'generalcategory': parse_xml(CLIENT.service.GetGeneralCategoryCV()),
                'valuetype': parse_xml(CLIENT.service.GetValueTypeCV()),
                'censorcode': parse_xml(CLIENT.service.GetCensorCodeCV())
            }
        }

        json.dump(watermlcvs, open(os.path.join(work_dir, 'watermlcvs.json'), 'wb'))
        print('Success WaterML 1.1 Controlled Vocabularies has been updated.')
    except:
        print('Can\'t connect to CUAHSI Service, controlled vocabularies are not updated.')


def get_waterml_cvs(): return json.load(open(os.path.join(os.path.abspath(os.path.curdir),
                                                          'watermlcvs.json'), 'rb'))


def check_dataTypeEnum(datatype):
    default = "Unknown"
    valueList = get_waterml_cvs()['controlled_vocab']['datatype']
    # valueList = [
    #     "Continuous",
    #     "Instantaneous",
    #     "Cumulative",
    #     "Incremental",
    #     "Average",
    #     "Maximum",
    #     "Minimum",
    #     "Constant Over Interval",
    #     "Categorical",
    #     "Best Easy Systematic Estimator ",
    #     "Unknown",
    #     "Variance",
    #     "Median",
    #     "Mode",
    #     "Best Easy Systematic Estimator",
    #     "Standard Deviation",
    #     "Skewness",
    #     "Equivalent Mean",
    #     "Sporadic",
    #     "Unknown",
    # ]
    if datatype is None:
        logging.warn('Datatype is not specified')
        return default
    if (datatype in valueList):
        return datatype
    else:
        logging.warn('value outside of enum for datatype ' + datatype)
        return default


def check_UnitsType(UnitsType):
    default = "Dimensionless"
    valueList = get_waterml_cvs()['controlled_vocab']['unitstype']
    # valueList = [
    #     "Angle",
    #     "Area",
    #     "Dimensionless",
    #     "Energy",
    #     "Energy Flux",
    #     "Flow",
    #     "Force",
    #     "Frequency",
    #     "Length",
    #     "Light",
    #     "Mass",
    #     "Permeability",
    #     "Power",
    #     "Pressure/Stress",
    #     "Resolution",
    #     "Scale",
    #     "Temperature",
    #     "Time",
    #     "Velocity",
    #     "Volume",
    # ]
    if UnitsType is None:
        logging.warn('UnitsType is not specified ')
        return default
    if (UnitsType in valueList):
        return UnitsType
    else:
        logging.warn('value outside of enum for UnitsType ' + UnitsType)
        return default


def check_SampleMedium(SampleMedium):
    default = "Unknown"
    valueList = get_waterml_cvs()['controlled_vocab']['samplemedium']
    # valueList = [
    #     "Surface Water",
    #     "Ground Water",
    #     "Sediment",
    #     "Soil",
    #     "Air",
    #     "Tissue",
    #     "Precipitation",
    #     "Unknown",
    #     "Other",
    #     "Snow",
    #     "Not Relevant",
    # ]
    if SampleMedium is None:
        logging.warn('SampleMedium is not specified')
        return default
    if (SampleMedium in valueList):
        return SampleMedium
    else:
        logging.warn('default returned: value outside of enum for SampleMedium ' + SampleMedium)  # noqa
        return default


def check_generalCategory(generalCategory):
    default = "Unknown"
    valueList = get_waterml_cvs()['controlled_vocab']['generalcategory']
    # valueList = [
    #     "Water Quality",
    #     "Climate",
    #     "Hydrology",
    #     "Geology",
    #     "Biota",
    #     "Unknown",
    #     "Instrumentation",
    # ]
    if generalCategory is None:
        logging.warn('GeneralCategory is not specified')
        return default
    if (generalCategory in valueList):
        return generalCategory
    else:
        logging.warn('default returned: value outside of enum for generalCategory ' + generalCategory)  # noqa
        return default


def check_valueType(valueType):
    default = "Unknown"
    valueList = get_waterml_cvs()['controlled_vocab']['valuetype']
    # valueList = [
    #     "Field Observation",
    #     "Sample",
    #     "Model Simulation Result",
    #     "Derived Value",
    #     "Unknown",
    # ]
    if valueType is None:
        logging.warn('ValueType is not specified')
        return default
    if (valueType in valueList):
        return valueType
    else:
        logging.warn('default returned: value outside of enum for valueType ' + valueType)  # noqa
        return default


def check_censorCode(censorCode):
    default = "nc"
    valueList = get_waterml_cvs()['controlled_vocab']['censorcode']
    # valueList = [
    #     "lt",
    #     "gt",
    #     "nc",
    #     "nd",
    #     "pnq",
    # ]
    if (censorCode in valueList):
        return censorCode
    else:
        return default


def check_QualityControlLevel(QualityControlLevel):
    default = "Unknown"
    valueList = [
        "Raw data",
        "Quality controlled data",
        "Derived products",
        "Interpreted products",
        "Knowledge products",
        "Unknown",
    ]
    if (QualityControlLevel in valueList):
        return QualityControlLevel
    else:
        return default