"""Schema.org Validation."""
from __future__ import annotations

import json

# Import constants defining which schema types are officially supported and actively checked by this system.
from config.constants import SUPPORTED_SCHEMA_TYPES
# Import the data model used to structure the validation report.
from models.integrations import SchemaValidationResult
# Import the core page data model containing the extracted structured data.
from models.page_data import PageData


class SchemaValidator:
    """Validate structured data schemas against SEO best practices and schema.org requirements."""

    # Define the mandatory fields for common schema types. 
    # Missing these fields can prevent search engines from generating rich results for the content.
    REQUIRED_FIELDS: dict[str, list[str]] = {
        "Organization": ["name", "url"],
        "Article": ["headline", "author", "datePublished"],
        "FAQPage": ["mainEntity"],
        "HowTo": ["name", "step"],
        "BreadcrumbList": ["itemListElement"],
        "Product": ["name"],
        "Review": ["author", "reviewRating"],
        "Event": ["name", "startDate"],
        "LocalBusiness": ["name", "address"],
        "Person": ["name"],
        "VideoObject": ["name", "description", "thumbnailUrl"],
        "WebSite": ["name", "url"],
    }

    @staticmethod
    def validate(page: PageData) -> SchemaValidationResult:
        # Initialize the result object that will hold the validation findings.
        result = SchemaValidationResult()

        # Iterate through all raw JSON-LD blocks extracted from the page.
        for raw in page.structured_data.raw_json:
            # JSON-LD can be a single object or an array of objects (e.g., using @graph). 
            # Normalize to a list for uniform processing.
            schemas = raw if isinstance(raw, list) else [raw]
            
            for schema in schemas:
                # Skip any malformed entries that are not dictionaries.
                if not isinstance(schema, dict):
                    continue
                    
                # Extract the schema type. It can be a string or a list of strings (multiple types for one entity).
                schema_type = schema.get("@type", "")
                if isinstance(schema_type, list):
                    schema_type = schema_type[0] if schema_type else ""

                # If a valid type is identified, record it in the found schemas list.
                if schema_type:
                    result.schemas_found.append(schema_type)

                    # If the schema type is one we actively monitor, validate its required fields.
                    if schema_type in SUPPORTED_SCHEMA_TYPES:
                        required = SchemaValidator.REQUIRED_FIELDS.get(schema_type, [])
                        # Identify any mandatory fields that are missing from the current schema object.
                        missing = [f for f in required if f not in schema]
                        
                        if missing:
                            # Log the schema as invalid and specify which fields are missing.
                            result.invalid_schemas.append({
                                "type": schema_type,
                                "missing_fields": ", ".join(missing),
                            })
                        else:
                            # All required fields are present; mark as valid.
                            result.valid_schemas.append(schema_type)
                    else:
                        # For unsupported but recognized schema types, we still count them as validly formatted.
                        result.valid_schemas.append(schema_type)

        # Perform strategic checks for highly recommended schemas that are missing from the page.
        found_types = set(result.schemas_found)
        
        if "Organization" not in found_types:
            result.missing_recommended.append("Organization schema recommended for brand")
            
        if "BreadcrumbList" not in found_types and page.breadcrumbs.found:
            result.missing_recommended.append("BreadcrumbList schema missing despite visible breadcrumbs")
            
        if "WebSite" not in found_types:
            result.missing_recommended.append("WebSite schema with SearchAction recommended")

        # Propagate any syntax or parsing errors that were detected during the initial JSON extraction.
        result.errors = page.structured_data.errors[:]
        
        return result