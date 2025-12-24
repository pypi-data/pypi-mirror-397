from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.diagnostics_dto import DiagnosticsDto
    from ..models.geoteknisk_unders import GeotekniskUnders


T = TypeVar("T", bound="ValidatedGeotekniskUnders")


@_attrs_define
class ValidatedGeotekniskUnders:
    """GeotekniskUnders med valideringsresultat

    Attributes:
        geoteknisk_unders (GeotekniskUnders | Unset): geografisk område hvor det finnes eller er planlagt geotekniske
            borehull tilhørende et gitt prosjekt <engelsk>geographical area where there are or are planned geotechnical
            boreholes for a given project</engelsk>
        diagnostics (DiagnosticsDto | Unset): A Dto for Diagnostic instances, with a list of DiagnosticDto instances.
        status (str | Unset):
    """

    geoteknisk_unders: GeotekniskUnders | Unset = UNSET
    diagnostics: DiagnosticsDto | Unset = UNSET
    status: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        geoteknisk_unders: dict[str, Any] | Unset = UNSET
        if not isinstance(self.geoteknisk_unders, Unset):
            geoteknisk_unders = self.geoteknisk_unders.to_dict()

        diagnostics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.diagnostics, Unset):
            diagnostics = self.diagnostics.to_dict()

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if geoteknisk_unders is not UNSET:
            field_dict["geotekniskUnders"] = geoteknisk_unders
        if diagnostics is not UNSET:
            field_dict["diagnostics"] = diagnostics
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.diagnostics_dto import DiagnosticsDto
        from ..models.geoteknisk_unders import GeotekniskUnders

        d = dict(src_dict)
        _geoteknisk_unders = d.pop("geotekniskUnders", UNSET)
        geoteknisk_unders: GeotekniskUnders | Unset
        if isinstance(_geoteknisk_unders, Unset):
            geoteknisk_unders = UNSET
        else:
            geoteknisk_unders = GeotekniskUnders.from_dict(_geoteknisk_unders)

        _diagnostics = d.pop("diagnostics", UNSET)
        diagnostics: DiagnosticsDto | Unset
        if isinstance(_diagnostics, Unset):
            diagnostics = UNSET
        else:
            diagnostics = DiagnosticsDto.from_dict(_diagnostics)

        status = d.pop("status", UNSET)

        validated_geoteknisk_unders = cls(
            geoteknisk_unders=geoteknisk_unders,
            diagnostics=diagnostics,
            status=status,
        )

        validated_geoteknisk_unders.additional_properties = d
        return validated_geoteknisk_unders

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
