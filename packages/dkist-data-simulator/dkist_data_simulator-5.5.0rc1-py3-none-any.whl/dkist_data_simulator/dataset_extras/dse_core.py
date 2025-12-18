from enum import StrEnum
from typing import Any
from dataclasses import dataclass

import numpy as np
from astropy.io import fits
from dkist_fits_specifications import dataset_extras

from dkist_data_simulator.dataset import Dataset
from dkist_data_simulator.schemas import Schema
from dkist_data_simulator.spec122 import KNOWN_INSTRUMENT_TABLES

__all__ = [
    "DatasetExtraName",
    "DatasetExtraTables",
    "InstrumentTables",
    "DatasetExtraBase",
    "DatasetExtraSchema",
]


class DatasetExtraTables(StrEnum):
    aggregate = "aggregate"
    atlas = "atlas"
    common = "common"
    fits = "fits"
    gos = "gos"
    ip_task = "ip_task"
    wavecal = "wavecal"


InstrumentTables = StrEnum("InstrumentTables", KNOWN_INSTRUMENT_TABLES)

common_schema = dataset_extras.load_full_dataset_extra("common")["common"]
extname_values = common_schema["EXTNAME"]["values"]
DatasetExtraName = StrEnum(
    "DatasetExtraName", {s.lower().replace(" ", "_"): s for s in extname_values}
)


@dataclass(init=False)
class DatasetExtraSchema(Schema):
    """
    A representation of the Dataset Extra schema.

    Parameters
    ----------
    instrument
        Member of `.InstrumentTables`.  If None, all instrument tables will be
        in the header.
    keep_schemas
        List of `.DatasetExtraTables` to keep in the headers.  If `None`, all
        dataset extra tables will be in the header.
    remove_instrument_table
        Set to true to remove the instrument table, relevant for certain
        reference dataset extras.  If True, no instrument tables will be
        in the header.
    random
        Instance of the Numpy random `Generator` class.  If None,
        `numpy.random.default_rng` is used.
    """

    def __init__(
        self,
        instrument: InstrumentTables | None = None,
        keep_schemas: list[DatasetExtraTables] | None = None,
        remove_instrument_table: bool = False,
        random=None,
        **other_header_values,
    ):
        random = random or np.random.default_rng()

        sections = dataset_extras.load_processed_dataset_extra(**other_header_values)
        sections.pop("compression", None)

        if instrument or remove_instrument_table:
            for inst_table in InstrumentTables:
                if inst_table != instrument or remove_instrument_table:
                    sections.pop(inst_table.name, None)
        if keep_schemas:
            for dse_table in DatasetExtraTables:
                if dse_table not in keep_schemas:
                    sections.pop(dse_table, None)

        super().__init__(self.sections_from_dicts(sections.values(), random=random))

        self.instrument = instrument
        if remove_instrument_table:
            self.instrument = None


class DatasetExtraBase(Dataset):
    """
    Generate a collection of FITS files for one instrument and one Dataset Extra type.

    Parameters
    ----------
    file_schema
        Instance of `.DatasetExtraSchema`, normally populated with instrument name
        and other specific tables for the Dataset Extra.
    dataset_extra_name
        Member of DatasetExtraName for the EXTNAME keyword.
    dataset_shape
        The full shape of the dataset.  For Dataset Extra files, this is normally
        ``(N, yshape, xshape)`` or ``(N, vshape)`` where ``N`` is the number of files
        to be generated and the remaining dimensions are the data size.
    array_shape
        The size of the data.  Because the dataset extras are not reconstructed into
        higher-dimensional arrays, they should not include dummy dimensions.  Arrays
        are ``(yshape, xshape)`` and vectors are ``(vshape)``.  Single values
        can be entered as ``(1,)``.
    """

    def __init__(
        self,
        file_schema: DatasetExtraSchema = DatasetExtraSchema(),
        dataset_extra_name: DatasetExtraName | None = None,
        dataset_shape: tuple[int, ...] = (2, 10, 10),
        array_shape: tuple[int, ...] = (10, 10),
        **additional_schema_header_values: dict[str, Any] | fits.Header,
    ):
        super().__init__(
            file_schema=file_schema,
            dataset_shape=dataset_shape,
            array_shape=array_shape,
        )
        self.file_schema = file_schema
        self.dataset_extra_name = dataset_extra_name
        self.add_constant_key("NAXIS", self.array_ndim)
        for n in range(1, self.array_ndim + 1):
            self.add_constant_key(
                "NAXIS" + str(n), self.array_shape[self.array_ndim - n]
            )

        self.add_constant_key("TIMESYS", "UTC")
        self.add_constant_key("ORIGIN", "National Solar Observatory")
        self.add_constant_key("TELESCOP", "Daniel K. Inouye Solar Telescope")
        self.add_constant_key("OBSRVTRY", "Haleakala High Altitude Observatory Site")
        self.add_constant_key("NETWORK", "NSF-DKIST")
        self.add_constant_key("BUNIT", "ADU")
        if self.file_schema.instrument:
            self.add_constant_key("INSTRUME", self.file_schema.instrument.value)
        if self.dataset_extra_name:
            self.add_constant_key("EXTNAME", self.dataset_extra_name.value)

    @property
    def data(self):
        return np.zeros(self.array_shape)
