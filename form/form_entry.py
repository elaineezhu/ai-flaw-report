import streamlit as st
from typing import List, Callable, Optional, Dict, Any, Tuple
from enum import Enum, auto

class InputType(Enum):
    TEXT = auto()
    TEXT_AREA = auto()
    NUMBER = auto()
    RADIO = auto()
    SELECT = auto()
    MULTISELECT = auto()
    CHECKBOX = auto()
    DATE = auto()
    SELECT_SLIDER = auto()
    SEGMENTED_CONTROL = auto()

class FormEntry:
    """
    Class representing a single form entry/field with methods to 
    render it using various UI frameworks
    """
    
    def __init__(
        self,
        name: str,
        title: str,
        input_type: InputType,
        options: Optional[List[str]] = None,
        default: Any = None,
        help_text: str = "",
        info_text: str = "",
        required: bool = False,
        handler: Optional[Callable] = None,
        validation: Optional[Callable] = None,
        extra_params: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.title = title
        self.input_type = input_type
        self.options = options
        self.default = default
        self.help_text = help_text
        self.info_text = info_text
        self.required = required
        self.handler = handler
        self.validation = validation
        self.extra_params = extra_params or {}
        
    def to_streamlit(self, container=None) -> Any:
        """Render this field using Streamlit components"""
        # Use the container if provided, otherwise use st directly
        ui = container if container else st
        
        help_text = self.help_text
        if self.required:
            help_text = f"{help_text} (Required)" if help_text else "Required field"
            
        ui.markdown(f"**{self.title}**")
        
        if self.info_text:
            ui.caption(self.info_text)
            
        result = None
        
        if self.input_type == InputType.TEXT:
            result = ui.text_input(
                label="",
                value=self.default,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.TEXT_AREA:
            result = ui.text_area(
                label="",
                value=self.default,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.NUMBER:
            result = ui.number_input(
                label="",
                value=self.default if self.default is not None else 0,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.RADIO:
            if not self.options:
                raise ValueError(f"Options must be provided for {self.name} radio input")
            result = ui.radio(
                label="",
                options=self.options,
                index=self.options.index(self.default) if self.default in self.options else 0,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.SELECT:
            if not self.options:
                raise ValueError(f"Options must be provided for {self.name} select input")
            result = ui.selectbox(
                label="",
                options=self.options,
                index=self.options.index(self.default) if self.default in self.options else 0,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.MULTISELECT:
            if not self.options:
                raise ValueError(f"Options must be provided for {self.name} multiselect input")
            result = ui.multiselect(
                label="",
                options=self.options,
                default=self.default if self.default else [],
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.CHECKBOX:
            result = ui.checkbox(
                self.title,
                value=self.default if self.default is not None else False,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.DATE:
            result = ui.date_input(
                label="",
                value=self.default,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.SELECT_SLIDER:
            if not self.options:
                raise ValueError(f"Options must be provided for {self.name} select slider")
            result = ui.select_slider(
                label="",
                options=self.options,
                value=self.default if self.default else self.options[0],
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
            
        elif self.input_type == InputType.SEGMENTED_CONTROL:
            if not self.options:
                raise ValueError(f"Options must be provided for {self.name} segmented control")
            result = ui.segmented_control(
                label="",
                options=self.options,
                help=help_text,
                key=self.extra_params.get("key", self.name),
                **{k: v for k, v in self.extra_params.items() if k != "key"}
            )
        
        else:
            raise ValueError(f"Unsupported input type: {self.input_type}")
            
        return result
    
    def to_json_ld(self, value: Any) -> Tuple[str, Any]:
        """Convert the field and its value to a JSON-LD property name and value"""
        json_ld_name = self.name.lower().replace(" ", "_").replace("(", "").replace(")", "")
        return json_ld_name, value
    
    def validate(self, value: Any) -> Tuple[bool, Optional[str]]:
        """Validate the field value, return (is_valid, error_message)"""
        if self.required and (value is None or value == "" or (isinstance(value, list) and len(value) == 0)):
            return False, f"{self.title} is required"
        
        if self.validation:
            return self.validation(value)
            
        return True, None