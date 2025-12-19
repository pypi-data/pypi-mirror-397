#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO
import copy
import uuid
from typing import Union

from esdl import esdl, PhysicalQuantityEnum
from esdl.units.conversion import equals

unitdict = {
    'NONE': '-',
    'AMPERE': 'A',
    'JOULE': 'J',
    'WATTHOUR': 'Wh',
    'WATT': 'W',
    'VOLT': 'V',
    'BAR': 'bar',
    'PSI': 'psi',
    'DEGREES_CELSIUS': '\u2103',  # Sign for degrees Celcius
    'KELVIN': 'K',
    'GRAM': 'g',
    'TONNE': 't',
    'EURO': 'EUR',
    'DOLLAR': 'USD',
    'METRE': 'm',
    'SQUARE_METRE': 'm2',
    'CUBIC_METRE': 'm3',
    'LITRE': 'l',
    'WATTSECOND': 'Ws',
    'ARE': 'a',
    'HECTARE': 'ha',
    'PERCENT': '%',
    'VOLT_AMPERE': 'VA',
    'VOLT_AMPERE_REACTIVE': 'VAR',
    'PASCAL': 'Pa',
    'NEWTON': 'N',
    'DEGREES': '\u00b0',  # Sign for degrees
    'HOUR': 'h'
}


timeunitdict = {
    'SECOND': 'sec',
    'MINUTE': 'min',
    'QUARTER': '15mins',
    'HOUR': 'hr',
    'DAY': 'day',
    'WEEK': 'wk',
    'MONTH': 'mon',
    'YEAR': 'yr'
}


multiplierdict = {
    'ATTO': 'a',
    'FEMTO': 'f',
    'PICO': 'p',
    'NANO': 'n',
    'MICRO': 'u',
    'MILLI': 'm',
    'KILO': 'k',
    'MEGA': 'M',
    'GIGA': 'G',
    'TERA': 'T',
    'TERRA': 'T',       # due to spelling mistake in ESDL
    'PETA': 'P',
    'EXA': 'E'
}


def qau_to_string(qau):
    """
    Converts a QuantityAndUnit instance to a string, for example "POWER in MW".

    :param qau: an esdl.QuantityAndUnit instance
    :result: string representation of the QuanityAndUnit instance
    """
    s = qau.physicalQuantity.name
    str_unit = unit_to_string(qau)
    if str_unit != '':
        s += ' in ' + str_unit

    return s


def unit_to_string(qau):
    """
    Converts the unit of a QuantityAndUnit instance to a string, for example "MW".

    :param qau: an esdl.QuantityAndUnit instance
    :result: string representation of the unit only of the QuanityAndUnit instance
    """
    mult = qau.multiplier.name
    unit = qau.unit.name
    pmult = qau.perMultiplier.name
    punit = qau.perUnit.name
    ptunit = qau.perTimeUnit.name

    s = ''

    if unit != 'NONE' and unit != 'UNDEFINED':
        if mult != 'NONE' and mult != 'UNDEFINED':
            s += multiplierdict[mult]
        try:
            s += unitdict[unit]
        except KeyError:
            s += unit
    if punit != 'NONE' and punit != 'UNDEFINED':
        s += '/'
        if pmult != 'NONE' and pmult != 'UNDEFINED':
            s += multiplierdict[pmult]
        try:
            s += unitdict[punit]
        except KeyError:  # SECOND etc is not in the dict
            s += punit
    if ptunit != 'NONE' and ptunit != 'UNDEFINED':
        s += '/' + timeunitdict[ptunit]

    return s


