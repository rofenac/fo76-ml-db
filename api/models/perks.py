"""Perk-related Pydantic models"""
from typing import Optional
from pydantic import BaseModel, Field


class PerkRank(BaseModel):
    """Individual perk rank"""
    rank: int = Field(description="Rank number (1-5 for regular, 1-4 for legendary)")
    description: str = Field(description="Rank description/effects")
    form_id: Optional[str] = Field(default=None, description="Game form ID")


class PerkBase(BaseModel):
    """Base perk model"""
    id: int = Field(description="Perk ID", alias="perk_id")
    name: str = Field(description="Perk name", alias="perk_name")
    special: Optional[str] = Field(default=None, description="SPECIAL attribute (S, P, E, C, I, A, L)")
    min_level: Optional[int] = Field(default=None, description="Minimum player level requirement")
    race: Optional[str] = Field(default=None, description="Race restrictions (Human, Ghoul, or both)")

    class Config:
        populate_by_name = True


class PerkDetail(PerkBase):
    """Detailed perk model with rank information"""
    rank: Optional[int] = Field(default=None, description="Current rank being viewed")
    rank_description: Optional[str] = Field(default=None, description="Description for this rank")


class LegendaryPerkBase(BaseModel):
    """Base legendary perk model"""
    id: int = Field(description="Legendary perk ID", alias="legendary_perk_id")
    name: str = Field(description="Legendary perk name", alias="perk_name")
    base_description: Optional[str] = Field(default=None, description="Base perk description")
    race: Optional[str] = Field(default=None, description="Race restrictions")

    class Config:
        populate_by_name = True


class LegendaryPerkDetail(LegendaryPerkBase):
    """Detailed legendary perk model with rank information"""
    rank: Optional[int] = Field(default=None, description="Current rank (1-4)")
    rank_description: Optional[str] = Field(default=None, description="Description for this rank")
    effect_value: Optional[float] = Field(default=None, description="Effect value for this rank")
    effect_type: Optional[str] = Field(default=None, description="Effect type/unit")


class PerkFilters(BaseModel):
    """Query filters for perks"""
    special: Optional[str] = Field(default=None, description="Filter by SPECIAL attribute")
    race: Optional[str] = Field(default=None, description="Filter by race")
    search: Optional[str] = Field(default=None, description="Search by name")
