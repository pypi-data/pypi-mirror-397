from dataclasses import dataclass


@dataclass(frozen=True)
class ChannelPolicy:
    name: str                 # e.g. "10-20-minimal"
    strict: bool = False      # error vs warn


# Built-in policies
TEN_TWENTY_MINIMAL = ChannelPolicy(
    name="10-20-minimal",
    strict=False
)