def build_qau_from_unit_string(unit_string: str, physical_quantity: esdl.PhysicalQuantityEnum = None):
    """
    Build an esdl.QuantityAndUnit instance from a string representing only the unit (and not the physical quantity),
    for example from "kWh/yr".

    :param unit_string: string representation of the QuanityAndUnit unit (without the physical quantity)
    :param physical_quantity: Optional sets the associated Physical quantity, e.g. esdl.PhysicalQuantityEnum.POWER
           or esdl.PhysicalQuantityEnum.ENERGY, esdl.PhysicalQuantityEnum.COST, also string version is supported, e.g.
           "Power", "Energy", "Cost" (case does not matter), but Python 3.10 does not like the
           esdl.PhysicalQuantityEnum | str definition in the method definition.
    :result: an esdl.QuantityAndUnit instance
    """

    qau = esdl.QuantityAndUnitType(id=str(uuid.uuid4()))

    if physical_quantity:
        if isinstance(physical_quantity, esdl.PhysicalQuantityEnum):
            qau.physicalQuantity = physical_quantity
        elif isinstance(physical_quantity, str):
            pq = esdl.PhysicalQuantityEnum.from_string(physical_quantity.upper())
            if pq:
                qau.physicalQuantity = pq

    unit_parts = unit_string.split('/')
    if unit_parts:
        # Parse the unit
        for u in unitdict:
            if unitdict[u] == unit_parts[0]:
                qau.unit = esdl.UnitEnum.from_string(u)
                break

        # if the first try failed, try to see if there is a multiplier in front of the unit
        if qau.unit == esdl.UnitEnum.NONE:
            unit = unit_parts[0][1:]
            for u in unitdict:
                if unitdict[u] == unit:
                    for m in multiplierdict:
                        if multiplierdict[m] == unit_parts[0][0]:
                            qau.unit = esdl.UnitEnum.from_string(u)
                            qau.multiplier = esdl.MultiplierEnum.from_string(m)
                            break
                    break

        # Zero, one or two 'perUnits' are possible
        if len(unit_parts) > 1:
            for up in range(1, len(unit_parts)):
                # Parse the perUnit
                for u in unitdict:
                    if unitdict[u] == unit_parts[up]:
                        qau.perUnit = esdl.UnitEnum.from_string(u)
                        break

                # if the first try failed, try to see if there is a multiplier in front of the perUnit
                if qau.perUnit == esdl.UnitEnum.NONE:
                    unit = unit_parts[up][1:]
                    for u in unitdict:
                        if unitdict[u] == unit:
                            for m in multiplierdict:
                                if multiplierdict[m] == unit_parts[up][0]:
                                    qau.perUnit = esdl.UnitEnum.from_string(u)
                                    qau.perMultiplier = esdl.MultiplierEnum.from_string(m)
                                    break
                            break

                # Parse the perTimeUnit
                for tu in timeunitdict:
                    if timeunitdict[tu] == unit_parts[up]:
                        qau.perTimeUnit = esdl.TimeUnitEnum.from_string(tu)
                        break

    return qau


def is_valid_uuid(uuid_to_test, version=4):
    """
    Check if uuid_to_test is a valid UUID.

    Parameters
    ----------
    uuid_to_test : str
    version : {1, 2, 3, 4}

    Returns
    -------
    `True` if uuid_to_test is a valid UUID, otherwise `False`.

    Examples
    --------
    >>> is_valid_uuid('c9bf9e57-1685-4c89-bafb-ff5af830be8a')
    True
    >>> is_valid_uuid('c9bf9e58')
    False
    """

    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def instantiate_qau(orig_qau: esdl.QuantityAndUnitType):
    """
    Creates a new instance of a QuantityAndUnit instance by copying the contents and creating a new ID.

    :param orig_qau: an esdl.QuantityAndUnit instance used as template
    """
    qau = orig_qau.deepcopy()
    qau.id = str(uuid.uuid4())
    return qau


def get_or_create_global_qau_reference(es: esdl.EnergySystem, orig_qau: esdl.QuantityAndUnitType):
    """
    Finds a QuantityAndUnit instance in the global list of QuantityAndUnit instances in the EnergySystemInformation.
    It the QuantityAndUnit exists, a QuantityAndUnitReference is returned. If the QuantityAndUnit does not exist,
    it will be created and a QuantityAndUnitReference is returned. Must be used with the default QuantityAndUnits, like
    defined in conversion.py, like ENERGY_IN_PJ, COST_IN_MEur

    :param es: the EnergySystem instance
    :param orig_qau: a QuantityAndUnit instance from the list of QuantityAndUnit templates
    """
    esi = es.energySystemInformation
    if not esi:
        esi = es.energySystemInformation = esdl.EnergySystemInformation()

    qaus = esi.quantityAndUnits
    if not qaus:
        qaus = esi.quantityAndUnits = esdl.QuantityAndUnits(id=str(uuid.uuid4()), name="Global quantities and units")

    qau_ref = None
    for qau in qaus.quantityAndUnit:
        if equals(qau, orig_qau):
            qau_ref = esdl.QuantityAndUnitReference(reference=qau)

    if not qau_ref:
        new_qau = orig_qau.deepcopy()
        if is_valid_uuid(new_qau.id, 4):
            new_qau.id = str(uuid.uuid4())     # If the orig_qau had an UUID as ID, change it

        qaus.quantityAndUnit.append(new_qau)
        qau_ref = esdl.QuantityAndUnitReference(reference=new_qau)

    return qau_ref
