from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    Any,
    TypeVar,
    Union,
)

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.subscribe_mode import SubscribeMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.agent_output import AgentOutput


T = TypeVar("T", bound="PeerOptionsAgent")


@_attrs_define
class PeerOptionsAgent:
    """Options specific to the Agent peer

    Attributes:
        output (Union[Unset, AgentOutput]): Output audio options
        subscribe_mode (Union[Unset, SubscribeMode]): Configuration of peer's subscribing policy
    """

    output: Union[Unset, "AgentOutput"] = UNSET
    subscribe_mode: Union[Unset, SubscribeMode] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        output: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.output, Unset):
            output = self.output.to_dict()

        subscribe_mode: Union[Unset, str] = UNSET
        if not isinstance(self.subscribe_mode, Unset):
            subscribe_mode = self.subscribe_mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if output is not UNSET:
            field_dict["output"] = output
        if subscribe_mode is not UNSET:
            field_dict["subscribeMode"] = subscribe_mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.agent_output import AgentOutput

        d = dict(src_dict)
        _output = d.pop("output", UNSET)
        output: Union[Unset, AgentOutput]
        if isinstance(_output, Unset):
            output = UNSET
        else:
            output = AgentOutput.from_dict(_output)

        _subscribe_mode = d.pop("subscribeMode", UNSET)
        subscribe_mode: Union[Unset, SubscribeMode]
        if isinstance(_subscribe_mode, Unset):
            subscribe_mode = UNSET
        else:
            subscribe_mode = SubscribeMode(_subscribe_mode)

        peer_options_agent = cls(
            output=output,
            subscribe_mode=subscribe_mode,
        )

        peer_options_agent.additional_properties = d
        return peer_options_agent

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
