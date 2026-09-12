from typing import Optional
from pydantic import BaseModel


class BarChartItem(BaseModel):
    type: str
    count: int
    total: float
    year: int
    month: int


class LineChartItem(BaseModel):
    year: int
    month: int
    value: float


class PieChartItem(BaseModel):
    categoryName: str
    color: Optional[str] = None
    count: int


class ChartsResponse(BaseModel):
    barChart: list[BarChartItem]
    lineChart: list[LineChartItem]
    pieChart: list[PieChartItem]