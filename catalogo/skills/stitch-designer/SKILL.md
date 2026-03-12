---
name: stitch-designer
version: 1.0.0
type: utility
subtype: skill
tier: all
description: "Orchestrates and designs user interfaces using the StitchMCP server tools."
triggers:
  primary: [diseña pantalla, usa stitch, genera ui, crea proyecto ux]
  secondary: [edita pantalla interactiva, StitchMCP]
  context: [ui design, mockup generation]
dependencies: []
framework_version: ">=2.3.0"
---

# Stitch Designer

This skill provides instructions on how to efficiently operate the **StitchMCP** server for the creation and management of user interfaces and UI projects.

## 0. Prerrequisitos
- The `StitchMCP` server MUST be active and accessible via natural language tools.

## 1. Flujo de Trabajo (Mandatory Protocol)

1. **Context Recognition:**
   - Start by evaluating if the user already has projects by calling `mcp_StitchMCP_list_projects`.

2. **Screen Generation:**
   - Use `mcp_StitchMCP_generate_screen_from_text`.
   - Requirements: `projectId` and an explicit `prompt`.
   - Consider passing `deviceType` (MOBILE, DESKTOP, TABLET).

3. **Screen Verification and Recovery:**
   - The generation process can be asynchronous and may take time. If a temporary connection failure occurs, **DO NOT RETRY**. The server will complete the generation in the background.
   - Use `mcp_StitchMCP_list_screens` with the `projectId` to confirm which screens have been generated.

4. **Design Iteration:**
   - Selective editing: Use `mcp_StitchMCP_edit_screens` (requires `projectId`, `selectedScreenIds` and `prompt`).
   - Alternative generation: Use `mcp_StitchMCP_generate_variants` specifying the corresponding `variantOptions`.

## 2. Reglas de Diseño de Prompts (Stitch UI)
When the operator requests to generate a UI, assist by defining a deep architectural prompt:
- **Rich Aesthetics:** Avoid basic colors. Recommend color palettes (HSL, HEX), Dark Modes or nuanced shades.
- **Typography and Layout:** Specify modern typography (Inter, Roboto, Outfit) and visual frameworks.
- **Animation:** If applicable, describe hover states or micro-animations within the prompt to the MCP.

## 3. Condiciones de Parada (Stop-Loss)
- If the MCP tool is not listed or connected, stop execution and ask the operator to start it.
- Never assume raw IDs (for projects or screens) without previously listing them or asking the user.

