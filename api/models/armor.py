"""Armor-related Pydantic models"""
from typing import Optional
from pydantic import BaseModel, Field
from decimal import Decimal


class ArmorBase(BaseModel):
    """Base armor model"""
    id: int = Field(description="Armor ID")
    name: str = Field(description="Armor piece name")
    armor_type: Optional[str] = Field(default=None, description="Armor type (regular, power)")
    armor_class: Optional[str] = Field(default=None, description="Armor class (Light, Sturdy, Heavy)")
    slot: Optional[str] = Field(default=None, description="Equipment slot")
    set_name: Optional[str] = Field(default=None, description="Armor set name")
    min_level: Optional[int] = Field(default=None, description="Minimum player level requirement")


class ArmorDetail(ArmorBase):
    """Detailed armor model with all resistances"""
    damage_resistance: Optional[Decimal] = Field(default=None, description="Physical damage resistance")
    energy_resistance: Optional[Decimal] = Field(default=None, description="Energy damage resistance")
    radiation_resistance: Optional[Decimal] = Field(default=None, description="Radiation resistance")
    cryo_resistance: Optional[Decimal] = Field(default=None, description="Cryo resistance")
    fire_resistance: Optional[Decimal] = Field(default=None, description="Fire resistance")
    poison_resistance: Optional[Decimal] = Field(default=None, description="Poison resistance")
    form_id: Optional[str] = Field(default=None, description="Game form ID")
    source_url: Optional[str] = Field(default=None, description="Source URL from wiki")


class ArmorFilters(BaseModel):
    """Query filters for armor"""
    armor_type: Optional[str] = Field(default=None, description="Filter by armor type")
    armor_class: Optional[str] = Field(default=None, description="Filter by armor class")
    slot: Optional[str] = Field(default=None, description="Filter by equipment slot")
    set_name: Optional[str] = Field(default=None, description="Filter by armor set")
    search: Optional[str] = Field(default=None, description="Search by name")
