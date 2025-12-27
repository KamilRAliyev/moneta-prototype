# Business Logic Documentation

This folder contains detailed documentation of complex business logic flows in the Moneta application.

## Contents

### [Date Lock Logic](./Date%20Lock%20Logic.md)
Documents how date locking works to mark already-ingested date ranges. Includes:
- Core concept and behavior
- Logic flow diagrams
- Examples and edge cases
- Validation rules

### [CSV Metadata Extraction](./CSV%20Metadata%20Extraction.md)
Documents the automatic metadata extraction process for uploaded CSV files. Includes:
- Extraction flow
- Date column detection
- Date format inference
- Error handling

### [Statement File Upload](./Statement%20File%20Upload.md)
Documents the atomic file upload process with duplicate detection. Includes:
- Upload flow
- Atomic operation guarantee
- Duplicate detection logic
- Error recovery

## Diagram Conventions

All mermaid diagrams in this folder follow these conventions:

- **Green nodes** (`#d1fae5`) - Success/Valid states
- **Red nodes** (`#fee2e2`) - Error/Invalid states
- **Blue nodes** (`#dbeafe`) - Information/Neutral states
- **Diamond shapes** - Decision points
- **Rectangles** - Process steps
- **Dashed lines** - Error paths

## Adding New Documentation

When documenting new business logic:

1. Create a new markdown file in this folder
2. Include a clear overview section
3. Use mermaid diagrams for complex flows
4. Provide examples and edge cases
5. Link to related components
6. Update this README

## Related Documentation

- [Architecture Documentation](../Architecture/) - System architecture and structure
- [Issues](../Issues/) - Feature specifications and requirements
- [Notes](../Notes/) - Development notes and checklists
