from itertools import chain

from dkist_data_simulator.dataset import key_function
from .dse_core import (
    DatasetExtraBase,
    DatasetExtraName,
    DatasetExtraSchema,
    DatasetExtraTables,
    InstrumentTables,
)

VISP_DEFAULT_KEEP_SCHEMA = [
    DatasetExtraTables.aggregate,
    DatasetExtraTables.common,
    DatasetExtraTables.fits,
    DatasetExtraTables.gos,
    DatasetExtraTables.ip_task,
]


class VispDatasetExtraSchema(DatasetExtraSchema):
    def __init__(
        self, *args, instrument=InstrumentTables.visp, keep_schemas=None, **kwargs
    ):
        if keep_schemas is None:
            keep_schemas = VISP_DEFAULT_KEEP_SCHEMA
        super().__init__(instrument=instrument, keep_schemas=keep_schemas, **kwargs)


class VispBeamDatasetExtraBase(DatasetExtraBase):
    @key_function("VSPBEAM")
    def beam_number(self, key: str):
        return self.index + 1


class VispDarkExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.dark,
            dataset_shape=(2, 1000, 2560),
            array_shape=(1000, 2560),
        )


class VispBackgroundLightExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.background_light,
            dataset_shape=(2, 1000, 2560),
            array_shape=(1000, 2560),
        )


class VispSolarGainExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.ip_task],
            ),
            dataset_extra_name=DatasetExtraName.solar_gain,
            dataset_shape=(2, 1000, 2560),
            array_shape=(1000, 2560),
        )


class VispCharacteristicSpectraExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.characteristic_spectra,
            dataset_shape=(2, 1000, 2560),
            array_shape=(1000, 2560),
        )


class VispModulationStateOffsetsExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.modulation_state_offsets,
            dataset_shape=(20, 2),
            array_shape=(2,),
        )


class VispBeamAnglesExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.beam_angles,
            dataset_shape=(2, 1),
            array_shape=(1,),
        )


class VispSpectralCurvatureShiftsExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.spectral_curvature_shifts,
            dataset_shape=(2, 2560),
            array_shape=(2560,),
        )


class VispWaveCalInputSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_input_spectrum,
            dataset_shape=(1, 1000),
            array_shape=(1000,),
        )
        self.add_constant_key("VSPBEAM", 1)


class VispWaveCalReferenceSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.atlas],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_reference_spectrum,
            dataset_shape=(1, 10, 10),
            array_shape=(10, 10),
        )


class VispReferenceWavelengthVectorExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.wavecal],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.reference_wavelength_vector,
            dataset_shape=(1, 1000),
            array_shape=(1000,),
        )


class VispDemodulationMatricesExtra(VispBeamDatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.aggregate,
                ],
            ),
            dataset_extra_name=DatasetExtraName.demodulation_matrices,
            dataset_shape=(2, 1000, 2560, 4, 10),
            array_shape=(1000, 2560, 4, 10),
        )


class VispPolcalAsScienceExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=VispDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.gos,
                ],
            ),
            dataset_extra_name=DatasetExtraName.polcal_as_science,
            dataset_shape=(14, 1000, 2560),
            array_shape=(1000, 2560),
        )


ALL_VISP_DATASET_EXTRAS = [
    VispDarkExtra,
    VispBackgroundLightExtra,
    VispSolarGainExtra,
    VispCharacteristicSpectraExtra,
    VispModulationStateOffsetsExtra,
    VispBeamAnglesExtra,
    VispSpectralCurvatureShiftsExtra,
    VispWaveCalInputSpectrumExtra,
    VispWaveCalReferenceSpectrumExtra,
    VispReferenceWavelengthVectorExtra,
    VispDemodulationMatricesExtra,
    VispPolcalAsScienceExtra,
]


def all_visp_dataset_extras():
    """Returns a file-by-file iterable for the dataset extras."""
    return chain.from_iterable([extra() for extra in ALL_VISP_DATASET_EXTRAS])
