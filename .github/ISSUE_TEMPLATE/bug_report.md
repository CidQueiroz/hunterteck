name: Bug Report
description: Report a bug or issue
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report!
  
  - type: input
    id: title
    attributes:
      label: Bug Title
      description: Brief description of the bug
    validations:
      required: true
  
  - type: textarea
    id: description
    attributes:
      label: Description
      description: Detailed description of the bug
    validations:
      required: true
  
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: |
        Steps to reproduce the behavior:
        1. 
        2. 
        3.
    validations:
      required: true
  
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What you expected to happen
    validations:
      required: true
  
  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happened
    validations:
      required: true
  
  - type: input
    id: version
    attributes:
      label: Version
      description: HunterTeck version
      placeholder: "1.0.0"
    validations:
      required: true
  
  - type: textarea
    id: logs
    attributes:
      label: Logs
      description: Relevant log output
      render: bash
