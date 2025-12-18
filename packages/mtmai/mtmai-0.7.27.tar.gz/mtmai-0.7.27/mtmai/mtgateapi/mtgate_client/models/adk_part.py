from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.adk_blob import AdkBlob
    from ..models.adk_code_execution_result import AdkCodeExecutionResult
    from ..models.adk_executable_code import AdkExecutableCode
    from ..models.adk_file_data import AdkFileData
    from ..models.adk_function_call import AdkFunctionCall
    from ..models.adk_function_resp import AdkFunctionResp


T = TypeVar("T", bound="AdkPart")


@_attrs_define
class AdkPart:
    """
    Attributes:
        text (str | Unset):
        inline_data (AdkBlob | Unset):
        function_call (AdkFunctionCall | Unset):
        function_response (AdkFunctionResp | Unset):
        thought (bool | Unset):
        file_data (AdkFileData | Unset):
        executable_code (AdkExecutableCode | Unset):
        code_execution_result (AdkCodeExecutionResult | Unset):
    """

    text: str | Unset = UNSET
    inline_data: AdkBlob | Unset = UNSET
    function_call: AdkFunctionCall | Unset = UNSET
    function_response: AdkFunctionResp | Unset = UNSET
    thought: bool | Unset = UNSET
    file_data: AdkFileData | Unset = UNSET
    executable_code: AdkExecutableCode | Unset = UNSET
    code_execution_result: AdkCodeExecutionResult | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        inline_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.inline_data, Unset):
            inline_data = self.inline_data.to_dict()

        function_call: dict[str, Any] | Unset = UNSET
        if not isinstance(self.function_call, Unset):
            function_call = self.function_call.to_dict()

        function_response: dict[str, Any] | Unset = UNSET
        if not isinstance(self.function_response, Unset):
            function_response = self.function_response.to_dict()

        thought = self.thought

        file_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.file_data, Unset):
            file_data = self.file_data.to_dict()

        executable_code: dict[str, Any] | Unset = UNSET
        if not isinstance(self.executable_code, Unset):
            executable_code = self.executable_code.to_dict()

        code_execution_result: dict[str, Any] | Unset = UNSET
        if not isinstance(self.code_execution_result, Unset):
            code_execution_result = self.code_execution_result.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if text is not UNSET:
            field_dict["text"] = text
        if inline_data is not UNSET:
            field_dict["inlineData"] = inline_data
        if function_call is not UNSET:
            field_dict["functionCall"] = function_call
        if function_response is not UNSET:
            field_dict["functionResponse"] = function_response
        if thought is not UNSET:
            field_dict["thought"] = thought
        if file_data is not UNSET:
            field_dict["fileData"] = file_data
        if executable_code is not UNSET:
            field_dict["executableCode"] = executable_code
        if code_execution_result is not UNSET:
            field_dict["codeExecutionResult"] = code_execution_result

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.adk_blob import AdkBlob
        from ..models.adk_code_execution_result import AdkCodeExecutionResult
        from ..models.adk_executable_code import AdkExecutableCode
        from ..models.adk_file_data import AdkFileData
        from ..models.adk_function_call import AdkFunctionCall
        from ..models.adk_function_resp import AdkFunctionResp

        d = dict(src_dict)
        text = d.pop("text", UNSET)

        _inline_data = d.pop("inlineData", UNSET)
        inline_data: AdkBlob | Unset
        if isinstance(_inline_data, Unset):
            inline_data = UNSET
        else:
            inline_data = AdkBlob.from_dict(_inline_data)

        _function_call = d.pop("functionCall", UNSET)
        function_call: AdkFunctionCall | Unset
        if isinstance(_function_call, Unset):
            function_call = UNSET
        else:
            function_call = AdkFunctionCall.from_dict(_function_call)

        _function_response = d.pop("functionResponse", UNSET)
        function_response: AdkFunctionResp | Unset
        if isinstance(_function_response, Unset):
            function_response = UNSET
        else:
            function_response = AdkFunctionResp.from_dict(_function_response)

        thought = d.pop("thought", UNSET)

        _file_data = d.pop("fileData", UNSET)
        file_data: AdkFileData | Unset
        if isinstance(_file_data, Unset):
            file_data = UNSET
        else:
            file_data = AdkFileData.from_dict(_file_data)

        _executable_code = d.pop("executableCode", UNSET)
        executable_code: AdkExecutableCode | Unset
        if isinstance(_executable_code, Unset):
            executable_code = UNSET
        else:
            executable_code = AdkExecutableCode.from_dict(_executable_code)

        _code_execution_result = d.pop("codeExecutionResult", UNSET)
        code_execution_result: AdkCodeExecutionResult | Unset
        if isinstance(_code_execution_result, Unset):
            code_execution_result = UNSET
        else:
            code_execution_result = AdkCodeExecutionResult.from_dict(_code_execution_result)

        adk_part = cls(
            text=text,
            inline_data=inline_data,
            function_call=function_call,
            function_response=function_response,
            thought=thought,
            file_data=file_data,
            executable_code=executable_code,
            code_execution_result=code_execution_result,
        )

        adk_part.additional_properties = d
        return adk_part

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
