This folder contains the generated OpenAPI specification for the backend.

To regenerate:
- Ensure the FastAPI app imports successfully.
- Run: `python -m src.api.generate_openapi`
- The file `openapi.json` will be overwritten with the latest schema.

Note: The development server at /docs will also reflect the current API schema.
