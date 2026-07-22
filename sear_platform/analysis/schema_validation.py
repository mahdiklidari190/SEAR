"""Schema.org Validation."""
from __future__ import annotations

import json

from config.constants import SUPPORTED_SCHEMA_TYPES
from models.integrations import SchemaValidationResult
from models.page_data import PageData


class SchemaValidator:
    """Validate structured data schemas."""

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
        result = SchemaValidationResult()

        for raw in page.structured_data.raw_json:
            schemas = raw if isinstance(raw, list) else [raw]
            for schema in schemas:
                if not isinstance(schema, dict):
                    continue
                schema_type = schema.get("@type", "")
                if isinstance(schema_type, list):
                    schema_type = schema_type[0] if schema_type else ""

                if schema_type:
                    result.schemas_found.append(schema_type)

                    if schema_type in SUPPORTED_SCHEMA_TYPES:
                        # Check required fields
                        required = SchemaValidator.REQUIRED_FIELDS.get(schema_type, [])
                        missing = [f for f in required if f not in schema]
                        if missing:
                            result.invalid_schemas.append({
                                "type": schema_type,
                                "missing_fields": ", ".join(missing),
                            })
                        else:
                            result.valid_schemas.append(schema_type)
                    else:
                        result.valid_schemas.append(schema_type)

        # Check for missing recommended schemas
        found_types = set(result.schemas_found)
        if "Organization" not in found_types:
            result.missing_recommended.append("Organization schema recommended for brand")
        if "BreadcrumbList" not in found_types and page.breadcrumbs.found:
            result.missing_recommended.append("BreadcrumbList schema missing despite visible breadcrumbs")
        if "WebSite" not in found_types:
            result.missing_recommended.append("WebSite schema with SearchAction recommended")

        result.errors = page.structured_data.errors[:]
        return result