import surferai
from pydantic import BaseModel
from typing import Optional



# markdown_result = convertToMarkdown("https://example.com")
# print("Markdown conversion:", markdown_result)

# Example of parseFromURL
class StartupWebsite(BaseModel):
    company_mission: Optional[str]
    supports_sso: Optional[bool]
    is_open_source: Optional[bool]

    #A nice to string method
    def __str__(self):
        return f"Company Mission: {self.company_mission}\nSupports SSO: {self.supports_sso}\nIs Open Source: {self.is_open_source}"

startup_data = parseFromURL("https://mendable.ai", StartupWebsite)
print("Parsed startup data:", startup_data)