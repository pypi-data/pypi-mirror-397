import logging
import random
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

import aramis_exporter as _pkg
import numpy as np

from .constants import (RESULT_TYPE_MAP,
                        DISP_DIRECTION_MAP,
                        CALIBRATION_FIELD_MAP,
                        ACQUISITION_FIELD_MAP,
                        IMAGE_MODE_FIELD_MAP,
                        SURFACE_COMPONENT_FIELD_MAP)
from .models import (FacetData,
                     ValueElement,
                     StageObjMetadata,
                     ProcessMetadata,
                     CalibrationMetadata,
                     AcquisitionMetadata,
                     ImageModeMetadata,
                     SurfaceComponentParameters,
                     StageProcessData,
                     RbmcData,
                     GlobalMetadata,
                     PerStageMetadata, SignalData
                     )
from .utils import safe_getattr


class GOMClient:
    """
    Wrapper for interaction with GOM API.

    Methods:
        open_project(project_path: str) -> None
            Opens an already existing project.

        close_project() -> None
            Closes the currently open project.

        initialize(set_rbmc_active: bool = True) -> None
            Prepare the client for data extraction: checks surface components,
             ensures RBMC is present and active (if not requested otherwise),
            parses XML metadata and verifies all stages are active.

        show_last_stage() -> Any
            Show (display) and return the last stage of the project.

        show_stage(stage_index: int) -> Any
            Show (display) and return the stage specified by a 0-based index.

        get_is_initialized() -> bool
            Return True when the client has been initialized via `initialize()`.

        get_project_name() -> str
            Return the project name.

        get_project_file_path() -> str
            Return the absolute path to the project file.

        get_all_stages() -> Any
            Return the project stages collection.

        get_stage_by_index(stage_index: int) -> Optional[Any]
            Return the stage object for the given index or None if not found.

        get_index_of_stage(stage: Any) -> int
            Return the index value of the supplied stage object.

        get_current_stage_index() -> int
            Return the 0-based index of the currently active stage.

        get_current_stage_name() -> str
            Return the name of the currently active stage.

        get_num_stages() -> int
            Return the total number of stages in the project.

        get_ref_stage_index() -> int
            Return the reference stage index (0-based).

        is_current_stage_computed() -> bool
            Return True if the currently active stage has computed results.

        get_current_stage_results() -> FacetData
            Extract numeric result arrays (coordinates, displacement, strain) for the currently active stage.

        get_current_stage_facet_connections() -> np.ndarray
            Return triangle/node connectivity for the currently active stage.

        get_project_metadata() -> GlobalMetadata
            Gather and return global metadata for the project (process, calibration, acquisition, image mode, surface params).

        get_current_stage_metadata() -> PerStageMetadata
            Gather and return metadata for the currently active stage (stage header, stage process data, RBMC and signal data).
    """

    def __init__(self, gom, logger: Optional[logging.Logger] = None):
        """
        Args:
            gom: GOM API object
            logger: Optional logger instance. If None, a default logger is created.
        """
        # setup logger
        if logger is None:
            logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
            logger.setLevel(logging.INFO)

            if not logger.hasHandlers():
                ch = logging.StreamHandler()
                ch.setLevel(logging.INFO)
                formatter = logging.Formatter(
                    "%(asctime)s %(levelname)s %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                ch.setFormatter(formatter)
                logger.addHandler(ch)

        self.logger = logger

        # GOM application
        self._gom = gom
        self.app = gom.app
        try:
            self.project = gom.app.project
        except AttributeError as e:
            self.logger.error("No project is currently opened in ZEISS Inspect. "
                              "Please open a project before proceeding."
                              "Use GOMClient.open_project(project_path) to open a project programmatically.")
            self.project = None
        self.script = gom.script
        self.gom_File = gom.File

        # Project metadata
        self.current_surface_comp = None
        (self.process_data, self.camera_information,
         self.calibration_data, self.surface_component_parameters) = None, None, None, None
        self.xml_metadata = None

        # helpers
        self.result_types, self.disp_directions = RESULT_TYPE_MAP, DISP_DIRECTION_MAP

        # state variables
        self.surface_component_checked = False
        self.rbmc_active = False
        self.all_stages_active = False
        self.initialized = False

    def open_project(self, project_path: str):
        """
        Opens a GOM project file.

        Args:
            project_path: Path to the GOM project file to open.
        """
        self.logger.info(f"Opening GOM project from {project_path}...")
        self.script.sys.load_project(
            file=project_path,
            load_working_copy=True
        )
        self.project = self.app.project
        self.logger.info("Project opened.")

    def close_project(self):
        """
        Closes the currently opened GOM project.
        """
        self.logger.info("Closing current GOM project...")
        self.script.sys.close_project()
        self.project = None
        self.initialized = False
        self.logger.info("Project closed.")

    def initialize(self, set_rbmc_active=True):
        """Initializes the GOM client for the currently opened Aramis project.

        Args:
            set_rbmc_active: Whether to activate rigid body motion compensation. Default is True. If False,
                            deactivates RBMC if it exists.
        """
        if self.project is None:
            raise RuntimeError("No project is currently opened in ZEISS Inspect. "
                               "Please open a project before initializing the GOM client."
                               "Use GOMClient.open_project(project_path) to open a project programmatically.")

        self.logger.info("Initializing GOM client...")
        self._check_surface_components()
        self.current_surface_comp = self._get_current_component()
        self._check_rbmc(activate_rbmc=set_rbmc_active)
        self.xml_metadata = self._gather_xml_metadata()
        self._check_all_stages_active()
        self.initialized = True
        self.logger.info("GOM client initialized.")

    def is_initialized(self) -> bool:
        """
        Returns:
            whether the client has been initialized
        """
        return self.initialized

    def get_all_stages(self) -> Any:
        """
        Returns:
            all stages of the project
        """
        return self.project.stages

    def get_stage_by_index(self, stage_idx: int) -> Optional[Any]:
        """
        Args:
            stage_idx: index of the stage to retrieve

        Returns:
            stage at the specified index
        """
        return next((stage for stage in self.project.stages if stage.get('index') == stage_idx), None)

    def get_index_of_stage(self, stage: Any) -> int:
        """
        Args:
            stage: stage object to find the index for

        Returns:
            index of the specified stage
        """
        return stage.get('index')

    def get_current_stage_index(self) -> int:
        """Gets the index of the currently active stage (0-based)."""
        return int(self._get_current_component().get('stage.index') - 1)

    def get_current_stage_name(self) -> str:
        """Gets the name of the currently active stage."""
        return self._get_current_component().get('stage.name')

    def get_ref_stage_index(self) -> int:
        """
        Returns:
            reference stage index
        """
        return int(self.project.get('reference_stage.index') - 1)

    def get_num_stages(self) -> int:
        """
        Returns:
            total number of stages
        """
        return len(self.project.stages)

    def is_current_stage_computed(self) -> bool:
        """Checks if the currently active stage has computed inspection results."""
        current_surface_comp = self._get_current_component(comp_index=0).get('name')
        return self.project.inspection[current_surface_comp + '.dX'].computation_status == "computed"

    def get_current_stage_results(self) -> FacetData:
        """Gets all inspection results for the currently active stage as numpy arrays."""
        current_stage_idx = self.get_current_stage_index()
        self.logger.info(
            f"Getting result dictionary for stage with name {self.project.stages[current_stage_idx].get('name')}"
            f" and index {current_stage_idx}...")
        return self._get_stage_results(stage_idx=current_stage_idx)

    def get_current_stage_facet_connections(self) -> np.ndarray:
        """Gets facet connectivity for the currently active stage."""
        current_surface_comp = self._get_current_component(comp_index=0).get('name')
        current_stage_idx = self.get_current_stage_index()
        self.logger.info(
            f"Getting facet connections for stage with name {self.project.stages[current_stage_idx].get('name')} "
            f"and index {self.project.stages[current_stage_idx].get('index')}...")
        return np.array(self.project.actual_elements[current_surface_comp].data.triangle[current_stage_idx])

    def show_stage(self, stage_idx: int):
        """Shows specific stage and returns the aramis stage object.

        Args:
            stage_idx: index used to specify stage. Starting with 0 for first stage

        Returns:
            aramis stage object

        """
        stage = self.project.stages[stage_idx]
        self.script.sys.show_stage(stage=stage)
        self.logger.info(
            f"Showing stage with name {self.project.stages[stage_idx].get('name')} "
            f"and index {self.project.stages[stage_idx].get('index')}...")
        return stage

    def show_last_stage(self):
        """Shows last stage of project and returns the stage object.

        Returns:
            aramis stage object
        """
        stage = self.project.stages[-1]
        self.script.sys.show_stage(stage=stage)
        self.logger.info(f"Showing stage with name {self.project.stages[-1].get('name')} "
                         f"and index {self.project.stages[-1].get('index')}...")
        return stage

    def get_project_name(self) -> str:
        """
        Returns:
            project name
        """
        return self.project.get('name')

    def get_project_file_path(self) -> str:
        """
        Returns:
            project file path
        """
        return self.project.project_file

    def get_project_metadata(self) -> GlobalMetadata:
        """Gathers all global metadata from the open Aramis dic project.

        Returns:
            (dict) global metadata

        """
        return GlobalMetadata(
            process=self._gather_general_process_metadata(),
            calibration=self._gather_calibration_metadata(),
            acquisition=self._gather_acquisition_metadata(),
            image_mode=self._gather_image_mode_metadata(),
            surface_component=self._gather_surface_component_parameters(),
        )

    def get_current_stage_metadata(self) -> PerStageMetadata:
        """Gathers metadata for the currently active stage (header, process, RBMC, signals)."""
        return PerStageMetadata(
            stage_metadata=self._get_stageobj_metadata(self.get_current_stage_index()),
            stage_process_data=self._gather_stage_process_data(),
            rbmc_data=self._gather_rmbc_data(),
            signal_data=self._gather_signal_data()
        )

    def _get_stage_results(self, stage_idx: int) -> FacetData:
        """Gets all inspection results for a specific stage as numpy arrays.

        Args:
            stage_idx: index of stage starting from 0

        Returns:
            FacetData object
        """
        current_surface_comp = self._get_current_component(comp_index=0)

        facet_coordinates = np.array(self.project.actual_elements[current_surface_comp.name].data.coordinate[
                                         stage_idx])  # check for s.th. like 'data.ref_coordinate
        facet_coordinates = np.where(np.abs(facet_coordinates) > 1e-30, facet_coordinates, 0)
        disp_x = np.array(self.project.inspection[current_surface_comp.name + '.dX'].data.result_dimension.deviation[
                              stage_idx]).flatten()
        disp_y = np.array(self.project.inspection[current_surface_comp.name + '.dY'].data.result_dimension.deviation[
                              stage_idx]).flatten()
        disp_z = np.array(self.project.inspection[current_surface_comp.name + '.dZ'].data.result_dimension.deviation[
                              stage_idx]).flatten()
        eps_x = np.array(self.project.inspection[current_surface_comp.name + '.epsX'].data.result_dimension.deviation[
                             stage_idx]).flatten()
        eps_y = np.array(self.project.inspection[current_surface_comp.name + '.epsY'].data.result_dimension.deviation[
                             stage_idx]).flatten()
        eps_xy = np.array(self.project.inspection[current_surface_comp.name + '.epsXY'].data.result_dimension.deviation[
                              stage_idx]).flatten()
        eps_eqv = np.array(self.project.inspection[current_surface_comp.name + '.phiM'].data.result_dimension.deviation[
                               stage_idx]).flatten()

        x_undef = facet_coordinates[:, 0] - disp_x
        y_undef = facet_coordinates[:, 1] - disp_y
        z_undef = facet_coordinates[:, 2] - disp_z

        return FacetData(
            facet_coordinates=facet_coordinates,
            x_undef=x_undef,
            y_undef=y_undef,
            z_undef=z_undef,
            disp_x=disp_x,
            disp_y=disp_y,
            disp_z=disp_z,
            eps_x=eps_x,
            eps_y=eps_y,
            eps_xy=eps_xy,
            eps_eqv=eps_eqv,
        )

    def _get_stageobj_metadata(self, current_stage_idx: int) -> StageObjMetadata:
        """Gets metadata of a specific stage.

        Args:
            current_stage_idx: index of current stage starting from 0

        Returns:
            StageMetadata object

        """
        return self.xml_metadata[current_stage_idx]

    def _get_current_component(self, comp_index=0):
        """Gets the surface component of index as current_component.

        Args:
            comp_index: index of surface component

        Returns:
            current surface component

        """
        return self.project.actual_elements.filter("type", "surface_component")[comp_index]

    def _check_all_stages_active(self):
        """Checks if all stages are active.
            Raises Error if not."""
        for stage in self.project.stages:
            if not stage.is_active:
                raise ValueError("Exports only work if ALL stages are set active.")
            else:
                pass

        self.all_stages_active = True

    def _check_rbmc(self, activate_rbmc=True):
        """Checks if rigid body motion compensation was conducted and is active."""

        if not self._is_rbmc_applied():
            self.logger.info("No rigid body motion compensation found. Creating one...")
            self._create_rbmc()

        gom_elements = self.project.alignments.filter('type', 'transformation_object')
        for gom_elem in gom_elements:
            if gom_elem.get('object_family') == 'alignment_rbmc':
                rbmc_object_name = gom_elem.get('name')
                if activate_rbmc:
                    self.script.manage_alignment.set_alignment_active(
                        movement_correction=self.project.alignments[rbmc_object_name])
                    self.rbmc_active = True
                    self.logger.info("Activating rigid body motion compensation.")
                else:
                    self.script.manage_alignment.deactivate_rigid_body_motion_compensation(
                        movement_correction=self.project.alignments[rbmc_object_name])
                    self.logger.info("Deactivating rigid body motion compensation as per user request.")
                    self.rbmc_active = False

        self.script.sys.recalculate_project(with_reports=False)

    def _create_rbmc(self):
        """Creates rigid body motion compensation object in the project."""
        if self._is_rbmc_applied():
            self.logger.info("Rigid body motion compensation already exists. Nothing to create.")
            return

        _ = self.script.alignment.create_rbmc_by_component(
            alignment_stage_creation_policy='separate_alignment_for_each_stage',
            component=self.project.actual_elements[self.current_surface_comp.name],
            name_expression='SKBK über $creation_sequence_args[\'component\'] != Unknown ? creation_sequence_args[\'component\'].name : \'?\'$')

        self.script.sys.recalculate_project(with_reports=False)

    def _delete_rbmc(self):
        """Deletes rigid body motion compensation from the project."""
        if not self._is_rbmc_applied():
            self.logger.info("No rigid body motion compensation found. Nothing to delete.")
            return

        gom_elements = self.project.alignments.filter('type', 'transformation_object')
        for gom_elem in gom_elements:
            if gom_elem.get('object_family') == 'alignment_rbmc':
                rbmc_object_name = gom_elem.get('name')
                self.script.cad.delete_element(
                    elements=self.project.alignments[rbmc_object_name],
                    with_measuring_principle=True)
                self.logger.info("Deleting rigid body motion compensation.")

        self.rbmc_active = False
        self.script.sys.recalculate_project(with_reports=False)

    def _is_rbmc_applied(self) -> bool:
        """Checks if rigid body motion compensation was conducted.

        Returns:
            whether rigid body motion compensation is applied
        """
        gom_elements = self.project.alignments.filter('type', 'transformation_object')
        for gom_elem in gom_elements:
            if gom_elem.get('object_family') == 'alignment_rbmc':
                return True
        return False

    def _check_surface_components(self):
        """Checks if all necessary data are calculated."""
        gom_surface_component_elements = self.project.actual_elements.filter('type', 'surface_component')
        surface_component_element_name = gom_surface_component_elements[0].get('name')

        actual_surf_elements = []
        for gom_element in self.project.inspection:
            actual_surf_elements.append(gom_element.get('name'))

        for result_string in self.result_types.keys():
            if surface_component_element_name + result_string not in actual_surf_elements:
                if self.result_types[result_string] == "displacement":
                    distance_restriction = self.disp_directions[result_string]
                    _ = self.script.inspection.inspect_dimension(
                        elements=[self.project.actual_elements[surface_component_element_name]],
                        distance_restriction=distance_restriction,
                        nominal_value=0.0,
                        nominal_value_source='fixed_value',
                        type=self.result_types[result_string])
                else:
                    _ = self.script.inspection.inspect_dimension(
                        elements=[self.project.actual_elements[surface_component_element_name]],
                        nominal_value=0.0,
                        nominal_value_source='fixed_value',
                        type=self.result_types[result_string])
                self.logger.info(f"Creating surface element '{surface_component_element_name + result_string}' "
                                 f"against nominal value = 0.0.")
        self.logger.info("Recalculating...")
        self.script.sys.recalculate_project(with_reports=False)
        self.logger.info("...done.")

    def _gather_general_process_metadata(self) -> ProcessMetadata:
        """Gathers all process data from the open Aramis dic project.

        Returns:
            (dict) process data

        """
        return ProcessMetadata(
            application_name=self.app.application_name,
            application_version=self.app.application_build_information.version,
            application_revision=self.app.application_build_information.revision,
            application_build_date=self.app.application_build_information.date,
            current_user=self.app.current_user,
            gom_project_file=self.project.project_file,
            project_creation_time=self.project.project_creation_time,
            aramis_data_exporter_version=getattr(_pkg, "__version__", "unknown"),
        )

    def _gather_calibration_metadata(self) -> CalibrationMetadata:
        """Gathers all calibration data from the open Aramis dic project."""
        calibration = self.current_surface_comp.deformation_measurement_information.calibration

        data = {
            field: safe_getattr(calibration, attr)
            for field, attr in CALIBRATION_FIELD_MAP.items()
        }

        return CalibrationMetadata(**data)

    def _gather_acquisition_metadata(self) -> AcquisitionMetadata:
        acquisition = self.current_surface_comp.deformation_measurement_information.acquisition

        data = {
            field: safe_getattr(acquisition, attr)
            for field, attr in ACQUISITION_FIELD_MAP.items()
        }

        return AcquisitionMetadata(**data)

    def _gather_image_mode_metadata(self) -> ImageModeMetadata:
        acquisition = self.current_surface_comp.deformation_measurement_information.acquisition
        # get the image mode object
        image_mode = safe_getattr(acquisition, "image_mode")

        data = {
            field: safe_getattr(image_mode, attr)
            for field, attr in IMAGE_MODE_FIELD_MAP.items()
        }
        data.update({"image_mode": image_mode})
        return ImageModeMetadata(**data)

    def _gather_surface_component_parameters(self):
        curr_surface_comp = self.current_surface_comp

        data = {
            field: safe_getattr(curr_surface_comp, attr)
            for field, attr in SURFACE_COMPONENT_FIELD_MAP.items()
        }
        return SurfaceComponentParameters(**data)

    def _gather_stage_process_data(self) -> StageProcessData:
        """Gathers process data tied to the currently active stage."""

        return StageProcessData(
            export_date=datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f"),
            exposure_time=self.project.measurement_series['Deformation 1']
            .measurements['D1']
            .get('acquisition_parameters.exposure_time'),
            current_stage_index=self.get_current_stage_index(),
            current_stage_name=self.get_current_stage_name(),
            current_stage_date=self.current_surface_comp.get('stage.absolute_time_stamp'),
            current_stage_date_ms=self.xml_metadata[self.get_current_stage_index()].date,
            current_stage_relative_date=self.current_surface_comp.get('stage.relative_time'),
            reference_stage_index=self.get_ref_stage_index(),
            reference_stage_name=self.current_surface_comp.get('reference_stage.name'),
            reference_stage_date=self.current_surface_comp.get('reference_stage.absolute_time_stamp'),
        )

    def _gather_rmbc_data(self) -> Optional[RbmcData]:
        """Gathers rigid body motion compensation data for the currently active stage."""
        gom_elements = self.project.alignments.filter('type', 'transformation_object')

        for gom_element in gom_elements:
            if gom_element.get('object_family') == 'alignment_rbmc':
                rbmc_object_name = gom_element.get('name')
                a = self.project.alignments[rbmc_object_name].alignment

                return RbmcData(
                    alignment_is_active=self.rbmc_active,
                    alignment_rotation_x=a.rotation.x,
                    alignment_rotation_y=a.rotation.y,
                    alignment_rotation_z=a.rotation.z,
                    alignment_translation_x=a.translation.x,
                    alignment_translation_y=a.translation.y,
                    alignment_translation_z=a.translation.z,
                    alignment_deviation=a.deviation,
                )

        return None

    def _gather_signal_data(self) -> SignalData:
        """Gathers analog input and inspection signal values for the currently active stage.


        Returns:
            (dict) analog input signals

        """
        gom_value_elements = self.project.inspection.filter('type', 'inspection_value_element')
        if not gom_value_elements:
            gom_value_elements = self.project.actual_elements.filter('type', 'inspection_value_element')
        inspection_value_elements = []
        for value_element in gom_value_elements:
            ele = ValueElement(name=value_element.get('name'),
                               type=value_element.get('type'),
                               value=value_element.get("input_value"))
            inspection_value_elements.append(ele)

        gom_value_elements = self.project.inspection.filter('type', 'value_element')
        if not gom_value_elements:
            gom_value_elements = self.project.actual_elements.filter('type', 'value_element')
        value_elements = []
        for value_element in gom_value_elements:
            ele = ValueElement(name=value_element.get('name'),
                               type=value_element.get('type'),
                               value=value_element.get("input_value"))
            value_elements.append(ele)

        gom_analog_inputs = self.project.inspection.filter('type', 'analog_input')
        if not gom_analog_inputs:
            gom_analog_inputs = self.project.actual_elements.filter('type', 'analog_input')
        analog_inputs = []
        for analog_input in gom_analog_inputs:
            ai = ValueElement(name=analog_input.get('name'),
                              type=analog_input.get('type'),
                              value=analog_input.get("dimension"))
            analog_inputs.append(ai)

        return SignalData(inspection_value_elements=inspection_value_elements or None,
                          value_elements=value_elements or None,
                          analog_inputs=analog_inputs or None)

    def _gather_xml_metadata(self) -> Dict[int, StageObjMetadata]:
        """Gathers metadata from the XML file (Datei -> Exportieren -> Stufendaten -> Elements (xml)).
        This is currently the sole source of timestamps with millisecond precision.

        Returns:
            (dict) metadata from the XML file

        """
        self.logger.info("Gathering metadata from the XML file...")
        random_number = random.randint(1, 1000)
        xml_path = Path(self.project.project_file).parent / f"tmp_{random_number}.xml"
        self.script.sys.export_gom_xml(
            angle_unit='default',
            decimal_places=50,
            elements=[self.project.actual_elements[self.current_surface_comp.name]],
            export_stages_mode='all',
            file=str(xml_path),
            format=self.gom_File('giefv20_stages.xsl'),
            length_unit='default',
            one_file_per_stage=False,
            use_imported_names_for_export=False)
        metadata = self._parse_xml_metadata(xml_path)
        xml_path.unlink()  # Delete the temporary file
        return metadata

    def _parse_xml_metadata(self, xml_path: Path) -> Dict[int, StageObjMetadata]:
        tree = ET.parse(xml_path)
        meta: Dict[int, StageObjMetadata] = {}
        for stage in tree.findall('.//header/stage'):
            idx = int(stage.get('index')) - 1
            meta[idx] = StageObjMetadata(
                index=idx,
                id=int(stage.get('id')),
                name=stage.get('name'),
                date=datetime.strptime(stage.get('date'), "%Y-%m-%dT%H:%M:%S.%f"),
                nanoseconds=int(stage.get('nanoseconds')),
                rel_time=float(stage.get('rel_time'))
            )
        return meta
