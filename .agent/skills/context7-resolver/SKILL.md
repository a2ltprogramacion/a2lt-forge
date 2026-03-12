---
name: context7-resolver
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integrates the context7 MCP server for searching updated documentation and real code examples.
  Activate automatically in Code Gen (Step 4 of La Forja) if there are external dependencies, or manually
  when encountering obsolete code or model hallucinations.
  Trigger phrases: "busca documentación", "resuelve contexto de la librería", "verifica versión en context7",
  "cómo se usa la API de", "find docs context7".
  Do NOT activate for logic unrelated to third-party libraries (use rag-query).

triggers:
  primary: ["docs en context7", "verifica la api de", "cómo usar la librería"]
  secondary: ["resuelve contexto código", "ejemplos de código actualizados"]
  context: ["paso 4 de la forja", "dependencia externa nueva", "evitar alucinaciones"]
dependencies: []
framework_version: ">=2.3.0"
---

# Context7 Resolver — Instant Documentation Extractor

**Role:** You are the dedicated liaison with the `context7` MCP server. Your objective is to ensure that all code generated in La Forja for third-party libraries (Astro, Tailwind, Django, SDKs) is based on the most recent official documentation, eliminating structural hallucinations.

This is a **High Freedom** component. It does not contain external scripts since the orchestrator has native access to the `context7` MCP server tools. Its purpose is to dictate the *doctrine* for using these tools within La Forja.

---

## 1. When to Activate (Trigger Conditions)

You must routinely invoke this skill during:
- **Step 4 (Code Gen) of any Forge:** If the component to be generated imports tools, libraries, or SDKs that you do not master 100% in their most current declared version.
- **API Error Troubleshooting:** When a pre-existing function breaks due to a TypeError or deprecation ("Module not found", "Property does not exist on type").
- **Explicit operator request:** When requested to review "how it's done in the latest version" of a utility.

---

## 2. Mandatory Operating Flow (MCP Usage)

To obtain the necessary information from context7, you must always execute this strict 2-step sequence:

### Step 1: `resolve-library-id`
**Objective:** Obtain the official ID recognized by context7. NEVER assume the ID of a library.
1. Make a call to the MCP tool `mcp_context7_resolve-library-id`.
2. Provide:
   - `libraryName`: General name of the library (e.g., "Astro", "TailwindCSS", "Next.js").
   - `query`: What you are trying to do (e.g., "How to use ViewTransitions", "Theming configuration").
3. Receive the list of results. Evaluate the reputation score, snippet coverage, and select the most precise ID (in `/org/project` or `/org/project/version` format).

### Step 2: `query-docs`
**Objective:** Extract the technical specification.
1. Use the ID obtained in the previous step.
2. Make a call to `mcp_context7_query-docs`.
3. Provide:
   - `libraryId`: The exact retrieved ID (`/vercel/next.js`).
   - `query`: Your highly specific question. Be concrete.
     - *BAD:* "auth"
     - *GOOD:* "How to implement JWT authentication and refresh tokens at the edge with middleware".
4. **Critical Restriction:** If you do not find the answer, you can call this tool up to a maximum of **3 times per question session** by rephrasing the query. After that, operate with the best available information.

---

## 3. Code Injection Protocol (Anti-Hallucinations)

Once the response from context7 is obtained:
1. **Incompatibility Audit:** Compare the pattern returned by context7 against the A2LT base stack in `[CONTEXT §3.2]` (e.g., if `query-docs` returns code for React but the environment is Astro, logically transpile the architecture to the target environment, do not copy and paste).
2. **Implementation:** When injecting the code into your artifact or document, include a brief comment (header or alert) indicating that this pattern is based on dynamically obtained context7 specifications:
   `// Implementation validated via context7 (Latest version)`

---

## 4. Limitations and Warnings

- **Security:** NEVER send passwords, API keys (such as GoHighLevel keys), or private tokens within the `query` parameter to `context7`. It is an external network.
- **Redundancy:** Avoid resorting to context7 for standard Python native components (`os`, `json`, `datetime`) or basic HTML5 tags unless it's an edge case.
- **Operational Silence:** When using this skill in the middle of a Core Flow (e.g., Code Gen), it is not necessary to announce it in detail to the operator. Simply obtain the data and write the resulting perfect code.
