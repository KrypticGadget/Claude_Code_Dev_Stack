# FinTech Application Prompts

Use these prompts for financial technology projects with the Claude Code Agent System.

## Payment Processing Platform

```
> Use the master-orchestrator agent to begin new project: "Payment processing platform supporting credit cards, ACH, wire transfers, and digital wallets with PCI DSS compliance, fraud detection, multi-currency support, and merchant dashboard. Processing target of [VOLUME] transactions daily."
```

## Digital Banking Application

```
> Use the master-orchestrator agent to begin new project: "Digital banking application with account management, transfers, bill pay, mobile deposit, and budgeting tools. Must meet [REGULATORY] compliance with biometric authentication and real-time fraud monitoring."
```

## Trading Platform

```
> Use the master-orchestrator agent to begin new project: "Trading platform for [ASSET TYPES] with real-time quotes, order execution, portfolio management, and technical analysis tools. Supporting [USER COUNT] concurrent traders with sub-second latency."
```

## Lending Platform

```
> Use the master-orchestrator agent to begin new project: "Lending platform with loan origination, underwriting automation, credit decisioning, and servicing. Supporting [LOAN TYPES] with [COMPLIANCE REQUIREMENTS] and integration with [CREDIT BUREAUS]."
```

## Cryptocurrency Exchange

```
> Use the master-orchestrator agent to begin new project: "Cryptocurrency exchange supporting [CRYPTO PAIRS] with spot trading, wallet management, KYC/AML compliance, and cold storage security. Handling [TPS] transactions per second."
```

## Personal Finance Manager

```
> Use the master-orchestrator agent to begin new project: "Personal finance management app with account aggregation, expense tracking, budgeting, investment tracking, and financial insights. Integrating with [BANK COUNT] financial institutions via [AGGREGATOR]."
```

## Insurance Platform

```
> Use the master-orchestrator agent to begin new project: "Insurance platform for [INSURANCE TYPES] with quote generation, policy management, claims processing, and agent portal. Meeting [STATE/COUNTRY] regulatory requirements."
```

## Crowdfunding Platform

```
> Use the master-orchestrator agent to begin new project: "Crowdfunding platform for [PROJECT TYPES] with campaign creation, payment processing, investor verification, and regulatory compliance for [JURISDICTION]."
```

## Expense Management System

```
> Use the master-orchestrator agent to begin new project: "Corporate expense management with receipt scanning, approval workflows, credit card integration, and accounting software sync. Supporting [EMPLOYEE COUNT] users across [COUNTRIES]."
```

## Wealth Management Platform

```
> Use the master-orchestrator agent to begin new project: "Wealth management platform with portfolio management, robo-advisory, performance reporting, and client portal. Managing [AUM] in assets with [COMPLIANCE] requirements."
```

## FinTech-Specific Features

### Compliance & Security
```
"...with SOC2 Type II compliance, PCI DSS Level 1, end-to-end encryption, and comprehensive audit logging"
```

### Fraud Detection
```
"...including ML-based fraud detection, transaction monitoring, velocity checks, and device fingerprinting"
```

### Regulatory Reporting
```
"...with automated regulatory reporting for [REGULATIONS], suspicious activity monitoring, and KYC/AML workflows"
```

### Integration Requirements
```
"...integrated with [Plaid/Yodlee] for account aggregation, [Stripe/Adyen] for payments, and [CORE BANKING] system"
```

## Common FinTech Patterns

### Multi-Currency Support
```
> Use the financial-analyst agent to implement multi-currency support with real-time exchange rates, conversion fees, and settlement reconciliation
```

### Reconciliation Engine
```
> Use the backend-services agent to build reconciliation engine matching transactions across [SYSTEMS] with exception handling
```

### Risk Scoring
```
> Use the backend-services agent to implement risk scoring system for [USE CASE] using [DATA POINTS] with ML models
```

### Audit Trail
```
> Use the security-architecture agent to implement immutable audit trail for all financial transactions with tamper detection
```

## Variables to Replace:
- `[VOLUME]` - 100K, 1M, 10M transactions
- `[REGULATORY]` - FDIC, FCA, GDPR
- `[ASSET TYPES]` - Stocks, forex, crypto
- `[LOAN TYPES]` - Personal, mortgage, business
- `[COMPLIANCE REQUIREMENTS]` - TILA, FCRA, ECOA
- `[CRYPTO PAIRS]` - BTC/USD, ETH/USD, etc.
- `[TPS]` - Transactions per second
- `[INSURANCE TYPES]` - Auto, home, life
- `[AUM]` - Assets under management amount