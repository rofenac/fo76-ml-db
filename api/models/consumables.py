"""Consumable-related Pydantic models"""
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class ConsumableBase(BaseModel):
    """Base consumable model"""
    id: int = Field(description="Consumable ID", alias="consumable_id")
    name: str = Field(description="Consumable name", alias="consumable_name")
    category: str = Field(description="Category (food, drink, chem, aid, alcohol, beverage)")
    subcategory: Optional[str] = Field(default=None, description="Subcategory")

    class Config:
        populate_by_name = True


class ConsumableDetail(ConsumableBase):
    """Detailed consumable model with all stats"""
    effects: Optional[str] = Field(default=None, description="Effects description (semicolon-separated)")
    duration: Optional[str] = Field(default=None, description="Duration (e.g., '3600 seconds')")
    hp_restore: Optional[Decimal] = Field(default=None, description="HP restored")
    rads: Optional[Decimal] = Field(default=None, description="Radiation (negative = removal)")
    hunger_satisfaction: Optional[Decimal] = Field(default=None, description="Hunger satisfaction value")
    thirst_satisfaction: Optional[Decimal] = Field(default=None, description="Thirst satisfaction value")
    special_modifiers: Optional[str] = Field(default=None, description="SPECIAL modifiers (e.g., '+1 S, +2 P')")
    addiction_risk: Optional[Decimal] = Field(default=None, description="Addiction risk percentage")
    disease_risk: Optional[Decimal] = Field(default=None, description="Disease risk percentage")
    weight: Optional[Decimal] = Field(default=None, description="Item weight")
    value: Optional[int] = Field(default=None, description="Item value (caps)")
    form_id: Optional[str] = Field(default=None, description="Game form ID")
    crafting_station: Optional[str] = Field(default=None, description="Required crafting station")
    source_url: Optional[str] = Field(default=None, description="Source URL from wiki")


class ConsumableFilters(BaseModel):
    """Query filters for consumables"""
    category: Optional[str] = Field(default=None, description="Filter by category")
    subcategory: Optional[str] = Field(default=None, description="Filter by subcategory")
    search: Optional[str] = Field(default=None, description="Search by name")
