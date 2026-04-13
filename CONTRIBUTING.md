# Contributing to email-security-world-requirements

Thank you for helping document the global email security landscape! This guide explains how to add or update country data.

---

## Table of Contents

- [Adding a New Country](#adding-a-new-country)
- [Updating Existing Data](#updating-existing-data)
- [Data Quality Standards](#data-quality-standards)
- [Running Validation Locally](#running-validation-locally)
- [Pull Request Checklist](#pull-request-checklist)
- [What Counts as a Valid Source?](#what-counts-as-a-valid-source)
- [Frequently Asked Questions](#frequently-asked-questions)

---

## Adding a New Country

1. **Copy the template:**

   ```bash
   cp data/countries/_template.yaml data/countries/XX.yaml
   ```

   Replace `XX` with the [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) country code (uppercase). For example: `DE` for Germany, `JP` for Japan, `NO` for Norway.

2. **Fill in the required fields:**

   - `country_code` — must match the filename (e.g., `DE`)
   - `country_name` — full English name
   - `last_reviewed` — today's date in `YYYY-MM-DD` format
   - `requirements` — at least one standard entry

3. **For each standard entry, set:**

   - `standard` — one of: `SPF`, `DKIM`, `DMARC`, `DANE`, `MTA-STS`, `TLS-RPT`, `BIMI`, `STARTTLS`
   - `status` — see the Status Values table below
   - `applies_to` — see the Applies-To Values table below
   - `references` — **required** if status is `mandatory` or `recommended`

4. **Status Values:**

   | Status | When to use |
   |---|---|
   | `mandatory` | Legally or policy-required — non-compliance has consequences |
   | `recommended` | Explicit official guidance or best-practice document exists |
   | `informational` | Mentioned in an official document without a clear directive |
   | `none` | Explicitly confirmed as not required |
   | `unknown` | You searched but found no official information |

5. **Applies-To Values:**

   | Value | Meaning |
   |---|---|
   | `all_organizations` | All organisations in the country |
   | `government_agencies` | Government/public sector in general |
   | `federal_agencies` | Federal-level agencies specifically |
   | `state_agencies` | State/provincial/regional agencies |
   | `critical_infrastructure` | Operators of critical infrastructure (energy, water, health, etc.) |
   | `financial_sector` | Banks and financial institutions |
   | `healthcare` | Hospitals and health services |
   | `education` | Schools and universities |
   | `private_sector` | Non-government private organizations |
   | `tld_registrants` | Domain name registrants under the national TLD |

6. **Validate your file:**

   ```bash
   pip install pyyaml jsonschema
   python scripts/validate_data.py
   ```

7. **Open a Pull Request** using the PR template.

---

## Updating Existing Data

- Only update `last_reviewed` when you have *actually re-verified* the data against official sources.
- If a requirement has been removed, changed, or the policy has lapsed, update the `status` field and explain the change in `notes`.
- Add the new source to `references` — do not remove old references (they provide historical context).

---

## Data Quality Standards

### Sources must be official

Every `mandatory` or `recommended` entry **must** have at least one URL in `references` pointing to an official document from:

- A government ministry or department
- A national cybersecurity agency (CISA, NCSC, BSI, ANSSI, ACSC, CCCS, NCSA, etc.)
- A formal standards body (Forum Standaardisatie, etc.)
- A legally binding directive or regulation (EU directive, binding operational directive, etc.)

**Not acceptable as sole sources:**

- News articles or blog posts (can be cited as supplementary context in `notes`)
- Wikipedia
- Vendor white papers or marketing materials
- Social media posts

### Unknown is valuable data

If you have researched a country and found **no** official email security guidance, create the file with `status: unknown` for all standards and document what you searched in the `notes` field. This is genuinely useful information.

### Dates

- All dates must be in `YYYY-MM-DD` (ISO 8601) format.
- `last_reviewed` should be the date you last checked the source documents, not the policy's publication date.

---

## Running Validation Locally

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Validate all country files
python scripts/validate_data.py

# Regenerate the map and README table (optional — CI does this automatically)
python scripts/fetch_basemap.py   # Only needed once
python scripts/generate_map.py
python scripts/generate_readme_table.py
python scripts/generate_webversion.py
```

Validation will:
- Check all YAML files against the JSON schema
- Verify `country_code` matches the filename
- Warn if `last_reviewed` is more than 12 months ago
- Warn if `mandatory`/`recommended` entries lack references

---

## Pull Request Checklist

When opening a PR, confirm:

- [ ] Country file is at `data/countries/XX.yaml` with the correct ISO code
- [ ] `last_reviewed` is set to today's date
- [ ] All `mandatory` and `recommended` entries have at least one source URL in `references`
- [ ] Sources are official government/agency documents
- [ ] `python scripts/validate_data.py` passes (or CI passes)
- [ ] You have **not** modified generated files directly (`docs/map.svg`, `docs/index.html`, `webversion/`, or the matrix section of `README.md`)

---

## What Counts as a Valid Source?

Here are examples of acceptable official sources by country:

| Country | Acceptable Source Types |
|---|---|
| Netherlands | Forum Standaardisatie, NCSC/NCSA, BIO documentation, Digitale Overheid |
| United States | CISA (cyber.dhs.gov), NIST, OMB M-Memoranda |
| United Kingdom | NCSC (ncsc.gov.uk), Cabinet Office, GDS |
| Germany | BSI (bsi.bund.de) |
| France | ANSSI (ssi.gouv.fr) |
| Australia | ASD/ACSC (cyber.gov.au), PSPF |
| Canada | CCCS (cyber.gc.ca), Treasury Board directives |
| EU | EUR-Lex (eur-lex.europa.eu), ENISA |

---

## Frequently Asked Questions

**Q: My country has a recommendation but it's buried in a long framework document. Should I still add it?**

Yes — cite the specific document and page/section if you can. Add the direct quote or a summary in `notes`.

**Q: The official guidance uses different terminology. What status should I choose?**

Use your judgment based on the practical effect:
- If non-compliance can result in an audit finding, penalty, or loss of certification → `mandatory`
- If the document says "should", "recommended", "best practice" with no consequence → `recommended`
- If it's just mentioned or listed as one option → `informational`

**Q: Should I add an entry for standards the country has no guidance on at all?**

You can omit them (they'll show as ❓ Unknown in the table), or you can include them with `status: unknown` and a note explaining you searched but found nothing. The latter is more informative.

**Q: The policy only applies to `.gov` domains, not all government agencies. How do I express that?**

Use `applies_to: [government_agencies]` and add a note like `"Applies to .gov.uk domains only"` in the `notes` field.

**Q: I found a source in a language other than English. Is that OK?**

Absolutely — email security is global and most source documents are in local languages. Add the original-language URL in `references` and write a brief English summary in `notes`.
