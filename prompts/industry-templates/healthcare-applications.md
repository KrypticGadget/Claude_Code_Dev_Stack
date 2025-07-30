# Healthcare Application Prompts

Use these prompts for healthcare and medical technology projects with the Claude Code Agent System.

## Electronic Health Records (EHR)

```
> Use the master-orchestrator agent to begin new project: "Electronic Health Records system for [FACILITY TYPE] with patient management, clinical documentation, e-prescribing, lab integration, and billing. HIPAA compliant with support for [PROVIDER COUNT] providers."
```

## Telemedicine Platform

```
> Use the master-orchestrator agent to begin new project: "Telemedicine platform with video consultations, appointment scheduling, patient portal, prescription management, and payment processing. Supporting [CONCURRENT SESSIONS] simultaneous consultations with HIPAA compliance."
```

## Medical Practice Management

```
> Use the master-orchestrator agent to begin new project: "Practice management system for [SPECIALTY] with appointment scheduling, patient registration, billing, insurance claims, and reporting. Integrating with [EHR SYSTEM] and supporting [LOCATION COUNT] locations."
```

## Patient Portal

```
> Use the master-orchestrator agent to begin new project: "Patient portal with health records access, appointment booking, medication refills, secure messaging, and bill payment. Supporting [PATIENT COUNT] patients with mobile apps and accessibility compliance."
```

## Clinical Trial Management

```
> Use the master-orchestrator agent to begin new project: "Clinical trial management system for [TRIAL PHASES] with participant recruitment, protocol management, data collection, adverse event tracking, and regulatory reporting for [REGULATORY BODY]."
```

## Healthcare Analytics Platform

```
> Use the master-orchestrator agent to begin new project: "Healthcare analytics platform processing [DATA TYPES] for population health, clinical outcomes, operational efficiency, and predictive modeling. HIPAA compliant with real-time dashboards."
```

## Medical Device Integration

```
> Use the master-orchestrator agent to begin new project: "Medical device integration platform connecting [DEVICE TYPES] with EHR systems, real-time monitoring, alert management, and data analytics. Supporting [PROTOCOL STANDARDS] protocols."
```

## Pharmacy Management System

```
> Use the master-orchestrator agent to begin new project: "Pharmacy management system with prescription processing, inventory management, drug interaction checking, insurance adjudication, and patient counseling records. Integrating with [PBM SYSTEMS]."
```

## Mental Health Platform

```
> Use the master-orchestrator agent to begin new project: "Mental health platform with therapist matching, session scheduling, progress tracking, treatment plans, and outcome measurements. Supporting [SESSION TYPES] with crisis intervention features."
```

## Medical Imaging System

```
> Use the master-orchestrator agent to begin new project: "Medical imaging system for [MODALITIES] with DICOM storage, viewer, reporting tools, and AI-assisted diagnosis. Supporting [STUDY VOLUME] studies per day with cloud archival."
```

## Healthcare-Specific Features

### HIPAA Compliance
```
"...with HIPAA compliance including encryption at rest and in transit, access controls, audit logging, and BAA support"
```

### HL7 Integration
```
"...supporting HL7 v2.x and FHIR standards for interoperability with [SYSTEM TYPES] and automated data mapping"
```

### Clinical Decision Support
```
"...including clinical decision support with drug interactions, allergy checking, and evidence-based recommendations"
```

### Patient Privacy
```
"...implementing patient consent management, data minimization, and granular access controls for PHI"
```

## Common Healthcare Patterns

### Patient Matching
```
> Use the backend-services agent to implement patient matching algorithm using [MATCHING CRITERIA] with duplicate detection
```

### Appointment Scheduling
```
> Use the backend-services agent to create intelligent scheduling system considering provider availability, room resources, and appointment types
```

### Insurance Verification
```
> Use the api-integration-specialist agent to integrate insurance eligibility verification with [CLEARINGHOUSE] for real-time checks
```

### Clinical Workflows
```
> Use the frontend-architecture agent to design clinical workflow for [WORKFLOW TYPE] with role-based forms and decision trees
```

## Regulatory Considerations

### FDA Compliance
```
"...meeting FDA [CLASS] medical device software requirements with design controls and validation documentation"
```

### International Standards
```
"...compliant with [ISO 13485/IEC 62304] standards for medical device software development"
```

### State Regulations
```
"...adhering to [STATE] telemedicine regulations including licensure, prescribing, and record retention"
```

## Variables to Replace:
- `[FACILITY TYPE]` - Hospital, clinic, practice
- `[PROVIDER COUNT]` - Number of healthcare providers
- `[SPECIALTY]` - Cardiology, pediatrics, etc.
- `[EHR SYSTEM]` - Epic, Cerner, Allscripts
- `[PATIENT COUNT]` - Expected patient volume
- `[TRIAL PHASES]` - Phase I-IV
- `[REGULATORY BODY]` - FDA, EMA, etc.
- `[DEVICE TYPES]` - Monitors, pumps, etc.
- `[MODALITIES]` - X-ray, MRI, CT, etc.
- `[CLEARINGHOUSE]` - Availity, Change Healthcare