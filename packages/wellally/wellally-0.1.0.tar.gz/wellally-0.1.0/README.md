# WellAlly Python SDK

Python data models for the WellAlly health data platform.

**Website:** https://www.wellally.tech/

## Installation

```bash
pip install wellally
```

## Features

- 🏥 **Lab Reports**: Structured laboratory test results with LOINC codes
- 🔬 **Imaging Reports**: Diagnostic imaging reports with DICOM support
- 💊 **Medications**: Medication records with RxNorm codes
- 👤 **Personal Health**: Individual health records following FHIR standards
- 👨‍👩‍👧‍👦 **Family Health**: Family health trees for genetic tracking

## Usage

### Lab Report Example

```python
from wellally import LabReport, LabResult, CodeableConcept, Coding, Quantity
from datetime import datetime

# Create a lab result
result = LabResult(
    code=CodeableConcept(
        coding=[Coding(
            system="http://loinc.org",
            code="2339-0",
            display="Glucose"
        )]
    ),
    value=Quantity(value=95.0, unit="mg/dL"),
    interpretation="N"
)

# Create a lab report
report = LabReport(
    id="lab-001",
    patientId="patient-123",
    issuedAt=datetime.now(),
    results=[result]
)
```

### Personal Health Record Example

```python
from wellally import Person, HumanName
from datetime import date

person = Person(
    id="patient-123",
    name=[HumanName(
        family="Zhang",
        given=["San"]
    )],
    birthDate=date(1990, 1, 1),
    gender="male"
)
```

## Data Models

### Common Types
- `Coding`: Coded value from a terminology system
- `CodeableConcept`: Concept with multiple codes
- `Quantity`: Measured value with UCUM unit
- `HumanName`: Structured person name
- `ContactPoint`: Contact information
- `Address`: Postal address

### Domain Models
- `LabReport`: Laboratory test report
- `ImagingReport`: Diagnostic imaging report
- `MedicationRecord`: Medication administration record
- `Person`: Personal health record
- `FamilyHealthTree`: Family health tree

## Standards Compliance

This package implements data models based on:
- HL7 FHIR (Fast Healthcare Interoperability Resources)
- LOINC (Logical Observation Identifiers Names and Codes)
- SNOMED CT (Systematized Nomenclature of Medicine)
- RxNorm (medication naming)
- UCUM (Unified Code for Units of Measure)
- DICOM (Digital Imaging and Communications in Medicine)

## License

MIT License - see LICENSE file for details

## Support

- Documentation: https://www.wellally.tech/docs
- Issues: https://github.com/huifer/wellally-schemas/issues
- Email: huifer97@163.com
