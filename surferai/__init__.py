from pydantic import BaseModel
import requests
from typing import Any, Dict, Type, TypeVar, Optional, Union
from pydantic.fields import ModelField

SURFER_URL = "http://localhost:42069/"

class SurferAPIError(Exception):
    pass

T = TypeVar('T', bound=BaseModel)

def _make_request(method: str, endpoint: str, data: Dict[str, Any] = {}) -> Dict[str, Any]:
    url = f"{SURFER_URL}{endpoint}"
    try:
        if method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise SurferAPIError(f"API request failed: {str(e)}")

def convertToMarkdown(url: str, local: bool = False) -> Dict[str, Any]:
    """Convert a URL to Markdown using the Surfer API."""
    data = {"url": url, "local": local}
    return _make_request("POST", "convertToMarkdown", data)

def _get_openapi_type(field: ModelField) -> Dict[str, Any]:
    if field.outer_type_ == str:
        return {"type": "string"}
    elif field.outer_type_ == int:
        return {"type": "integer"}
    elif field.outer_type_ == float:
        return {"type": "number"}
    elif field.outer_type_ == bool:
        return {"type": "boolean"}
    elif field.outer_type_ == list:
        return {"type": "array", "items": {"type": "string"}}  # Assuming array of strings
    elif field.outer_type_ == dict:
        return {"type": "object"}
    elif isinstance(field.outer_type_, type) and issubclass(field.outer_type_, BaseModel):
        return {"$ref": f"#/components/schemas/{field.outer_type_.__name__}"}
    else:
        return {"type": "string"}  # Default to string for unknown types

def _create_openapi_schema(model: Type[T]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            field_name: _get_openapi_type(field)
            for field_name, field in model.__fields__.items()
        }
    }

def parseFromURL(url: str, schema: Union[Type[T], Dict[str, Any]]) -> Union[T, Dict[str, Any]]:
    """
    Parse structured data from a URL using the Surfer API and return an instance of the specified model or a dictionary.
    
    :param url: The URL to parse
    :param schema: Either a Pydantic model class or an OpenAPI schema dictionary
    :return: An instance of the Pydantic model or a dictionary matching the OpenAPI schema
    """
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        parsing_output = _create_openapi_schema(schema)
    elif isinstance(schema, dict):
        parsing_output = schema
    else:
        raise ValueError("Schema must be either a Pydantic model class or an OpenAPI schema dictionary")
    
    data = {"url": url, "local": False, "parsingOutput": parsing_output}
    result = _make_request("POST", "parseStructuredOutput", data)

    if result["success"]:
        print(result["structuredOutput"])
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            parsed_data = {}
            for field_name, field in schema.__fields__.items():
                value = result["structuredOutput"].get(field_name)
                if value is not None:
                    parsed_data[field_name] = field.type_(value)
                else:
                    parsed_data[field_name] = None
            return schema(**parsed_data)
        else:
            return result["structuredOutput"]
    else:
        raise SurferAPIError("Failed to parse structured output from URL")

# Example usage
if __name__ == "__main__":
    class StartupWebsite(BaseModel):
        company_mission: Optional[str]
        supports_sso: Optional[bool]
        is_open_source: Optional[bool]

        def __str__(self):
            return f"Company Mission: {self.company_mission}\nSupports SSO: {self.supports_sso}\nIs Open Source: {self.is_open_source}"

    # Using Pydantic model
    startup_data = parseFromURL("https://mendable.ai", StartupWebsite)
    print("Parsed startup data (Pydantic model):", startup_data)

    # Using OpenAPI schema
    openapi_schema = {
        "type": "object",
        "properties": {
            "github_social_link": {
                "type": "string"
            },
            "twitter_social_link": {
                "type": "string"
            },
            "discord_social_link": {
                "type": "string"
            }
        }
    }
    
    startup_data_dict = parseFromURL("https://docs.vapi.ai/assistants/dynamic-variables", openapi_schema)
    print("Parsed startup data (OpenAPI schema):", startup_data_dict)