# Security Policy

## Supported Versions
We actively patch security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability
The SEAR team takes security seriously. If you discover a security vulnerability within this project, please send an email to [Your Email] or use the GitHub Security Advisories feature. 

**Please do not report security vulnerabilities through public GitHub issues.**

You will receive a response from us within 48 hours. If the issue is confirmed, we will release a patch as soon as possible, depending on the complexity of the issue.

## Best Practices for Users
- Never commit your `.env` file containing API keys to a public repository.
- Keep your Python dependencies updated (`pip install --upgrade -r requirements.txt`).
- Run SEAR on trusted networks when crawling internal or staging environments.
