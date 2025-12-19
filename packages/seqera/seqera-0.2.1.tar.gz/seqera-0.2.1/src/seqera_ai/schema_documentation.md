# Nextflow Schema Documentation

## Overview

The `nextflow_schema.json` file provides comprehensive parameter validation and documentation for Nextflow pipelines. This schema follows the nf-core standards and JSON Schema Draft 7 specification.

## Key Components

### 1. Schema Metadata

- **$schema**: References JSON Schema Draft 7 specification
- **$id**: Unique identifier/URL for the schema
- **title**: Human-readable title for the pipeline
- **description**: Brief description of the pipeline's purpose

### 2. Parameter Groups (Definitions)

The schema organizes parameters into logical groups for better organization and documentation:

#### Input/Output Options

- **Purpose**: Define where the pipeline finds input data and saves output
- **Required Parameters**: `input`, `outdir`
- **Key Features**:
  - File path validation with `format: "file-path"`
  - File existence checking with `exists: true`
  - MIME type validation
  - Pattern matching for file extensions
  - Email validation using regex patterns

#### Reference Genome Options

- **Purpose**: Manage reference genome files and iGenomes configuration
- **Key Parameters**:
  - `genome`: iGenomes reference ID
  - `fasta`: FASTA genome file path
  - `gtf`/`gff`: Annotation files
  - `save_reference`: Boolean to save generated indices
- **Features**:
  - Multiple file format support (.fa, .fasta, .gz)
  - Pattern validation for bioinformatics file formats
  - Hidden parameters for advanced configuration

#### Alignment Options

- **Purpose**: Configure alignment algorithms and parameters
- **Key Features**:
  - Enum values for aligner selection (`star`, `star_salmon`, `hisat2`, `salmon`)
  - Boolean flags for saving intermediate files
  - Sequencing center metadata

#### Read Trimming Options

- **Purpose**: Control adapter trimming and quality filtering
- **Features**:
  - Tool selection via enum (`trimgalore`, `fastp`)
  - Integer constraints for minimum reads
  - Extra arguments passing for tool customization
  - Skip flags for workflow control

#### Quality Control Options

- **Purpose**: Enable/disable QC steps
- **Features**:
  - Multiple skip flags for granular control
  - FastQC, RSeQC, Qualimap, dupRadar, Preseq
  - MultiQC configuration

#### Process Skipping Options

- **Purpose**: Skip major workflow steps
- **Use Cases**: Testing, debugging, partial re-runs

#### Institutional Config Options

- **Purpose**: Support for centralized configuration profiles
- **Features**: Hidden parameters for nf-core institutional configs

#### Max Job Request Options

- **Purpose**: Cap resource requests to prevent job failures
- **Parameters**:
  - `max_cpus`: Integer constraint
  - `max_memory`: String with pattern validation (e.g., "128.GB")
  - `max_time`: Duration string with pattern validation (e.g., "240.h")

#### Generic Options

- **Purpose**: Common pipeline configuration
- **Features**:
  - Help and version flags
  - Email notification settings
  - Publishing options
  - Validation controls
  - MultiQC customization

## Parameter Properties

### Common Properties

1. **type**: Data type (`string`, `boolean`, `integer`, `number`, `object`, `array`)
2. **description**: Short description shown in help text
3. **help_text**: Extended explanation with context and examples
4. **fa_icon**: Font Awesome icon for documentation (e.g., `"fas fa-file"`)
5. **default**: Default value if not specified
6. **enum**: List of allowed values
7. **pattern**: Regex pattern for validation
8. **hidden**: Hide from default `--help` output
9. **format**: Special format validation (`file-path`, `directory-path`, `uri`)
10. **exists**: Check if file/directory exists (true/false)
11. **mimetype**: Expected MIME type for files
12. **required**: Array of required parameter names (at group level)

### Validation Features

#### String Validation

```json
{
  "type": "string",
  "pattern": "^\\S+\\.csv$",
  "format": "file-path",
  "exists": true,
  "mimetype": "text/csv"
}
```

#### Email Validation

```json
{
  "type": "string",
  "pattern": "^([a-zA-Z0-9_\\-\\.]+)@([a-zA-Z0-9_\\-\\.]+)\\.([a-zA-Z]{2,5})$"
}
```

#### Memory/Time Validation

```json
{
  "type": "string",
  "pattern": "^\\d+(\\.\\d+)?\\.?\\s*(K|M|G|T)?B$"
}
```

#### Enum Validation

```json
{
  "type": "string",
  "enum": ["star", "star_salmon", "hisat2", "salmon"]
}
```

## Using the Schema

### 1. In Nextflow Pipeline

Add to your `nextflow.config`:

```groovy
manifest {
    name = 'your-pipeline'
    description = 'Pipeline description'
    nextflowVersion = '>=23.04.0'
}

params {
    // Default values should match schema defaults
    input = null
    outdir = './results'
    genome = null
    // ... other parameters
}
```

### 2. Validation in Pipeline

Use nf-validation plugin in `main.nf`:

