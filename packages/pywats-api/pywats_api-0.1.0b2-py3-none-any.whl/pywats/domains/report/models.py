"""Report domain models - filter and header classes for querying."""
from typing import Optional
from datetime import datetime
from uuid import UUID
from pydantic import Field, AliasChoices, field_serializer

from ...shared import PyWATSModel
from .enums import DateGrouping


class WATSFilter(PyWATSModel):
    """
    WATS filter for querying reports and statistics.

    Attributes:
        serial_number: Filter by serial number
        part_number: Filter by part number
        revision: Filter by revision
        batch_number: Filter by batch number
        station_name: Filter by station name
        test_operation: Filter by test operation
        status: Filter by status
        yield_value: Filter by yield percentage
        misc_description: Filter by misc info description
        misc_value: Filter by misc info value
        product_group: Filter by product group
        level: Filter by level
        sw_filename: Filter by software filename
        sw_version: Filter by software version
        socket: Filter by socket
        date_from: Filter by start date
        date_to: Filter by end date
        date_grouping: Date grouping option
        period_count: Number of periods
        include_current_period: Include current period
        max_count: Maximum results
        min_count: Minimum count filter
        top_count: Top N results
        dimensions: Custom dimensions string
    """
    serial_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("serialNumber", "serial_number"),
        serialization_alias="serialNumber"
    )
    part_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("partNumber", "part_number"),
        serialization_alias="partNumber"
    )
    revision: Optional[str] = Field(default=None)
    batch_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("batchNumber", "batch_number"),
        serialization_alias="batchNumber"
    )
    station_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("stationName", "station_name"),
        serialization_alias="stationName"
    )
    test_operation: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("testOperation", "test_operation"),
        serialization_alias="testOperation"
    )
    status: Optional[str] = Field(default=None)
    yield_value: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("yield", "yield_value"),
        serialization_alias="yield"
    )
    misc_description: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("miscDescription", "misc_description"),
        serialization_alias="miscDescription"
    )
    misc_value: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("miscValue", "misc_value"),
        serialization_alias="miscValue"
    )
    product_group: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("productGroup", "product_group"),
        serialization_alias="productGroup"
    )
    level: Optional[str] = Field(default=None)
    sw_filename: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("swFilename", "sw_filename"),
        serialization_alias="swFilename"
    )
    sw_version: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("swVersion", "sw_version"),
        serialization_alias="swVersion"
    )
    socket: Optional[str] = Field(default=None)
    date_from: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("dateFrom", "date_from"),
        serialization_alias="dateFrom"
    )
    date_to: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("dateTo", "date_to"),
        serialization_alias="dateTo"
    )
    date_grouping: Optional[DateGrouping] = Field(
        default=None,
        validation_alias=AliasChoices("dateGrouping", "date_grouping"),
        serialization_alias="dateGrouping"
    )
    period_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("periodCount", "period_count"),
        serialization_alias="periodCount"
    )
    include_current_period: Optional[bool] = Field(
        default=None,
        validation_alias=AliasChoices(
            "includeCurrentPeriod", "include_current_period"
        ),
        serialization_alias="includeCurrentPeriod"
    )
    max_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("maxCount", "max_count"),
        serialization_alias="maxCount"
    )
    min_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("minCount", "min_count"),
        serialization_alias="minCount"
    )
    top_count: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("topCount", "top_count"),
        serialization_alias="topCount"
    )
    dimensions: Optional[str] = Field(default=None)

    @field_serializer('date_from', 'date_to')
    def serialize_datetime(self, v: Optional[datetime]) -> Optional[str]:
        """Serialize datetime to ISO format."""
        return v.isoformat() if v else None


class ReportHeader(PyWATSModel):
    """
    Represents a report header (summary info).

    Attributes:
        uuid: Report unique identifier
        serial_number: Unit serial number
        part_number: Product part number
        revision: Product revision
        batch_number: Batch number
        station_name: Test station name
        test_operation: Test operation name
        status: Report status
        start_utc: Test start time
        root_node_type: Root node type
        operator: Operator name
    """
    uuid: Optional[UUID] = Field(default=None)
    serial_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("serialNumber", "serial_number"),
        serialization_alias="serialNumber"
    )
    part_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("partNumber", "part_number"),
        serialization_alias="partNumber"
    )
    revision: Optional[str] = Field(default=None)
    batch_number: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("batchNumber", "batch_number"),
        serialization_alias="batchNumber"
    )
    station_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("stationName", "station_name"),
        serialization_alias="stationName"
    )
    test_operation: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("testOperation", "test_operation"),
        serialization_alias="testOperation"
    )
    status: Optional[str] = Field(default=None)
    start_utc: Optional[datetime] = Field(
        default=None,
        validation_alias=AliasChoices("startUtc", "start_utc"),
        serialization_alias="startUtc"
    )
    root_node_type: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("rootNodeType", "root_node_type"),
        serialization_alias="rootNodeType"
    )
    operator: Optional[str] = Field(default=None)


class Attachment(PyWATSModel):
    """
    Represents a report attachment.

    Attributes:
        attachment_id: Attachment ID
        file_name: Original filename
        mime_type: MIME type
        size: File size in bytes
        description: Attachment description
    """
    attachment_id: Optional[int] = Field(
        default=None,
        validation_alias=AliasChoices("attachmentId", "attachment_id"),
        serialization_alias="attachmentId"
    )
    file_name: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("fileName", "file_name"),
        serialization_alias="fileName"
    )
    mime_type: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("mimeType", "mime_type"),
        serialization_alias="mimeType"
    )
    size: Optional[int] = Field(default=None)
    description: Optional[str] = Field(default=None)
