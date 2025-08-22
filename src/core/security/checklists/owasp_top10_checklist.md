# OWASP Top 10 2023 Security Checklist
*Comprehensive security validation checklist for Claude Code v3.6.9*

## A01:2021 – Broken Access Control

### Access Control Implementation
- [ ] **Deny by Default**: Access is denied by default except for public resources
- [ ] **Centralized Access Control**: Access control mechanisms are implemented once and reused throughout the application
- [ ] **Ownership Model**: Access controls enforce record ownership rather than accepting that the user can create, read, update, or delete any record
- [ ] **Domain Model**: Unique application business limit requirements are enforced by domain models
- [ ] **Directory Listing Disabled**: Web server directory listing is disabled and ensures file metadata and backup files are not present within web roots
- [ ] **Log Access Control Failures**: Access control failures are logged and administrators are alerted when appropriate
- [ ] **Rate Limiting**: API and controller access is rate limited to minimize harm from automated attack tooling
- [ ] **Session Invalidation**: JWT tokens are invalidated on the server after logout

### Testing Checklist
- [ ] Verify access controls work on server-side
- [ ] Test for privilege escalation
- [ ] Verify access to admin functions requires admin authorization
- [ ] Test for forced browsing to unauthorized functionality
- [ ] Verify that users cannot access other users' data

### Code Review Items
- [ ] Review authorization checks in all endpoints
- [ ] Verify consistent access control implementation
- [ ] Check for hardcoded authorization decisions
- [ ] Validate role-based access control implementation
- [ ] Review session management and JWT handling

---

## A02:2021 – Cryptographic Failures

### Data Classification
- [ ] **Data Inventory**: Classify data processed, stored, or transmitted by the application
- [ ] **Privacy Laws**: Identify which data falls under privacy laws, regulatory requirements, or business needs
- [ ] **Data Retention**: Don't store sensitive data unnecessarily; discard it as soon as possible
- [ ] **PCI DSS Compliance**: Ensure all credit card data storage complies with PCI DSS requirements

### Encryption Implementation
- [ ] **At Rest Encryption**: All sensitive data is encrypted at rest
- [ ] **In Transit Encryption**: All sensitive data is encrypted in transit with secure protocols such as TLS with forward secrecy (FS) ciphers
- [ ] **Certificate Management**: Encryption keys are properly generated and managed
- [ ] **Strong Algorithms**: Ensure up-to-date and strong standard algorithms, protocols, and keys are in place
- [ ] **Key Management**: Use proper key management practices

### Testing Checklist
- [ ] Verify sensitive data is encrypted in storage
- [ ] Test TLS implementation and certificate validity
- [ ] Verify strong encryption algorithms are used
- [ ] Test key management procedures
- [ ] Verify passwords are hashed with appropriate salt

### Code Review Items
- [ ] Review cryptographic implementations
- [ ] Check for hardcoded encryption keys
- [ ] Verify use of secure random number generation
- [ ] Review password hashing mechanisms
- [ ] Validate certificate and key management

---

## A03:2021 – Injection

### Input Validation
- [ ] **Safe APIs**: Use safe APIs that avoid interpreters entirely, provide a parameterized interface, or migrate to Object Relational Mapping Tools (ORMs)
- [ ] **Positive Validation**: Use positive server-side input validation with an appropriate canonical representation
- [ ] **Special Characters**: Escape special characters using the specific escape syntax for the target interpreter
- [ ] **SQL Controls**: Use LIMIT and other SQL controls within queries to prevent mass disclosure of records in case of SQL injection

### Parameterized Queries
- [ ] **Prepared Statements**: Use parameterized queries, stored procedures, or prepared statements
- [ ] **Dynamic Queries**: Avoid dynamic query construction where possible
- [ ] **ORM Usage**: Use ORM frameworks that provide built-in protection
- [ ] **Input Sanitization**: Sanitize all user inputs before processing

### Testing Checklist
- [ ] Test all input fields for SQL injection
- [ ] Test for NoSQL injection vulnerabilities
- [ ] Verify command injection protection
- [ ] Test LDAP injection prevention
- [ ] Check for XPath injection vulnerabilities

### Code Review Items
- [ ] Review all database interaction code
- [ ] Check for dynamic SQL construction
- [ ] Verify parameterized query usage
- [ ] Review input validation implementations
- [ ] Check for proper output encoding

---

## A04:2021 – Insecure Design

### Secure Development Lifecycle
- [ ] **SDLC Integration**: Establish and use a secure development lifecycle with AppSec professionals
- [ ] **Design Patterns**: Establish and use a library of secure design patterns or paved road ready to use components
- [ ] **Threat Modeling**: Use threat modeling for critical authentication, access control, business logic, and key flows
- [ ] **User Stories**: Integrate security language and controls into user stories
- [ ] **Plausibility Checks**: Plausibility checks at each tier of your application

