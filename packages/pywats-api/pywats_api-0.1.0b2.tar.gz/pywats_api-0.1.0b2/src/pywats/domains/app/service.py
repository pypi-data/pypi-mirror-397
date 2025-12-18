"""App service - business logic layer.

All business operations for statistics, KPIs, and dashboard data.
"""
from typing import Optional, List, Dict, Any

from .repository import AppRepository
from .models import YieldData, ProcessInfo, LevelInfo, ProductGroup
from ..report.models import WATSFilter, ReportHeader


class AppService:
    """
    App/Statistics business logic layer.

    Provides high-level operations for statistics, KPIs, and analytics.
    """

    def __init__(self, repository: AppRepository):
        """
        Initialize with AppRepository.

        Args:
            repository: AppRepository instance for data access
        """
        self._repository = repository

    # =========================================================================
    # System Info
    # =========================================================================

    def get_version(self) -> Dict[str, Any]:
        """
        Get WATS API version information.

        Returns:
            Version information dictionary
        """
        return self._repository.get_version() or {}

    def get_processes(self) -> List[ProcessInfo]:
        """
        Get all defined test processes/operations.

        Returns:
            List of ProcessInfo objects
        """
        return self._repository.get_processes()

    def get_levels(self) -> List[LevelInfo]:
        """
        Get all production levels.

        Returns:
            List of LevelInfo objects
        """
        return self._repository.get_levels()

    def get_product_groups(self) -> List[ProductGroup]:
        """
        Get all product groups.

        Returns:
            List of ProductGroup objects
        """
        return self._repository.get_product_groups()

    # =========================================================================
    # Yield Statistics
    # =========================================================================

    def get_dynamic_yield(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[YieldData]:
        """
        Get dynamic yield statistics by custom dimensions (PREVIEW).

        Supported dimensions: partNumber, productName, stationName, location,
        purpose, revision, testOperation, processCode, swFilename, swVersion,
        productGroup, level, period, batchNumber, operator, fixtureId, etc.

        Args:
            filter_data: WATSFilter with dimensions and filters

        Returns:
            List of YieldData objects
        """
        return self._repository.get_dynamic_yield(filter_data)

    def get_dynamic_repair(
        self, filter_data: Union[WATSFilter, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Get dynamic repair statistics by custom dimensions (PREVIEW).

        Args:
            filter_data: WATSFilter with dimensions and filters

        Returns:
            List of repair statistics data
        """
        return self._repository.get_dynamic_repair(filter_data)

    def get_volume_yield(
        self,
        filter_data: Optional[WATSFilter] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Get volume/yield statistics.

        Args:
            filter_data: Optional WATSFilter for POST request
            product_group: Optional product group filter (for GET)
            level: Optional level filter (for GET)

        Returns:
            List of YieldData objects
        """
        return self._repository.get_volume_yield(
            filter_data=filter_data, product_group=product_group, level=level
        )

    def get_worst_yield(
        self,
        filter_data: Optional[WATSFilter] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Get worst yield statistics.

        Args:
            filter_data: Optional WATSFilter for POST request
            product_group: Optional product group filter (for GET)
            level: Optional level filter (for GET)

        Returns:
            List of YieldData objects
        """
        return self._repository.get_worst_yield(
            filter_data=filter_data, product_group=product_group, level=level
        )

    def get_worst_yield_by_product_group(
        self, filter_data: WATSFilter
    ) -> List[YieldData]:
        """
        Get worst yield by product group.

        Args:
            filter_data: WATSFilter with parameters

        Returns:
            List of YieldData objects by product group
        """
        return self._repository.get_worst_yield_by_product_group(filter_data)

    # =========================================================================
    # High Volume Analysis
    # =========================================================================

    def get_high_volume(
        self,
        filter_data: Optional[WATSFilter] = None,
        product_group: Optional[str] = None,
        level: Optional[str] = None,
    ) -> List[YieldData]:
        """
        Get high volume product list.

        Args:
            filter_data: Optional WATSFilter for POST request
            product_group: Optional product group filter (for GET)
            level: Optional level filter (for GET)

        Returns:
            List of YieldData objects
        """
        return self._repository.get_high_volume(
            filter_data=filter_data, product_group=product_group, level=level
        )

    def get_high_volume_by_product_group(
        self, filter_data: WATSFilter
    ) -> List[YieldData]:
        """
        Get yield by product group sorted by volume.

        Args:
            filter_data: WATSFilter with parameters

        Returns:
            List of YieldData objects by product group
        """
        return self._repository.get_high_volume_by_product_group(filter_data)

    # =========================================================================
    # Failure Analysis
    # =========================================================================

    def get_top_failed(
        self,
        filter_data: Optional[WATSFilter] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Get top failed test steps.

        Args:
            filter_data: Optional WATSFilter for POST request
            **kwargs: Additional query parameters for GET

        Returns:
            List of top failed step data
        """
        return self._repository.get_top_failed(filter_data, **kwargs)

    def get_test_step_analysis(
        self, filter_data: WATSFilter
    ) -> Dict[str, Any]:
        """
        Get test step analysis data (PREVIEW).

        Args:
            filter_data: WATSFilter with analysis parameters

        Returns:
            Test step analysis data
        """
        return self._repository.get_test_step_analysis(filter_data)

    # =========================================================================
    # Repair History
    # =========================================================================

    def get_related_repair_history(
        self, part_number: str, revision: str
    ) -> List[Dict[str, Any]]:
        """
        Get list of repaired failures related to the part number and revision.

        Args:
            part_number: Product part number
            revision: Product revision

        Returns:
            List of repair history records
        """
        return self._repository.get_related_repair_history(
            part_number, revision
        )

    # =========================================================================
    # Measurement Analysis
    # =========================================================================

    def get_aggregated_measurements(
        self, filter_data: WATSFilter
    ) -> List[Dict[str, Any]]:
        """
        Get aggregated measurement statistics.

        Args:
            filter_data: WATSFilter with measurement filters

        Returns:
            List of aggregated measurement data
        """
        return self._repository.get_aggregated_measurements(filter_data)

    def get_measurements(
        self, filter_data: WATSFilter
    ) -> List[Dict[str, Any]]:
        """
        Get measurement data (PREVIEW).

        Args:
            filter_data: WATSFilter with measurement filters

        Returns:
            List of measurement data
        """
        return self._repository.get_measurements(filter_data)

    # =========================================================================
    # OEE Analysis
    # =========================================================================

    def get_oee_analysis(self, filter_data: WATSFilter) -> Dict[str, Any]:
        """
        Get Overall Equipment Effectiveness analysis.

        Supported filters: productGroup, level, partNumber, revision,
        stationName, testOperation, status, swFilename, swVersion,
        socket, dateFrom, dateTo

        Args:
            filter_data: WATSFilter with OEE parameters

        Returns:
            OEE analysis data
        """
        return self._repository.get_oee_analysis(filter_data)

    # =========================================================================
    # Serial Number History
    # =========================================================================

    def get_serial_number_history(
        self, filter_data: WATSFilter
    ) -> List[ReportHeader]:
        """
        Get test history for a serial number.

        Supported filters: productGroup, level, serialNumber, partNumber,
        batchNumber, miscValue

        Args:
            filter_data: WATSFilter with serial number and other filters

        Returns:
            List of ReportHeader objects
        """
        return self._repository.get_serial_number_history(filter_data)

    # =========================================================================
    # UUT/UUR Reports
    # =========================================================================

    def get_uut_reports(
        self,
        filter_data: Optional[WATSFilter] = None,
        **kwargs: Any,
    ) -> List[ReportHeader]:
        """
        Get UUT report headers (like Test Reports in Reporting).

        By default the 1000 newest reports that match the filter are returned.
        Use topCount filter to change this.

        Note: This API is not suitable for workflow or production management,
        use the Production module instead.

        Args:
            filter_data: Optional WATSFilter for POST request
            **kwargs: Query parameters for GET request

        Returns:
            List of ReportHeader objects
        """
        return self._repository.get_uut_reports(filter_data, **kwargs)

    def get_uur_reports(self, filter_data: WATSFilter) -> List[ReportHeader]:
        """
        Get UUR report headers (like Repair Reports in Reporting).

        By default the 1000 newest reports that match the filter are returned.
        Use topCount filter to change this.

        Note: This API is not suitable for workflow or production management,
        use the Production module instead.

        Args:
            filter_data: WATSFilter with filter parameters

        Returns:
            List of ReportHeader objects
        """
        return self._repository.get_uur_reports(filter_data)

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def get_yield_summary(
        self,
        part_number: str,
        revision: Optional[str] = None,
        days: int = 30,
    ) -> List[YieldData]:
        """
        Get yield summary for a product over a time period.

        Args:
            part_number: Product part number
            revision: Optional product revision
            days: Number of days to include (default: 30)

        Returns:
            List of YieldData objects
        """
        filter_data = WATSFilter(
            part_number=part_number,
            revision=revision,
            period_count=days,
            dimensions="partNumber;period",
        )
        return self.get_dynamic_yield(filter_data)

    def get_station_yield(
        self, station_name: str, days: int = 7
    ) -> List[YieldData]:
        """
        Get yield statistics for a specific test station.

        Args:
            station_name: Test station name
            days: Number of days to include (default: 7)

        Returns:
            List of YieldData objects
        """
        filter_data = WATSFilter(
            station_name=station_name,
            period_count=days,
            dimensions="stationName;period",
        )
        return self.get_dynamic_yield(filter_data)
