# Django Model Scanner

A static analysis tool for Django models using pylint and astroid. Scan Django model definitions and export them to structured YAML **without** importing or executing any Django code.

## Why?

Existing Django model analysis tools require executing Django code (`django.setup()`), which:

- ❌ Is slow (full application initialization)
- ❌ Has side effects (signals, database connections)
- ❌ Requires proper environment setup (settings, database config)
- ❌ Cannot analyze broken or untrusted code safely

This tool uses **static AST analysis** with astroid to:

- ✅ Scan models without code execution
- ✅ Work without Django runtime or database
- ✅ Handle all import styles and aliases
- ✅ Support abstract inheritance
- ✅ Export to structured YAML

## Installation

```bash
pip install -e .
```

**Important:** Django must be installed for astroid type inference:

```bash
# Install with Django
pip install -e ".[examples]"

# Or install Django separately
pip install django>=3.2
```

Or with development dependencies:

```bash
pip install -e ".[dev]"
```

After installation, the `django-model-scanner` command will be available in your PATH.

## Quick Start

### CLI Usage (Recommended)

The simplest way to use the scanner:

```bash
# Scan a Django project or app
python -m django_model_scanner -p /path/to/project

# Or use the installed command
django-model-scanner -p /path/to/project

# Specify custom output location
python -m django_model_scanner -p ./myapp -o models.yaml

# Scan specific models file
django-model-scanner -p ./blog/models.py -o blog_models.yaml
```

This generates a YAML file (default: `django_models.yaml`) with all discovered models.

### Usage with Pylint (Advanced)

For direct pylint integration:

```bash
# Scan specific models file
python -m pylint myapp/models.py \
  --load-plugins=django_model_scanner.checker \
  --disable=all

# Scan all Python files in directory (recursive)
python -m pylint myapp/*.py \
  --load-plugins=django_model_scanner.checker \
  --disable=all

# Scan entire project
python -m pylint . \
  --load-plugins=django_model_scanner.checker \
  --disable=all
```

This generates `django_models.yaml` with all discovered models.

## CLI Reference

### Command-line Options

```bash
python -m django_model_scanner [OPTIONS]
# or
django-model-scanner [OPTIONS]
```

**Options:**
- `-p, --project PATH` (required): Path to Django project, app, or models.py file to scan
- `-o, --output FILE` (optional): Output YAML file path (default: `django_models.yaml`)
- `--version`: Show version and exit
- `-h, --help`: Show help message and exit

### Examples

```bash
# Basic usage with default output
django-model-scanner -p /path/to/project

# Custom output location
django-model-scanner -p ./src -o output/models.yaml

# Scan specific app
django-model-scanner -p ./blog -o blog_models.yaml

# Scan single models file
django-model-scanner -p ./myapp/models.py -o myapp.yaml

# Show help
django-model-scanner --help

# Show version
django-model-scanner --version
```

## Advanced Usage (Pylint Integration)

For users who need direct pylint control:

### Basic Scan

```bash
# Scan a specific models file
python -m pylint myapp/models.py --load-plugins=django_model_scanner.checker --disable=all

# Scan all .py files in a directory
python -m pylint myapp/*.py --load-plugins=django_model_scanner.checker --disable=all

# Scan entire project recursively
python -m pylint . --load-plugins=django_model_scanner.checker --disable=all
```

### Custom Output Path

```bash
pylint myapp/ \
  --load-plugins=django_model_scanner.checker \
  --disable=all \
  --django-models-output=output/models.yaml
```

### Verbose Mode

```bash
pylint myapp/ \
  --load-plugins=django_model_scanner.checker \
  --disable=all \
  --django-models-verbose=y
```

## Output Format

### Example YAML

```yaml
blog.models.TimestampedModel:
  module: blog.models
  abstract: true
  bases: []
  fields:
    created_at:
      type: DateTimeField
      auto_now_add: true
    updated_at:
      type: DateTimeField
      auto_now: true

blog.models.Category:
  module: blog.models
  abstract: false
  bases: []
  table: blog_categories
  fields:
    id:
      type: AutoField
      primary_key: true
    name:
      type: CharField
      max_length: 100
    slug:
      type: SlugField
      unique: true

blog.models.Post:
  module: blog.models
  abstract: false
  bases:
    - blog.models.TimestampedModel
  table: blog_post
  fields:
    created_at:
      type: DateTimeField
      auto_now_add: true
    updated_at:
      type: DateTimeField
      auto_now: true
    title:
      type: CharField
      max_length: 200
    status:
      type: CharField
      max_length: 20
      choices:
        - [draft, Draft]
        - [published, Published]
        - [archived, Archived]
      default: draft
    author:
      type: ForeignKey
      on_delete: models.CASCADE
      related_name: posts
  relationships:
    author:
      type: ForeignKey
      to: auth.models.User
      on_delete: models.CASCADE
      related_name: posts
    category:
      type: ForeignKey
      to: blog.models.Category
      on_delete: models.SET_NULL
      related_name: posts
```

### Schema Structure

Each model entry contains:

