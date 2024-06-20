from pydantic import BaseModel
import requests
from typing import Any, Dict, Type, TypeVar, Optional

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
    """
    Convert a URL to Markdown using the Surfer API.

    Args:
        url (str): The URL to convert to Markdown.
        local (bool, optional): Whether to use a local version of the page. Defaults to False.

    Returns:
        Dict[str, Any]: A dictionary containing the conversion result, including 'success', 'markdown', and 'metadata' fields.

    Raises:
        SurferAPIError: If the API request fails.
    """
    data = {"url": url, "local": local}
    return _make_request("POST", "convertToMarkdown", data)

def parseFromURL(url: str, model: Type[T]) -> T:
    """
    Parse structured data from a URL using the Surfer API and return an instance of the specified model.

    Args:
        url (str): The URL to parse.
        model (Type[T]): The Pydantic model class to use for parsing the structured output.

    Returns:
        T: An instance of the specified model populated with the parsed data.

    Raises:
        SurferAPIError: If the API request fails or if parsing is unsuccessful.
    """
    parsing_output = {
        "type": "object",
        "properties": {field: {"type": "string"} for field in model.__annotations__}
    }
    data = {"url": url, "local": False, "parsingOutput": parsing_output}
    result = _make_request("POST", "parseStructuredOutput", data)
    
    if result["success"]:
        print(result["structuredOutput"])
        parsed_data = {}
        for field, field_type in model.__annotations__.items():
            parsed_data[field] = result["structuredOutput"].get(field)
            if not isinstance(parsed_data[field], field_type):
                parsed_data[field] = None
        return model(**parsed_data)
    else:
        raise SurferAPIError("Failed to parse structured output from URL")

# Example usage
if __name__ == "__main__":
    # Example of convertToMarkdown
    # markdown_result = convertToMarkdown("https://example.com")
    # print("Markdown conversion:", markdown_result)

    # Example of parseFromURL
    class StartupWebsite(BaseModel):
        company_mission: Optional[str]
        supports_sso: Optional[bool]
        is_open_source: Optional[bool]

        def __str__(self):
            return f"Company Mission: {self.company_mission}\nSupports SSO: {self.supports_sso}\nIs Open Source: {self.is_open_source}"

    startup_data = parseFromURL("https://mendable.ai", StartupWebsite)
    print("Parsed startup data:", startup_data)