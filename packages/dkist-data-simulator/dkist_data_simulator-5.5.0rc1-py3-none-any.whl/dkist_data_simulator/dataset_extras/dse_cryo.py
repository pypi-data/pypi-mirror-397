from itertools import chain

from dkist_data_simulator.dataset import key_function
from .dse_core import (
    DatasetExtraBase,
    DatasetExtraName,
    DatasetExtraSchema,
    DatasetExtraTables,
    InstrumentTables,
)

CRYO_DEFAULT_KEEP_SCHEMA = [
    DatasetExtraTables.aggregate,
    DatasetExtraTables.common,
    DatasetExtraTables.fits,
    DatasetExtraTables.gos,
    DatasetExtraTables.ip_task,
]


class CryoDatasetExtraSchema(DatasetExtraSchema):
    def __init__(
        self, *args, instrument=InstrumentTables.cryonirsp, keep_schemas=None, **kwargs
    ):
        if keep_schemas is None:
            keep_schemas = CRYO_DEFAULT_KEEP_SCHEMA
        super().__init__(instrument=instrument, keep_schemas=keep_schemas, **kwargs)


class CryoBeamDatasetExtraBase(DatasetExtraBase):
    @key_function("CNBEAM")
    def beam_number(self, key: str):
        return self.index + 1


class CryoBadPixelMapExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.bad_pixel_map,
            dataset_shape=(1, 2048, 2048),
            array_shape=(2048, 2048),
        )


class CryoDarkExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.dark,
            dataset_shape=(2, 2048, 2048),
            array_shape=(2048, 2048),
        )


class CryoSolarGainExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.solar_gain,
            dataset_shape=(2, 2048, 2048),
            array_shape=(2048, 2048),
        )


class CryoCharacteristicSpectraExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.characteristic_spectra,
            dataset_shape=(2, 2048),
            array_shape=(2048,),
        )


class CryoBeamOffsetsExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.beam_offsets,
            dataset_shape=(2, 2),
            array_shape=(2,),
        )


class CryoBeamAnglesExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.beam_angles,
            dataset_shape=(2, 1),
            array_shape=(1,),
        )


class CryoSpectralCurvatureShiftsExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.spectral_curvature_shifts,
            dataset_shape=(2, 2048),
            array_shape=(2048,),
        )


class CryoWaveCalInputSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_input_spectrum,
            dataset_shape=(1, 1024),
            array_shape=(1024,),
        )


class CryoWaveCalReferenceSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.atlas],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_reference_spectrum,
            dataset_shape=(1, 10, 10),
            array_shape=(10, 10),
        )


class CryoReferenceWavelengthVectorExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.wavecal],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.reference_wavelength_vector,
            dataset_shape=(1, 1024),
            array_shape=(1024,),
        )


class CryoDemodulationMatricesExtra(CryoBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.aggregate,
                ],
            ),
            dataset_extra_name=DatasetExtraName.demodulation_matrices,
            dataset_shape=(2, 4, 8),
            array_shape=(4, 8),
        )


class CryoPolcalAsScienceExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=CryoDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.gos,
                ],
            ),
            dataset_extra_name=DatasetExtraName.polcal_as_science,
            dataset_shape=(14, 2046, 2048),
            array_shape=(2046, 2048),
        )


ALL_CRYO_DATASET_EXTRAS = [
    CryoBadPixelMapExtra,
    CryoDarkExtra,
    CryoSolarGainExtra,
    CryoCharacteristicSpectraExtra,
    CryoBeamOffsetsExtra,
    CryoBeamAnglesExtra,
    CryoSpectralCurvatureShiftsExtra,
    CryoWaveCalInputSpectrumExtra,
    CryoWaveCalReferenceSpectrumExtra,
    CryoReferenceWavelengthVectorExtra,
    CryoDemodulationMatricesExtra,
    CryoPolcalAsScienceExtra,
]


def all_cryo_dataset_extras():
    """Returns a file-by-file iterable for the dataset extras."""
    return chain.from_iterable([extra() for extra in ALL_CRYO_DATASET_EXTRAS])