### Security Architecture
- [ ] **Layered Security**: Implement defense in depth approach
- [ ] **Segregation**: Write unit and integration tests to validate that all critical flows are resistant to the threat model
- [ ] **Resource Limits**: Segregate tier layers on the system and network layers depending on the exposure and protection needs
- [ ] **Security Controls**: Implement comprehensive security controls for each layer

### Testing Checklist
- [ ] Review security architecture design
- [ ] Validate threat model implementation
- [ ] Test business logic security
- [ ] Verify secure design patterns usage
- [ ] Test for insecure design patterns

---

## A05:2021 – Security Misconfiguration

### Secure Configuration
- [ ] **Hardening Process**: A repeatable hardening process makes it fast and easy to deploy another environment that is appropriately secured
- [ ] **Minimal Platform**: A minimal platform without any unnecessary features, components, documentation, and samples
- [ ] **Configuration Review**: A task to review and update the configurations appropriate to all security notes, updates, and patches
- [ [ **Segmented Architecture**: A segmented application architecture provides effective separation between components or tenants
- [ ] **Security Headers**: Sending security directives to clients, e.g., Security Headers
- [ ] **Automated Verification**: An automated process to verify the effectiveness of the configurations and settings in all environments

### Environment Security
- [ ] **Development Environment**: Ensure development environments are secured similarly to production
- [ ] **Default Credentials**: Change all default passwords and credentials
- [ ] **Error Handling**: Implement proper error handling that doesn't reveal system information
- [ ] **Debug Mode**: Disable debug mode in production environments
- [ ] **Directory Listing**: Disable directory listing and file browsing

### Testing Checklist
- [ ] Test for default credentials
- [ ] Verify security headers implementation
- [ ] Check for information disclosure in error messages
- [ ] Test configuration security
- [ ] Verify unnecessary services are disabled

---

## A06:2021 – Vulnerable and Outdated Components

### Component Management
- [ ] **Inventory**: Remove unused dependencies, unnecessary features, components, files, and documentation
- [ ] **Version Tracking**: Continuously inventory the versions of both client-side and server-side components and their dependencies
- [ ] **Vulnerability Monitoring**: Only obtain components from official sources over secure links. Prefer signed packages
- [ ] **Maintenance Status**: Monitor for libraries and components that are unmaintained or do not create security patches for older versions
- [ ] **Update Process**: Have a patch management process in place for when new vulnerabilities are discovered

### Dependency Security
- [ ] **Source Validation**: Only obtain components from official sources over secure links
- [ ] **Signature Verification**: Prefer signed packages to reduce the chance of including a malicious component
- [ ] **Vulnerability Scanning**: Monitor for components with known vulnerabilities
- [ ] **Impact Assessment**: Have a plan for updating or removing vulnerable components

### Testing Checklist
- [ ] Scan all dependencies for known vulnerabilities
- [ ] Verify component authenticity and integrity
- [ ] Test for outdated components
- [ ] Review third-party component security
- [ ] Test dependency update procedures

---

## A07:2021 – Identification and Authentication Failures

### Authentication Security
- [ ] **Multi-Factor Authentication**: Implement multi-factor authentication to prevent automated credential stuffing, brute force, and stolen credential reuse attacks
- [ ] **Default Credentials**: Do not ship or deploy with any default credentials, particularly for admin users
- [ ] **Weak Password Checks**: Implement weak password checks, such as testing new or changed passwords against the top 10,000 worst passwords list
- [ ] **Password Policy**: Align password length, complexity, and rotation policies with NIST 800-63b's guidelines in section 5.1.1 for Memorized Secrets
- [ ] **Secure Registration**: Ensure registration, credential recovery, and API pathways are hardened against account enumeration attacks

### Session Management
- [ ] **Session Security**: Use a server-side, secure, built-in session manager that generates a new random session ID with high entropy after login
- [ ] **Session Invalidation**: Session identifier should not be in the URL, be securely stored, and invalidated after logout, idle, and absolute timeouts
- [ ] **Session Protection**: Protect against session fixation attacks
- [ ] **Session Monitoring**: Monitor and alert on suspicious authentication activities

### Testing Checklist
- [ ] Test authentication bypass attempts
- [ ] Verify multi-factor authentication implementation
- [ ] Test password policy enforcement
- [ ] Verify session management security
- [ ] Test for authentication timing attacks

---

## A08:2021 – Software and Data Integrity Failures

### Software Integrity
- [ ] **Digital Signatures**: Use digital signatures or similar mechanisms to verify the software or data is from the expected source and has not been altered
- [ ] **Trusted Repositories**: Ensure libraries and dependencies are consuming trusted repositories
- [ ] **Supply Chain Security**: Use a software supply chain security tool, such as OWASP Dependency Check or OWASP CycloneDX
- [ ] **CI/CD Security**: Ensure that your CI/CD pipeline has proper segregation, configuration, and access control to ensure the integrity of the code flowing through the build and deploy processes
- [ ] **Serialization Security**: Ensure that unsigned or unencrypted serialized data is not sent to untrusted clients without some form of integrity check or digital signature to detect tampering or replay

### Data Integrity
- [ ] **Data Validation**: Implement comprehensive data validation
- [ ] **Checksum Verification**: Use checksums or digital signatures to verify data integrity
- [ ] **Backup Integrity**: Ensure backup data integrity and restoration procedures
- [ ] **Audit Trails**: Maintain comprehensive audit trails for all data modifications

### Testing Checklist
- [ ] Test software signature verification
- [ ] Verify data integrity controls
- [ ] Test CI/CD pipeline security
- [ ] Verify serialization security
- [ ] Test backup and recovery integrity

---

## A09:2021 – Security Logging and Monitoring Failures

### Logging Implementation
- [ ] **Comprehensive Logging**: Ensure all login, access control, and server-side input validation failures can be logged with sufficient user context to identify suspicious or malicious accounts
- [ ] **Log Format**: Ensure that logs are generated in a format that log management solutions can easily consume
- [ ] **Log Encoding**: Ensure log data is encoded correctly to prevent injections or attacks on the logging or monitoring systems
- [ ] **Audit Trails**: Ensure high-value transactions have an audit trail with integrity controls to prevent tampering or deletion
- [ ] **Effective Monitoring**: Establish or adopt effective monitoring and alerting such that suspicious activities are detected and responded to quickly

### Monitoring and Alerting
- [ ] **Real-time Monitoring**: Implement real-time monitoring for security events
- [ ] **Alerting System**: Configure appropriate alerting for security incidents
- [ ] **Log Retention**: Establish appropriate log retention policies
- [ ] **Log Analysis**: Implement log analysis and correlation capabilities
- [ ] **Incident Response**: Establish clear incident response procedures

### Testing Checklist
- [ ] Verify comprehensive security logging
- [ ] Test log integrity and protection
- [ ] Verify monitoring and alerting functionality
- [ ] Test incident response procedures
- [ ] Verify log retention and analysis capabilities

---

## A10:2021 – Server-Side Request Forgery (SSRF)

### Input Validation
- [ ] **Sanitization**: Sanitize and validate all client-supplied input data
- [ ] **Positive Allow Lists**: Enforce the URL schema, port, and destination with a positive allow list
- [ ] **Response Handling**: Do not send raw responses to clients
- [ ] **HTTP Redirections**: Disable HTTP redirections
- [ ] **URL Consistency**: Be aware of the URL consistency to avoid attacks such as DNS rebinding and "time of check, time of use" (TOCTOU) race conditions

### Network Security
- [ ] **Network Segmentation**: Segment remote resource access functionality in separate networks to reduce the impact of SSRF
- [ ] **Firewall Rules**: Enforce "deny by default" firewall policies or network access control rules to block all but essential intranet traffic
- [ ] **Request Monitoring**: Monitor all network requests from the application
- [ ] **Response Validation**: Validate and sanitize all responses from remote resources

### Testing Checklist
- [ ] Test for SSRF vulnerabilities in all URL inputs
- [ ] Verify network access controls
- [ ] Test URL validation and sanitization
- [ ] Verify response handling security
- [ ] Test for DNS rebinding attacks

---

## Implementation Checklist

### Code Review Process
- [ ] Conduct regular security-focused code reviews
- [ ] Use automated security scanning tools
- [ ] Implement peer review for all security-critical code
- [ ] Maintain security coding standards
- [ ] Document security review findings and remediation

### Security Testing
- [ ] Implement automated security testing in CI/CD
- [ ] Conduct regular penetration testing
- [ ] Perform security regression testing
- [ ] Test security controls effectiveness
- [ ] Validate security configuration changes

### Monitoring and Incident Response
- [ ] Implement comprehensive security monitoring
- [ ] Establish incident response procedures
- [ ] Conduct regular security training
- [ ] Maintain security metrics and reporting
- [ ] Perform regular security assessments

### Documentation and Training
- [ ] Maintain up-to-date security documentation
- [ ] Provide regular security training for developers
- [ ] Document security procedures and policies
- [ ] Maintain security architecture documentation
- [ ] Keep security assessment reports current

---

## Compliance Validation

### Automated Checks
- [ ] All automated security tests are passing
- [ ] Dependency vulnerability scans show no critical issues
- [ ] Static code analysis shows acceptable risk levels
- [ ] Configuration security scans are clean
- [ ] Security unit tests are comprehensive and passing

### Manual Reviews
- [ ] Security architecture has been reviewed and approved
- [ ] Business logic security has been validated
- [ ] Access control implementation has been tested
- [ ] Cryptographic implementations have been reviewed
- [ ] Security documentation is complete and current

### Sign-off Requirements
- [ ] Security architect approval
- [ ] Lead developer sign-off on security implementations
- [ ] Compliance officer validation (if applicable)
- [ ] Security testing completion certification
- [ ] Risk assessment and acceptance documentation

---

*This checklist should be completed for each release and maintained as a living document. Regular updates should reflect changes in the OWASP Top 10 and emerging security threats.*