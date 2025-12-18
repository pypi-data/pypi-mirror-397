from itertools import chain

from .dse_core import (
    DatasetExtraBase,
    DatasetExtraName,
    DatasetExtraSchema,
    DatasetExtraTables,
    InstrumentTables,
)

DLNIRSP_DEFAULT_KEEP_SCHEMA = [
    DatasetExtraTables.aggregate,
    DatasetExtraTables.common,
    DatasetExtraTables.fits,
    DatasetExtraTables.gos,
    DatasetExtraTables.ip_task,
]


class DlnirspDatasetExtraSchema(DatasetExtraSchema):
    def __init__(
        self, *args, instrument=InstrumentTables.dlnirsp, keep_schemas=None, **kwargs
    ):
        if keep_schemas is None:
            keep_schemas = DLNIRSP_DEFAULT_KEEP_SCHEMA
        super().__init__(instrument=instrument, keep_schemas=keep_schemas, **kwargs)


class DlnirspBadPixelMapExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.gos,
                    DatasetExtraTables.aggregate,
                ],
            ),
            dataset_extra_name=DatasetExtraName.bad_pixel_map,
            dataset_shape=(1, 400, 70, 50),
            array_shape=(400, 70, 50),
        )


class DlnirspDarkExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.dark,
            dataset_shape=(1, 2048, 2048),
            array_shape=(2048, 2048),
        )


class DlnirspSolarGainExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.solar_gain,
            dataset_shape=(1, 2048, 2048),
            array_shape=(2048, 2048),
        )


class DlnirspCharacteristicSpectraExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.characteristic_spectra,
            dataset_shape=(1, 100),
            array_shape=(100,),
        )


class DlnirspSpectralCurvatureShiftsExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.spectral_curvature_shifts,
            dataset_shape=(1, 2, 10000),
            array_shape=(2, 10000),
        )


class DlnirspSpectralCurvatureScalesExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.spectral_curvature_scales,
            dataset_shape=(1, 2, 10000),
            array_shape=(2, 10000),
        )


class DlnirspWaveCalInputSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_input_spectrum,
            dataset_shape=(1, 100),
            array_shape=(100,),
        )


class DlnirspWaveCalReferenceSpectrumExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.atlas],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.wavelength_calibration_reference_spectrum,
            dataset_shape=(1, 10, 10),
            array_shape=(10, 10),
        )


class DlnirspReferenceWavelengthVectorExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(
                keep_schemas=[DatasetExtraTables.common, DatasetExtraTables.wavecal],
                remove_instrument_table=True,
            ),
            dataset_extra_name=DatasetExtraName.reference_wavelength_vector,
            dataset_shape=(1, 1024),
            array_shape=(1024,),
        )


class DlnirspDemodulationMatricesExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.aggregate,
                ],
            ),
            dataset_extra_name=DatasetExtraName.demodulation_matrices,
            dataset_shape=(1, 2048, 2048, 4, 8),
            array_shape=(2048, 2048, 4, 8),
        )


class DlnirspPolcalAsScienceExtra(DatasetExtraBase):
    def __init__(self):
        super().__init__(
            file_schema=DlnirspDatasetExtraSchema(
                keep_schemas=[
                    DatasetExtraTables.common,
                    DatasetExtraTables.ip_task,
                    DatasetExtraTables.gos,
                ],
            ),
            dataset_extra_name=DatasetExtraName.polcal_as_science,
            dataset_shape=(14, 400, 70, 50),
            array_shape=(400, 70, 50),
        )


ALL_DLNIRSP_DATASET_EXTRAS = [
    DlnirspBadPixelMapExtra,
    DlnirspDarkExtra,
    DlnirspSolarGainExtra,
    DlnirspCharacteristicSpectraExtra,
    DlnirspSpectralCurvatureScalesExtra,
    DlnirspSpectralCurvatureShiftsExtra,
    DlnirspWaveCalInputSpectrumExtra,
    DlnirspWaveCalReferenceSpectrumExtra,
    DlnirspReferenceWavelengthVectorExtra,
    DlnirspDemodulationMatricesExtra,
    DlnirspPolcalAsScienceExtra,
]


def all_dlnirsp_dataset_extras():
    """Returns a file-by-file iterable for the dataset extras."""
    return chain.from_iterable([extra() for extra in ALL_DLNIRSP_DATASET_EXTRAS])
