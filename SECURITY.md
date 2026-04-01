# Security Policy

## Supported Versions

I am committed to keeping your local Roomba connection secure. I prioritize security updates for the latest stable releases.

| Version | Supported          |
| ------- | ------------------ |
| v2.2.x  | :white_check_mark: |
| v2.1.x  | :white_check_mark: |
| < v2.1  | :x:                |

---

## Security Principles

This project is built with a **Security-First** mindset for local IoT environments:
* **Local-Only**: All communication stays within your private network. No data is sent to external clouds or third-party servers by this suite.
* **Credential Masking**: The architecture is designed to pull sensitive data from `.env` files, which are strictly excluded from version control via the included `.gitignore`.
* **Legacy SSL**: While I enable `SECLEVEL=1` to support older Roomba hardware, I restrict these settings to the specific local connection to minimize network exposure.

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a potential security risk in the **Roomba-900-Local-Connect** suite, please follow these steps to help me improve the project:

1.  **Private Report**: Send a detailed description of the vulnerability directly to **Michael Landbo (L4DK)** via a GitHub Private Security Advisory or through the contact methods listed on my [L4DK GitHub Profile](https://github.com/L4DK).
2.  **Response Time**: You can expect an acknowledgment of your report from me within **48–72 hours**.
3.  **Resolution**: I will provide a timeline for a fix. Once the fix is verified and released, I will offer credit to the reporter (if desired) in the project changelog.

### What to include in your report:
* A clear description of the vulnerability.
* A proof-of-concept (PoC) or clear steps to reproduce the issue.
* The potential impact (e.g., credential theft, unauthorized command execution).

---

## Safe Handling of `.env`

> [!WARNING]
> Your `.env` file contains your **ROOMBA_PASSWORD**, which is a plain-text key for your vacuum.

* **Never** share your `.env` file with anyone.
* **Never** take screenshots of your terminal if the credentials have just been extracted.
* **Always** verify that your `.gitignore` is active before pushing your code to a public fork.
