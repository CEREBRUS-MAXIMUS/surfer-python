from pydantic import BaseModel, Field
import requests
from typing import Any, Dict, Type, TypeVar, Optional, Union

SURFER_URL = "http://api.surfsup.ai/"
SURFER_LOCAL_URL = "http://localhost:42069/"

class SurferAPIError(Exception):
    pass

T = TypeVar('T', bound=BaseModel)

def _make_request(method: str, endpoint: str, data: Dict[str, Any] = {}, local: bool = False) -> Dict[str, Any]:
    base_url = SURFER_LOCAL_URL if local else SURFER_URL
    url = f"{base_url}{endpoint}"
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
    data = {"url": url}
    return _make_request("POST", "convertToMarkdown", data, local)

def _get_openapi_type(field: Field) -> Dict[str, Any]:
    if field.annotation == str:
        return {"type": "string"}
    elif field.annotation == int:
        return {"type": "integer"}
    elif field.annotation == float:
        return {"type": "number"}
    elif field.annotation == bool:
        return {"type": "boolean"}
    elif field.annotation == list:
        return {"type": "array", "items": {"type": "string"}}  # Assuming array of strings
    elif field.annotation == dict:
        return {"type": "object"}
    elif isinstance(field.annotation, type) and issubclass(field.annotation, BaseModel):
        return {"$ref": f"#/components/schemas/{field.annotation.__name__}"}
    else:
        return {"type": "string"}  # Default to string for unknown types

def _create_openapi_schema(model: Type[T]) -> Dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            field_name: _get_openapi_type(field)
            for field_name, field in model.model_fields.items()
        }
    }

def parseFromURL(url: str, schema: Union[Type[T], Dict[str, Any]], local: bool = False) -> Union[T, Dict[str, Any]]:
    """
    Parse structured data from a URL using the Surfer API and return an instance of the specified model or a dictionary.
    
    :param url: The URL to parse
    :param schema: Either a Pydantic model class or an OpenAPI schema dictionary
    :param local: Whether to use the local API endpoint
    :return: An instance of the Pydantic model or a dictionary matching the OpenAPI schema
    """
    if isinstance(schema, type) and issubclass(schema, BaseModel):
        parsing_output = _create_openapi_schema(schema)
    elif isinstance(schema, dict):
        parsing_output = schema
    else:
        raise ValueError("Schema must be either a Pydantic model class or an OpenAPI schema dictionary")
    
    data = {"url": url, "parsingOutput": parsing_output}
    result = _make_request("POST", "parseStructuredOutput", data, local)

    if result["success"]:
        print(result["structuredOutput"])
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            return schema.model_validate(result["structuredOutput"])
        else:
            return result["structuredOutput"]
    else:
        raise SurferAPIError("Failed to parse structured output from URL")

# Example usage
if __name__ == "__main__":
    class StartupWebsite(BaseModel):
        company_mission: Optional[str] = None
        supports_sso: Optional[bool] = None
        is_open_source: Optional[bool] = None

        def __str__(self):
            return f"Company Mission: {self.company_mission}\nSupports SSO: {self.supports_sso}\nIs Open Source: {self.is_open_source}"

    # Using Pydantic model
    startup_data = parseFromURL("https://mendable.ai", StartupWebsite, local=True)
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
    
    startup_data_dict = parseFromURL("https://docs.vapi.ai/assistants/dynamic-variables", openapi_schema, local=True)
    print("Parsed startup data (OpenAPI schema):", startup_data_dict)