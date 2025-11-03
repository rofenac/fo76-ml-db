"""Mutation-related Pydantic models"""
from typing import Optional
from pydantic import BaseModel, Field


class MutationBase(BaseModel):
    """Base mutation model"""
    id: int = Field(description="Mutation ID", alias="mutation_id")
    name: str = Field(description="Mutation name", alias="mutation_name")
    form_id: Optional[str] = Field(default=None, description="Game form ID")

    class Config:
        populate_by_name = True


class MutationDetail(MutationBase):
    """Detailed mutation model with effects and interactions"""
    positive_effects: Optional[str] = Field(default=None, description="Positive effects (semicolon-separated)")
    negative_effects: Optional[str] = Field(default=None, description="Negative effects (semicolon-separated)")
    exclusive_with: Optional[str] = Field(default=None, description="Mutually exclusive mutation")
    suppression_perk: Optional[str] = Field(default=None, description="Perk that suppresses negative effects")
    enhancement_perk: Optional[str] = Field(default=None, description="Perk that enhances positive effects")
    source_url: Optional[str] = Field(default=None, description="Source URL from wiki")


class MutationFilters(BaseModel):
    """Query filters for mutations"""
    search: Optional[str] = Field(default=None, description="Search by name")
