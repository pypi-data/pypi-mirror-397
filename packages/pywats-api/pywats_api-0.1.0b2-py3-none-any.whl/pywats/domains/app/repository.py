"""App repository - data access layer.

All API interactions for statistics, KPIs, and dashboard data.
"""
from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING, cast
import logging

if TYPE_CHECKING:
    from ...core import HttpClient
    from ...core.exceptions import ErrorHandler

from .models import YieldData, ProcessInfo, LevelInfo, ProductGroup
from ..report.models import WATSFilter, ReportHeader


class AppRepository:
    """
    App/Statistics data access layer.

    Handles all WATS API interactions for statistics and KPIs.
    """

    def __init__(
        self, 
        http_client: "HttpClient",
        error_handler: Optional["ErrorHandler"] = None
    ):
        """
        Initialize with HTTP client.

        Args:
            http_client: HttpClient for making HTTP requests
            error_handler: ErrorHandler for response handling (optional for backward compat)
        """
        self._http_client = http_client
        self._error_handler = error_handler

    # =========================================================================
    # System Info
    # =========================================================================

    def get_version(self) -> Optional[Dict[str, Any]]:
        """
        Get server/api version.

        GET /api/App/Version

        Returns:
            Version info dictionary or None
        """
        response = self._http_client.get("/api/App/Version")
        
        if self._error_handler:
            data = self._error_handler.handle_response(
                response, operation="get_version", allow_empty=True
            )
            return cast(Dict[str, Any], data) if data else None
        
        # Backward compatibility: original behavior
        if response.is_success and response.data:
            return cast(Dict[str, Any], response.data)
        return None

    def get_processes(self) -> List[ProcessInfo]:
        """
        Get processes.

        GET /api/App/Processes

        Returns:
            List of ProcessInfo objects
        """
        response = self._http_client.get("/api/App/Processes")
        
        if self._error_handler:
            data = self._error_handler.handle_response(
                response, operation="get_processes", allow_empty=True
            )
            if data:
                return [ProcessInfo.model_validate(item) for item in data]
            return []
        
        # Backward compatibility
        if response.is_success and response.data:
            return [ProcessInfo.model_validate(item) for item in response.data]
        return []

    def get_levels(self) -> List[LevelInfo]:
        """
        Retrieves all ClientGroups (levels).

        GET /api/App/Levels

        Returns:
            List of LevelInfo objects
        """
        response = self._http_client.get("/api/App/Levels")
        
        if self._error_handler:
            data = self._error_handler.handle_response(
                response, operation="get_levels", allow_empty=True
            )
            if data:
                return [LevelInfo.model_validate(item) for item in data]
            return []
        
        # Backward compatibility
        if response.is_success and response.data:
            return [LevelInfo.model_validate(item) for item in response.data]
        return []

    def get_product_groups(self) -> List[ProductGroup]:
        """
        Retrieves all ProductGroups.

        GET /api/App/ProductGroups

        Returns:
            List of ProductGroup objects
        """
        response = self._http_client.get("/api/App/ProductGroups")
        
        if self._error_handler:
            data = self._error_handler.handle_response(
                response, operation="get_product_groups", allow_empty=True
            )
            if data:
                return [ProductGroup.model_validate(item) for item in data]
            return []
        
        # Backward compatibility
        if response.is_success and response.data:
            return [
                ProductGroup.model_validate(item) for item in response.data
            ]
        return []

    # =========================================================================
    # Yield Statistics
    # =========================================================================

    def get_dynamic_yield(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Calculate yield by custom dimensions (PREVIEW).

        POST /api/App/DynamicYield

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of YieldData objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/DynamicYield", data=data)
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    def get_volume_yield(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Volume/Yield list.

        GET/POST /api/App/VolumeYield

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/VolumeYield", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/VolumeYield", params=params if params else None
            )
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    def get_high_volume(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        High Volume list.

        GET/POST /api/App/HighVolume

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/HighVolume", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/HighVolume", params=params if params else None
            )
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    def get_high_volume_by_product_group(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Yield by product group sorted by volume.

        POST /api/App/HighVolumeByProductGroup

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of YieldData objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post(
            "/api/App/HighVolumeByProductGroup", data=data
        )
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    def get_worst_yield(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Worst Yield list.

        GET/POST /api/App/WorstYield

        Args:
            filter_data: WATSFilter object or dict (for POST)
            product_group: Product group filter (for GET)
            level: Level filter (for GET)

        Returns:
            List of YieldData objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/WorstYield", data=data)
        else:
            params: Dict[str, Any] = {}
            if product_group:
                params["productGroup"] = product_group
            if level:
                params["level"] = level
            response = self._http_client.get(
                "/api/App/WorstYield", params=params if params else None
            )
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    def get_worst_yield_by_product_group(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Yield by product group sorted by lowest yield.

        POST /api/App/WorstYieldByProductGroup

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of YieldData objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post(
            "/api/App/WorstYieldByProductGroup", data=data
        )
        if response.is_success and response.data:
            return [YieldData.model_validate(item) for item in response.data]
        return []

    # =========================================================================
    # Repair Statistics
    # =========================================================================

    def get_dynamic_repair(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Calculate repair statistics by custom dimensions (PREVIEW).

        POST /api/App/DynamicRepair

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of repair statistics dictionaries
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/DynamicRepair", data=data)
        if response.is_success and response.data:
            return (
                response.data
                if isinstance(response.data, list)
                else [response.data]
            )
        return []

    def get_related_repair_history(
        self, part_number: str, revision: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of repaired failures related to the part number and revision.

        GET /api/App/RelatedRepairHistory

        Args:
            part_number: Product part number
            revision: Product revision

        Returns:
            List of repair history dictionaries
        """
        params: Dict[str, Any] = {
            "partNumber": part_number,
            "revision": revision,
        }
        response = self._http_client.get(
            "/api/App/RelatedRepairHistory", params=params
        )
        if response.is_success and response.data:
            return (
                response.data
                if isinstance(response.data, list)
                else [response.data]
            )
        return []

    # =========================================================================
    # Failure Analysis
    # =========================================================================

    def get_top_failed(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Get the top failed steps.

        GET/POST /api/App/TopFailed

        Args:
            filter_data: WATSFilter object or dict (for POST)
            **kwargs: Query parameters (for GET)

        Returns:
            List of failed step dictionaries
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/TopFailed", data=data)
        else:
            response = self._http_client.get(
                "/api/App/TopFailed", params=kwargs if kwargs else None
            )
        if response.is_success and response.data:
            return (
                response.data
                if isinstance(response.data, list)
                else [response.data]
            )
        return []

    def get_test_step_analysis(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get step and measurement statistics (PREVIEW).

        POST /api/App/TestStepAnalysis

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            Step analysis dictionary
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/TestStepAnalysis", data=data)
        if response.is_success and response.data:
            return cast(Dict[str, Any], response.data)
        return {}

    # =========================================================================
    # Measurements
    # =========================================================================

    def get_measurements(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get numeric measurements by measurement path (PREVIEW).

        POST /api/App/Measurements

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of measurement dictionaries
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/Measurements", data=data)
        if response.is_success and response.data:
            return (
                response.data
                if isinstance(response.data, list)
                else [response.data]
            )
        return []

    def get_aggregated_measurements(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated numeric measurements by measurement path.

        POST /api/App/AggregatedMeasurements

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of aggregated measurement dictionaries
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post(
            "/api/App/AggregatedMeasurements", data=data
        )
        if response.is_success and response.data:
            return (
                response.data
                if isinstance(response.data, list)
                else [response.data]
            )
        return []

    # =========================================================================
    # OEE (Overall Equipment Effectiveness)
    # =========================================================================

    def get_oee_analysis(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Overall Equipment Effectiveness - analysis.

        POST /api/App/OeeAnalysis

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            OEE analysis dictionary
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/OeeAnalysis", data=data)
        if response.is_success and response.data:
            return cast(Dict[str, Any], response.data)
        return {}

    # =========================================================================
    # Serial Number and Unit History
    # =========================================================================

    def get_serial_number_history(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[ReportHeader]:
        """
        Serial Number History.

        POST /api/App/SerialNumberHistory

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of ReportHeader objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/SerialNumberHistory", data=data)
        if response.is_success and response.data:
            return [
                ReportHeader.model_validate(item) for item in response.data
            ]
        return []

    def get_uut_reports(
        self,
        filter_data: Optional[Union[WATSFilter, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> List[ReportHeader]:
        """
        Returns UUT report header info.

        GET/POST /api/App/UutReport

        Args:
            filter_data: WATSFilter object or dict (for POST)
            **kwargs: Query parameters (for GET)

        Returns:
            List of ReportHeader objects
        """
        if filter_data:
            if isinstance(filter_data, WATSFilter):
                data = filter_data.model_dump(by_alias=True, exclude_none=True)
            else:
                data = filter_data
            response = self._http_client.post("/api/App/UutReport", data=data)
        else:
            response = self._http_client.get(
                "/api/App/UutReport", params=kwargs if kwargs else None
            )
        if response.is_success and response.data:
            return [
                ReportHeader.model_validate(item) for item in response.data
            ]
        return []

    def get_uur_reports(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[ReportHeader]:
        """
        Returns UUR report header info.

        POST /api/App/UurReport

        Args:
            filter_data: WATSFilter object or dict

        Returns:
            List of ReportHeader objects
        """
        if isinstance(filter_data, WATSFilter):
            data = filter_data.model_dump(by_alias=True, exclude_none=True)
        else:
            data = filter_data
        response = self._http_client.post("/api/App/UurReport", data=data)
        if response.is_success and response.data:
            return [
                ReportHeader.model_validate(item) for item in response.data
            ]
        return []
