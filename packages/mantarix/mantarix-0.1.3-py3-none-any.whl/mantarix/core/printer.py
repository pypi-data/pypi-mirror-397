from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Union, List

import json

from mantarix.core.constrained_control import Control
from mantarix.core.ref import Ref

class PrinterPageFormat(Enum):
    A3 = "a3"
    A4 = "a4"
    A5 = "a5"
    A6 = "a6"
    LETTER = "letter"
    LEGAL = "legal"
    ROLL57 = "roll57"
    ROLL80 = "roll80"
    STANDARD = "standard"
    UNDEFINED = "undefined"

class PrinterOutputType(Enum):
    GENERIC = "generic"
    GRAYSCALE = "grayscale"
    PHOTO = "photo"
    PHOTO_GRAYSCALE = "photoGrayscale"

@dataclass(frozen=True)
class PrinterDevice:
    url: str
    name: str
    model: Optional[str] = None
    location: Optional[str] = None
    comment: Optional[str] = None
    isDefault: bool = field(default=False)
    isAvailable: bool = field(default=True)

    def __post_init__(self):
        if self.name is None:
            object.__setattr__(self, "name", self.url)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrinterDevice":
        return cls(
            url=data.get("url"),
            name=data.get("name", data.get("url")),
            model=data.get("model"),
            location=data.get("location"),
            comment=data.get("comment"),
            isDefault=data.get("default", False),
            isAvailable=data.get("available", True)
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self.url,
            "name": self.name,
            "model": self.model,
            "location": self.location,
            "comment": self.comment,
            "default": self.isDefault,
            "available": self.isAvailable,
        }

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__} {self.name}\n"
            f"  url: {self.url}\n"
            f"  location: {self.location}\n"
            f"  model: {self.model}\n"
            f"  comment: {self.comment}\n"
            f"  isDefault: {self.isDefault}\n"
            f"  isAvailable: {self.isAvailable}"
        )

class Printer(Control):
    def __init__(
        self,
        ref: Optional[Ref] = None,
        data: Any = None,
    ):
        Control.__init__(
            self,
            ref=ref,
            data=data,
        )
    
    def _get_control_name(self):
        return "printer"
    
    def print(self, filePath:str, name:str="Document", format:PrinterPageFormat=PrinterPageFormat.STANDARD,dynamicLayout:bool=True, usePrinterSettings:bool=False, type:PrinterOutputType=PrinterOutputType.GENERIC, forceCustomPrintPaper:bool=False) -> Union[bool, str, None]:
        out = self.invoke_method(
            "print",
            arguments={
                "filePath": str(filePath),
                "name": str(name),
                "format": str(format.value),
                "dynamicLayout": str(dynamicLayout),
                "usePrinterSettings": str(usePrinterSettings),
                "type": str(type.value),
                "forceCustomPrintPaper": str(forceCustomPrintPaper),
            },
            wait_for_result=True,
            wait_timeout=None
        )
        if out == "ok":
            return True
        return out
    
    def directprint(self, printer:PrinterDevice, filePath:str, name:str="Document", format:PrinterPageFormat=PrinterPageFormat.STANDARD,dynamicLayout:bool=True, usePrinterSettings:bool=False, type:PrinterOutputType=PrinterOutputType.GENERIC, forceCustomPrintPaper:bool=False) -> Union[bool, str, None]:
        out = self.invoke_method(
            "directprint",
            arguments={
                "printer": json.dumps(printer.to_dict()),
                "filePath": str(filePath),
                "name": str(name),
                "format": str(format.value),
                "dynamicLayout": str(dynamicLayout),
                "usePrinterSettings": str(usePrinterSettings),
                "type": str(type.value),
                "forceCustomPrintPaper": str(forceCustomPrintPaper),
            },
            wait_for_result=True,
            wait_timeout=None
        )
        if out == "ok":
            return True
        return out
    
    def pickprinter(self) -> Union[PrinterDevice, None]:
        out = self.invoke_method(
            "pickprinter",
            wait_for_result=True,
            wait_timeout=None
        )
        try:
            printer = json.loads(str(out))
            if isinstance(printer, dict):
                return PrinterDevice.from_dict(printer)
            return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def getlistofprinters(self) -> Optional[List[PrinterDevice]]:
        out = self.invoke_method(
            "getlistofprinters",
            wait_for_result=True,
            wait_timeout=None
        )
        try:
            printers = json.loads(str(out))
            if isinstance(printers, list):
                return [PrinterDevice.from_dict(printer) for printer in printers]
            else:
                return None
        except (json.JSONDecodeError, TypeError):
            return None
    
    def share(self, filePath:str, name:str="Document.pdf", subject:str=None, body:str=None) -> Union[bool, str, None]:
        args = {
            "filePath": str(filePath),
            "name": str(name),
        }
        if subject is not None:
            args["subject"] = str(subject)
        if body is not None:
            args["body"] = str(body)
        out = self.invoke_method(
            "share",
            arguments=args,
            wait_for_result=True,
            wait_timeout=None
        )
        if out == "ok":
            return True
        return out