"""Plato SDK v2 - Models."""

from __future__ import annotations

from abc import ABC
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# ============================================================================
# Flow Step Models
# ============================================================================


class FlowStep(BaseModel, ABC):
    """Base flow step class that all specific flow steps inherit from."""

    type: str = Field(..., description="Step type")
    description: str | None = Field(default=None, description="Step descriptions")
    timeout: int = Field(default=10000, description="Timeout in milliseconds")
    retries: int = Field(default=0, ge=0, description="Number of times to retry on failure")
    retry_delay_ms: int = Field(default=500, ge=0, description="Delay between retries in milliseconds")

    class Config:
        extra = "forbid"


class WaitForSelectorStep(FlowStep):
    """Wait for a CSS selector to be present."""

    type: Literal["wait_for_selector"] = "wait_for_selector"  # type: ignore[reportIncompatibleVariableOverride]
    selector: str = Field(..., description="CSS selector to wait for")


class ClickStep(FlowStep):
    """Click on an element."""

    type: Literal["click"] = "click"  # type: ignore[reportIncompatibleVariableOverride]
    selector: str = Field(..., description="CSS selector to click")


class FillStep(FlowStep):
    """Fill an input field."""

    type: Literal["fill"] = "fill"  # type: ignore[reportIncompatibleVariableOverride]
    selector: str = Field(..., description="CSS selector for input field")
    value: str | int | bool = Field(..., description="Value to fill")


class WaitStep(FlowStep):
    """Wait for a specified duration."""

    type: Literal["wait"] = "wait"  # type: ignore[reportIncompatibleVariableOverride]
    duration: int = Field(..., description="Duration to wait in milliseconds")


class NavigateStep(FlowStep):
    """Navigate to a URL."""

    type: Literal["navigate"] = "navigate"  # type: ignore[reportIncompatibleVariableOverride]
    url: str = Field(..., description="URL to navigate to")


class WaitForUrlStep(FlowStep):
    """Wait for URL to contain specific text."""

    type: Literal["wait_for_url"] = "wait_for_url"  # type: ignore[reportIncompatibleVariableOverride]
    url_contains: str = Field(..., description="URL substring to wait for")


class CheckElementStep(FlowStep):
    """Check if an element exists."""

    type: Literal["check_element"] = "check_element"  # type: ignore[reportIncompatibleVariableOverride]
    selector: str = Field(..., description="CSS selector to check")
    should_exist: bool = Field(default=True, description="Whether element should exist")


class ScreenshotStep(FlowStep):
    """Take a screenshot."""

    type: Literal["screenshot"] = "screenshot"  # type: ignore[reportIncompatibleVariableOverride]
    filename: str = Field(..., description="Screenshot filename")
    full_page: bool = Field(default=False, description="Take full page screenshot")


class VerifyTextStep(FlowStep):
    """Verify text appears on the page."""

    type: Literal["verify_text"] = "verify_text"  # type: ignore[reportIncompatibleVariableOverride]
    text: str = Field(..., description="Text to verify")
    should_exist: bool = Field(default=True, description="Whether text should exist")


class VerifyUrlStep(FlowStep):
    """Verify the current URL."""

    type: Literal["verify_url"] = "verify_url"  # type: ignore[reportIncompatibleVariableOverride]
    url: str = Field(..., description="Expected URL")
    contains: bool = Field(default=True, description="Whether to use contains matching")


class VerifyNoErrorsStep(FlowStep):
    """Verify no error indicators are present."""

    type: Literal["verify_no_errors"] = "verify_no_errors"  # type: ignore[reportIncompatibleVariableOverride]
    error_selectors: list[str] = Field(
        default_factory=lambda: [
            ".error",
            ".alert-danger",
            ".alert-error",
            "[role='alert']",
            ".error-message",
            ".validation-error",
        ],
        description="Selectors for error elements",
    )


