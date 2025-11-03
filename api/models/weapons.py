"""Weapon-related Pydantic models"""
from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class DamageComponent(BaseModel):
    """Weapon damage component"""
    damage_type: str = Field(description="Type of damage (physical, energy, radiation, etc.)")
    min_damage: Decimal = Field(description="Minimum damage value")
    max_damage: Optional[Decimal] = Field(default=None, description="Maximum damage value (if range)")
    level_tier: Optional[int] = Field(default=None, description="Level tier for multi-level weapons")


class WeaponMechanic(BaseModel):
    """Special weapon mechanic"""
    mechanic_type: str = Field(description="Type of mechanic (charge, spin-up, chain_lightning, etc.)")
    description: Optional[str] = Field(default=None, description="Mechanic description")
    numeric_value: Optional[Decimal] = Field(default=None, description="Primary numeric value")
    numeric_value_2: Optional[Decimal] = Field(default=None, description="Secondary numeric value")
    string_value: Optional[str] = Field(default=None, description="String value or condition")
    unit: Optional[str] = Field(default=None, description="Unit (multiplier, percent, meters, etc.)")
    notes: Optional[str] = Field(default=None, description="Additional notes")


class WeaponBase(BaseModel):
    """Base weapon model"""
    id: int = Field(description="Weapon ID")
    name: str = Field(description="Weapon name")
    weapon_type: Optional[str] = Field(default=None, description="Weapon type (Ranged, Melee, Thrown)")
    weapon_class: Optional[str] = Field(default=None, description="Weapon class (Pistol, Rifle, Shotgun, etc.)")
    min_level: Optional[int] = Field(default=None, description="Minimum player level requirement")
    form_id: Optional[str] = Field(default=None, description="Game form ID")


class WeaponDetail(WeaponBase):
    """Detailed weapon model with damage, perks, and mechanics"""
    damage_components: List[DamageComponent] = Field(default_factory=list, description="Damage breakdown")
    regular_perks: Optional[str] = Field(default=None, description="Applicable regular perks (semicolon-separated)")
    legendary_perks: Optional[str] = Field(default=None, description="Applicable legendary perks (semicolon-separated)")
    mechanics: List[WeaponMechanic] = Field(default_factory=list, description="Special weapon mechanics")
    source_url: Optional[str] = Field(default=None, description="Source URL from wiki")


class WeaponListItem(WeaponBase):
    """Simplified weapon model for list views"""
    damage: Optional[str] = Field(default=None, description="Simplified damage string")


class WeaponFilters(BaseModel):
    """Query filters for weapons"""
    weapon_type: Optional[str] = Field(default=None, description="Filter by weapon type")
    weapon_class: Optional[str] = Field(default=None, description="Filter by weapon class")
    min_level: Optional[int] = Field(default=None, description="Filter by minimum level")
    search: Optional[str] = Field(default=None, description="Search by name")