- **module**: Python module path
- **abstract**: Boolean indicating if model is abstract
- **bases**: List of Django Model base classes (excluding `django.db.models.Model`)
- **table**: Database table name (only for concrete models)
- **fields**: Dictionary of field definitions
  - Field name → field properties (type, options)
  - Field choices are exported as structured lists
  - Defaults, booleans, and numbers are properly typed
- **relationships**: Dictionary of relationship metadata (ForeignKey, ManyToMany, OneToOne)
  - Includes: `to`, `on_delete`, `related_name`, `through`, etc.

## Features

### ✅ Model Detection

- Detects Django models via inheritance from `django.db.models.Model`
- Handles direct and indirect inheritance
- Supports aliased imports (`from django.db.models import Model as DjangoModel`)
- Works across files and modules

### ✅ Field Parsing

- Extracts all Django field types (CharField, IntegerField, etc.)
- Captures field options (max_length, null, blank, default, etc.)
- Identifies primary keys
- Handles various import styles

### ✅ Relationship Resolution

- ForeignKey relationships
- OneToOneField relationships
- ManyToManyField relationships
- Self-referential relationships (`"self"`)
- String model references (`"app.Model"`, `"Model"`)
- Cascade behaviors (`on_delete`)
- Related names and through models

### ✅ Abstract Inheritance

- Identifies abstract models (`Meta.abstract = True`)
- Merges fields from abstract parents into concrete children
- Handles multi-level inheritance
- Preserves field order per MRO

### ✅ YAML Export

- Structured, machine-readable output
- Normalized values (booleans, numbers, strings)
- Preserves definition order
- Separate fields and relationships sections

## Example

See the [examples/blog/models.py](examples/blog/models.py) file for a complete example with:

- Abstract base models
- ForeignKey relationships
- ManyToMany relationships
- Self-referential relationships
- OneToOne relationships
- Custom table names

Run the scanner on the example:

```bash
# Scan the example models file
pylint examples/blog/models.py \
  --load-plugins=django_model_scanner.checker \
  --disable=all

# Or use the quickstart script
./quickstart.sh
```

## How It Works

1. **Pylint Integration**: Runs as a pylint checker, leveraging pylint's file traversal
2. **AST Analysis**: Uses astroid to analyze Python AST without executing code
3. **Model Detection**: Identifies Django models via inheritance checking
4. **Field Extraction**: Parses field definitions and options from AST nodes
5. **Two-Pass Processing**:
   - Pass 1: Collect all models
   - Pass 2: Merge abstract inheritance
6. **YAML Export**: Normalizes values and exports to structured YAML

## Architecture

```
┌─────────────────────┐
│  Pylint Framework   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ DjangoModelChecker  │
│   (checker.py)      │
└──────────┬──────────┘
           │
    ┌──────┴──────┬──────────┐
    ▼             ▼          ▼
┌─────────┐  ┌─────────┐  ┌────────┐
│ast_utils│  │ model_  │  │export  │
│   .py   │  │parser.py│  │  .py   │
└─────────┘  └─────────┘  └────────┘
```

## Use Cases

- 📚 **Documentation**: Auto-generate model reference docs
- 📊 **ER Diagrams**: Convert to diagram formats (Mermaid, GraphViz)
- 🔍 **Schema Analysis**: Track model changes over time
- ✅ **Migration Validation**: Compare models against migrations
- 📈 **Metrics**: Calculate model complexity, field counts
- 🔗 **Relationship Mapping**: Visualize model dependencies

## Limitations

- **Dynamic Fields**: Cannot detect programmatically generated fields
- **Proxy Models**: Not supported in v0.1 (coming in future release)
- **Multi-table Inheritance**: Not supported in v0.1
- **Custom Metaclasses**: May not work with heavily customized model metaclasses
- **Standard App Structure**: Assumes `app.models` module structure

## Development

### Run Tests

```bash
python tests/test_scanner.py
```

Or with pytest:

```bash
pytest tests/
```

### Project Structure

```
django_model_scanner/
├── __init__.py       # Package initialization
├── ast_utils.py      # AST helper functions
├── model_parser.py   # Model parsing logic
├── export.py         # YAML export
└── checker.py        # Pylint checker

examples/
└── blog/
    └── models.py     # Example Django models

tests/
└── test_scanner.py   # Unit tests
```

## Configuration

The checker supports these options:

- `--django-models-output=<path>`: Output file path (default: `django_models.yaml`)
- `--django-models-verbose=<y/n>`: Enable verbose output (default: `n`)

## Contributing

Contributions welcome! Please:

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Keep changes focused and minimal

## License

MIT License - see LICENSE file for details

## Related Projects

- [Pylint](https://pylint.pycqa.org/) - Python linting framework
- [Astroid](https://github.com/PyCQA/astroid) - AST analysis library
- [Django](https://www.djangoproject.com/) - Web framework

## Roadmap

- [ ] Proxy model support
- [ ] Multi-table inheritance
- [ ] JSON export format
- [ ] ER diagram generation
- [ ] Migration validation
- [ ] Schema diff tool
- [ ] Custom field type plugins
