# Third-Party Licenses / Notices

This file documents third-party components included or generated within this
repository whose licenses are independent from the project's main license
(GNU GPLv3).

---

## `aqdr-ui/grafana-initialization/` (`grafana_client` package)

**Origin:** The code in this directory is **automatically generated** using
[OpenAPI Generator](https://openapi-generator.tech) (v7.6.0-SNAPSHOT,
`python` generator), from the OpenAPI specification published by the Grafana
project:

- Spec source: `public/openapi3.json`
- Origin repository: https://github.com/grafana/grafana
- Reference version used: `v11.4.0`
  (https://raw.githubusercontent.com/grafana/grafana/refs/tags/v11.4.0/public/openapi3.json)

**License of the source material:** Grafana (https://github.com/grafana/grafana)
is distributed under the **AGPL-3.0-only** license by default, as stated in
the project's own
[`LICENSING.md`](https://github.com/grafana/grafana/blob/main/LICENSING.md).
The `public/openapi3.json` file is not listed among the directories exempted
under Apache-2.0, and therefore falls under the project's default license:
**AGPL-3.0-only**.

- Copyright: Grafana Labs
- Full license text: https://www.gnu.org/licenses/agpl-3.0.txt

**Nature of the generated code:** The files in this directory (Python classes,
models, HTTP client, etc.) are a mechanical transformation of the OpenAPI
specification above, produced by a third-party tool (OpenAPI Generator,
licensed under Apache-2.0:
https://github.com/OpenAPITools/openapi-generator/blob/master/LICENSE).
They have not been manually written or modified by Bull SAS, and therefore **do not carry the project's own K-HEALTHinAIR
copyright header**.

**Treatment within this project:**
- This directory is treated as a **third-party / vendored component**, not
  as original project code.
- It is kept unmodified with respect to its licensing terms of origin.
- Its inclusion in a project distributed under GPLv3 is done on the
  understanding that AGPL-3.0 and GPLv3 are compatible for combination
  (AGPL-3.0 explicitly permits combining with code under GPLv3 "or later"),
  although the resulting combined work remains subject to AGPL-3.0 terms with
  respect to this component.

**To regenerate this client:**
```bash
docker run --rm --volume /temp:/out \
docker.io/openapitools/openapi-generator-cli generate \
--generator-name python \
--input-spec /out/openapi3.yaml \
--output "/out" \
--package-name "khealthinair_grafana_client" \
--additional-properties="generateSourceCodeOnly=true,projectName=khealthinair,dateFormat=%d/%m/%Y"
```

---