```groovy
#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

// Include validation plugin
include { validateParameters; paramsHelp } from 'plugin/nf-validation'

// Validate parameters against schema
if (params.help) {
   log.info paramsHelp("nextflow run main.nf --input samplesheet.csv")
   exit 0
}

validateParameters()

// Your workflow code here
```

### 3. Command Line Usage

```bash
# Show help with all parameters
nextflow run pipeline/ --help

# Show hidden parameters too
nextflow run pipeline/ --help --validationShowHiddenParams

# Run with validation
nextflow run pipeline/ --input samples.csv --outdir results --genome GRCh38

# Fail on unrecognized parameters
nextflow run pipeline/ --validationFailUnrecognisedParams
```

### 4. Web-based Parameter Builder

The schema enables the nf-core launch tool:

```bash
nf-core launch your-pipeline
```

This creates an interactive web interface for parameter selection.

## Best Practices

### 1. Organization

- Group related parameters together in definitions
- Use clear, descriptive group titles
- Order groups from most to least commonly used

### 2. Documentation

- Provide both `description` (short) and `help_text` (detailed)
- Use `fa_icon` for visual organization in documentation
- Include examples in `help_text`
- Mark advanced/expert parameters as `hidden: true`

### 3. Validation

- Use `required` array for mandatory parameters
- Add `pattern` validation for file extensions
- Use `enum` for fixed choices
- Set `exists: true` for input files
- Specify appropriate `format` (file-path, directory-path)

### 4. Defaults

- Always provide sensible defaults
- Match defaults in schema with `nextflow.config`
- Document why certain defaults were chosen

### 5. Types

- Use correct JSON Schema types
- Boolean for flags (true/false)
- Integer for counts, CPUs
- String for paths, memory, time specifications

### 6. File Paths

- Use absolute paths or document path resolution
- Validate file extensions with patterns
- Check existence for required input files
- Don't check existence for output paths

## Schema Generation Tools

### 1. nf-core schema build

```bash
# Interactive schema builder
nf-core schema build

# Automatically extracts parameters from nextflow.config and main.nf
# Provides interactive prompts to add descriptions
```

### 2. Manual Creation

- Copy template schema
- Customize parameter groups
- Add/remove parameters as needed
- Validate with JSON Schema validator

### 3. Schema Validation

```bash
# Validate schema syntax
nf-core schema lint

# Test schema against example parameters
nf-core schema validate --input samplesheet.csv
```

## Advanced Features

### 1. Dependent Parameters

Use JSON Schema's `dependencies` or `if-then-else`:

```json
{
  "if": {
    "properties": {
      "genome": { "const": null }
    }
  },
  "then": {
    "required": ["fasta", "gtf"]
  }
}
```

### 2. Input Sample Sheet Schema

Reference additional schemas for complex inputs:

```json
{
  "input": {
    "type": "string",
    "schema": "assets/schema_input.json"
  }
}
```

### 3. Custom Formats

Define custom format validators in your pipeline code.

## Integration with Seqera Platform

The schema integrates seamlessly with Seqera Platform:

1. **Launch Form**: Automatically generates web UI for pipeline launch
2. **Validation**: Parameters validated before workflow submission
3. **Documentation**: Schema descriptions appear in platform UI
4. **Presets**: Can save parameter sets as launch presets

## Example: Creating Schema for Your Pipeline

1. **Extract Parameters**: Review your `nextflow.config` and `main.nf`
2. **Group Parameters**: Organize into logical sections
3. **Add Validation**: Define types, patterns, enums
4. **Document**: Add descriptions and help text
5. **Test**: Run `nextflow run --help` to verify
6. **Validate**: Use `nf-validation` plugin to test

## Troubleshooting

### Common Issues

1. **Schema Validation Fails**

   - Check JSON syntax (trailing commas, quotes)
   - Verify pattern regex escaping
   - Ensure required parameters are provided

2. **Parameters Not Showing in Help**

   - Check `hidden: true` is not set
   - Verify parameter is in `allOf` array
   - Ensure proper JSON structure

3. **File Path Validation Fails**

   - Use correct path separators for OS
   - Check file actually exists
   - Verify permissions

4. **Pattern Matching Issues**
   - Test regex patterns separately
   - Remember to escape special characters
   - Use `^` and `$` anchors appropriately

## References

- [JSON Schema Specification](https://json-schema.org/draft-07/schema)
- [nf-core Schema Guide](https://nf-co.re/tools/#pipeline-schema)
- [nf-validation Plugin](https://nextflow-io.github.io/nf-validation/)
- [Nextflow Documentation](https://www.nextflow.io/docs/latest/)
- [Font Awesome Icons](https://fontawesome.com/icons)

## Summary

A well-structured `nextflow_schema.json` provides:

- ✅ Parameter validation before workflow execution
- ✅ Automatic help documentation generation
- ✅ Web-based parameter configuration
- ✅ Integration with nf-core tools
- ✅ Better user experience and fewer runtime errors
- ✅ Self-documenting pipeline parameters

The schema created above is production-ready and follows all nf-core best practices for RNA-seq and similar bioinformatics pipelines. Customize it to match your specific pipeline's needs!