class VerifyStep(FlowStep):
    """Generic verification step with subtypes."""

    type: Literal["verify"] = "verify"  # type: ignore[reportIncompatibleVariableOverride]
    verify_type: Literal["element_exists", "element_visible", "element_text", "element_count", "page_title"] = Field(
        ..., description="Verification subtype"
    )
    selector: str | None = Field(default=None, description="CSS selector (for element verifications)")
    text: str | None = Field(default=None, description="Expected text")
    contains: bool = Field(default=True, description="Whether to use contains matching")
    count: int | None = Field(default=None, description="Expected element count")
    title: str | None = Field(default=None, description="Expected page title")

    @model_validator(mode="after")
    def validate_verify_fields(self):
        verify_type = self.verify_type
        if verify_type in ["element_exists", "element_visible", "element_text", "element_count"]:
            if not self.selector:
                raise ValueError(f"selector is required for verification type '{verify_type}'")
        if verify_type == "element_text" and not self.text:
            raise ValueError("text is required for element_text verification")
        if verify_type == "element_count" and self.count is None:
            raise ValueError("count is required for element_count verification")
        if verify_type == "page_title" and not self.title:
            raise ValueError("title is required for page_title verification")
        return self


FLOW_STEP_TYPES: dict[str, type[FlowStep]] = {
    "wait_for_selector": WaitForSelectorStep,
    "click": ClickStep,
    "fill": FillStep,
    "wait": WaitStep,
    "navigate": NavigateStep,
    "wait_for_url": WaitForUrlStep,
    "check_element": CheckElementStep,
    "screenshot": ScreenshotStep,
    "verify_text": VerifyTextStep,
    "verify_url": VerifyUrlStep,
    "verify_no_errors": VerifyNoErrorsStep,
    "verify": VerifyStep,
}


def parse_flow_step(step_data: dict[str, Any]) -> FlowStep:
    """Parse a flow step dictionary into the appropriate FlowStep subclass."""
    step_type = step_data.get("type")
    if not step_type:
        raise ValueError("Type is required for flow step")
    if step_type not in FLOW_STEP_TYPES:
        raise ValueError(f"Unknown flow step type: {step_type}")

    step_class = FLOW_STEP_TYPES[step_type]
    return step_class.model_validate(step_data)


class Flow(BaseModel):
    """Flow configuration with validation."""

    name: str = Field(..., description="Flow name")
    description: str | None = Field(default=None, description="Flow description")
    steps: list[FlowStep] = Field(default_factory=list, description="Flow steps")

    @field_validator("steps", mode="before")
    @classmethod
    def parse_steps(cls, v):
        """Parse raw step dictionaries into proper FlowStep objects."""
        if isinstance(v, list):
            return [parse_flow_step(step) if isinstance(step, dict) else step for step in v]
        return v


# ============================================================================
# Configuration Models
# ============================================================================


class SimConfig(BaseModel):
    """Compute configuration for a blank VM."""

    cpus: int = Field(default=1, ge=1, le=8, description="vCPUs")
    memory: int = Field(default=2048, ge=512, le=16384, description="Memory in MB")
    disk: int = Field(default=10240, ge=1024, le=102400, description="Disk space in MB")


class EnvOption(BaseModel):
    """Configuration for a single environment in a session.

    Each EnvOption creates one job/VM. Provide either:
    - artifact_id: Use a specific artifact/snapshot
    - sim_config: Start a blank VM with specified resources

    If neither is provided, resolves artifact via the prod-latest tag.
    """

    simulator: str = Field(description="Simulator name (e.g., 'espocrm')")
    alias: str | None = Field(
        default=None,
        description="Custom name for this environment (defaults to simulator name)",
    )
    artifact_id: str | None = Field(default=None, description="Specific artifact/snapshot ID to use")
    sim_config: SimConfig | None = Field(
        default=None,
        description="Compute config for blank VM (mutually exclusive with artifact_id)",
    )

    @classmethod
    def from_simulator(cls, simulator: str, alias: str | None = None) -> EnvOption:
        """Create an EnvOption from just a simulator name (uses prod-latest artifact)."""
        return cls(simulator=simulator, alias=alias)

    @classmethod
    def from_artifact(cls, simulator: str, artifact_id: str, alias: str | None = None) -> EnvOption:
        """Create an EnvOption from a simulator and artifact_id."""
        return cls(simulator=simulator, artifact_id=artifact_id, alias=alias)

    @classmethod
    def blank_vm(
        cls,
        simulator: str,
        alias: str | None = None,
        cpus: int = 1,
        memory: int = 2048,
        disk: int = 10240,
    ) -> EnvOption:
        """Create an EnvOption for a blank VM with custom resources."""
        return cls(
            simulator=simulator,
            alias=alias,
            sim_config=SimConfig(cpus=cpus, memory=memory, disk=disk),
        )
