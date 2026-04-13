# DKIM — DomainKeys Identified Mail

## Purpose

DKIM adds a cryptographic digital signature to outgoing email messages. The signature is attached as an email header and can be verified by any receiving server using the public key published in the sender's DNS. This proves two things: the message was sent from a server authorized by the domain owner, and the message content (specified headers + body) has not been altered since it was signed.

Unlike SPF, DKIM survives email forwarding, because the signature travels with the message regardless of which server relays it. This makes DKIM a more robust authentication mechanism and an essential complement to SPF for DMARC alignment.

## How It Works

1. The sending mail server computes a hash of selected headers and the message body.
2. The hash is signed with the domain's private key.
3. The signature is added to the email as a `DKIM-Signature:` header.
4. The public key is published as a DNS TXT record at `selector._domainkey.your-domain.com`.
5. The receiving server retrieves the public key from DNS and verifies the signature.
6. A successful verification confirms the message originated from an authorized server and was not tampered with.

## RFCs and Specifications

| Document | Description |
|---|---|
| [RFC 6376](https://datatracker.ietf.org/doc/html/rfc6376) | DKIM Signatures (2011) — current standard |
| [RFC 8301](https://datatracker.ietf.org/doc/html/rfc8301) | Cryptographic algorithm updates |
| [RFC 8463](https://datatracker.ietf.org/doc/html/rfc8463) | Ed25519 algorithm for DKIM |
| [RFC 5585](https://datatracker.ietf.org/doc/html/rfc5585) | DKIM service overview |

## DNS Record Format

The public key is published at: `selector._domainkey.your-domain.com`

```dns
mail._domainkey.your-domain.com.  IN TXT  "v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQ..."
```

For Ed25519 (recommended for new deployments):

```dns
ed25519._domainkey.your-domain.com.  IN TXT  "v=DKIM1; k=ed25519; p=11qYAYKxCrfVS/7TyWQHOg7hcvPapiMlrwIaaPcHURo="
```

## Email Header Example

```
DKIM-Signature: v=1; a=rsa-sha256; c=relaxed/relaxed; d=example.com;
    s=mail; h=from:to:subject:date:message-id;
    bh=base64hash=; b=base64signature=
```

## Key Recommendations

- Use 2048-bit RSA or Ed25519 keys (1024-bit RSA is no longer acceptable)
- Rotate keys at least annually
- Use a dedicated selector per mail system (e.g., `google`, `sendgrid`, `ses`)
- Sign the `From:`, `Subject:`, `Date:`, `To:`, `Message-ID` headers at minimum
- Use `c=relaxed/relaxed` canonicalization for compatibility

## Testing Tools

| Tool | URL | Notes |
|---|---|---|
| internet.nl | https://internet.nl | Full suite test |
| MXToolbox DKIM Lookup | https://mxtoolbox.com/dkim.aspx | DNS key lookup |
| dmarcian DKIM Inspector | https://dmarcian.com/dkim-inspector/ | Detailed inspection |
| Mailcheck | https://passwordscon.org/mailcheck/ | Combined tester |

## Implementation Guides

- [Google Workspace: Set up DKIM](https://support.google.com/a/answer/180504)
- [Microsoft 365: Set up DKIM](https://learn.microsoft.com/en-us/microsoft-365/security/office-365-security/email-authentication-dkim-configure)
- [NCSC UK: Anti-spoofing using DKIM](https://www.ncsc.gov.uk/collection/email-security-and-anti-spoofing/anti-spoofing-using-dkim)

## Countries with DKIM Requirements

| Country | Status | Applies To | Authority |
|---|---|---|---|
| Netherlands | **Mandatory** | Government agencies | Forum Standaardisatie / BIO |
| United Kingdom | **Mandatory** | Government agencies | NCSC |
| United States | Recommended | Federal agencies | CISA BOD 18-01 |
| Germany | Recommended | Gov / Critical infra | BSI TR-03108 |
| Australia | Recommended | Government agencies | ASD / ACSC ISM |
| France | Recommended | Gov / Critical infra | ANSSI |
| Canada | Recommended | Government agencies | CCCS |
