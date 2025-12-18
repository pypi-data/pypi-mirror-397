"""Model parsing functions for extracting Django model structure."""

from typing import Any, Dict, List, Optional, Tuple
from astroid import nodes
from .ast_utils import (
    is_django_field,
    get_meta_option,
    get_app_label_from_module,
    safe_as_string,
    is_abstract_model,
    infer_literal_value,
)


# Relationship field types
REL_FIELDS = {
    "ForeignKey",
    "OneToOneField",
    "ManyToManyField",
}


def parse_field(assign_node: nodes.Assign) -> Tuple[str, str, List[str], Dict[str, Any]]:
    """Extract field information from an assignment node.

    Args:
        assign_node: Astroid Assign node representing a field definition

    Returns:
        Tuple of (field_name, field_type, positional_args, keyword_options)

    Example:
        >>> # For: name = models.CharField(max_length=100, null=False)
        >>> parse_field(node)
        ('name', 'CharField', [], {'max_length': 100, 'null': False})

        >>> # For: group = models.ForeignKey("Group", on_delete=models.CASCADE)
        >>> parse_field(node)
        ('group', 'ForeignKey', ['"Group"'], {'on_delete': 'models.CASCADE'})
    """
    call = assign_node.value

    # Extract field name from assignment target
    field_name = assign_node.targets[0].as_string()

    # Extract field type (e.g., CharField, ForeignKey)
    if hasattr(call.func, "attrname"):
        field_type = call.func.attrname  # models.CharField -> CharField
    elif hasattr(call.func, "name"):
        field_type = call.func.name  # CharField -> CharField (direct import)
    else:
        field_type = safe_as_string(call.func)

    # Extract positional arguments (important for ForeignKey, ManyToMany)
    args = [safe_as_string(arg) for arg in call.args]

    # Extract keyword arguments with literal value inference
    options = {}
    for kw in call.keywords:
        if kw.arg:  # Skip **kwargs
            # Try to infer literal values (for choices, defaults, etc.)
            inferred_value = infer_literal_value(kw.value)
            options[kw.arg] = inferred_value

    return field_name, field_type, args, options


def normalize_relation(field_type: str, args: List[str], options: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create relationship metadata for ForeignKey, OneToOne, ManyToMany fields.

    Args:
        field_type: Type of the field (e.g., 'ForeignKey')
        args: Positional arguments from field definition
        options: Keyword arguments from field definition

    Returns:
        Relationship metadata dict, or None if not a relationship field

    Example:
        >>> normalize_relation('ForeignKey', ['"User"'], {'on_delete': 'models.CASCADE'})
        {'type': 'ForeignKey', 'to': '"User"', 'on_delete': 'models.CASCADE'}
    """
    if field_type not in REL_FIELDS:
        return None

    rel = {
        "type": field_type,
        "to": args[0] if args else None,
    }

    # Add relationship-specific options
    rel_options = ["on_delete", "related_name", "through", "to_field", "symmetrical"]
    for opt in rel_options:
        if opt in options:
            rel[opt] = options[opt]

    return rel


def resolve_target_model(target_ref: str, current_module: str) -> str:
    """Resolve a model reference to a fully qualified name.

    Args:
        target_ref: Model reference string (e.g., '"User"', '"auth.Group"', '"self"')
        current_module: Current module name (e.g., 'myapp.models')

    Returns:
        Fully qualified model name

    Example:
        >>> resolve_target_model('"User"', 'accounts.models')
        'accounts.models.User'
        >>> resolve_target_model('"auth.Group"', 'accounts.models')
        'auth.models.Group'
        >>> resolve_target_model('"self"', 'accounts.models')
        'self'  # Special case, resolved later
    """
    # Strip quotes
    target = target_ref.strip("\"'")

    # Handle self-references
    if target == "self":
        return "self"

    # Handle fully qualified references (app.Model)
    if "." in target:
        parts = target.split(".")
        app_label = parts[0]
        model_name = parts[-1]
        return f"{app_label}.models.{model_name}"

    # Handle simple references (Model) - use current app
    app_label = get_app_label_from_module(current_module)
    return f"{app_label}.models.{target}"


def extract_table_name(class_node: nodes.ClassDef, app_label: str) -> Optional[str]:
    """Extract or derive the database table name for a model.

    Args:
        class_node: Astroid ClassDef node representing the model
        app_label: Django app label

    Returns:
        Database table name, or None for abstract models

    Example:
        >>> # With Meta.db_table = "custom_users"
        >>> extract_table_name(node, "accounts")
        'custom_users'

        >>> # Without db_table, for class User in app accounts
        >>> extract_table_name(node, "accounts")
        'accounts_user'
    """
    # Check if model is abstract
    if is_abstract_model(class_node):
        return None

    # Check for explicit db_table in Meta
    db_table = get_meta_option(class_node, "db_table")
    if db_table:
        return db_table

    # Derive default table name: app_label + lowercase model name
    model_name = class_node.name.lower()
    return f"{app_label}_{model_name}"


def parse_model(class_node: nodes.ClassDef) -> Dict[str, Any]:
    """Parse a Django model class and extract its structure.

    Args:
        class_node: Astroid ClassDef node representing a Django model

    Returns:
        Dictionary containing model metadata, fields, and relationships

    Example:
        >>> model = parse_model(user_class_node)
        >>> model['fields']['name']
        {'type': 'CharField', 'max_length': '100'}
        >>> model['relationships']['group']
        {'type': 'ForeignKey', 'to': 'auth.models.Group', 'on_delete': 'CASCADE'}
    """
    module_name = class_node.root().name
    app_label = get_app_label_from_module(module_name)

    model = {
        "module": module_name,
        "abstract": is_abstract_model(class_node),
        "table": extract_table_name(class_node, app_label),
        "bases": [],  # Direct Django Model base classes (excluding Model itself)
        "fields": {},
        "relationships": {},
        "ancestors": [],  # For inheritance tracking (internal use)
    }

    # Collect base class qualified names for inheritance tracking
    # Also build the "bases" list for export (excluding django.db.models.Model)
    try:
        for base in class_node.bases:
            if isinstance(base, nodes.NodeNG):
                base_str = safe_as_string(base)
                if base_str:
                    model["ancestors"].append(base_str)

                    # Try to infer the qualified name for the bases list
                    try:
                        inferred = list(base.infer())
                        if inferred and len(inferred) == 1:
                            inferred_base = inferred[0]
                            if isinstance(inferred_base, nodes.ClassDef):
                                qname = inferred_base.qname()
                                # Exclude django.db.models.Model itself
                                if qname != "django.db.models.base.Model":
                                    # Include all custom base classes (they're already Django models
                                    # if this class was detected as a Django model)
                                    model["bases"].append(qname)
                    except Exception:
                        # If inference fails, still track the base string in ancestors
                        pass
    except Exception:
        pass

    # Parse all field assignments in the model
    for stmt in class_node.body:
        if not isinstance(stmt, nodes.Assign):
            continue

        if not hasattr(stmt, "value") or not isinstance(stmt.value, nodes.Call):
            continue

        if not is_django_field(stmt.value):
            continue

        try:
            name, ftype, args, opts = parse_field(stmt)

            # Add to fields section
            model["fields"][name] = {
                "type": ftype,
                **opts,
            }

            # Check if it's a relationship field
            rel = normalize_relation(ftype, args, opts)
            if rel:
                # Resolve target model reference
                if rel["to"]:
                    rel["to"] = resolve_target_model(rel["to"], module_name)
                model["relationships"][name] = rel
        except Exception:
            # Skip fields that fail to parse
            continue

    return model


def _is_django_model_base(base_class: nodes.ClassDef) -> bool:
    """Check if a base class is a Django model.

    Args:
        base_class: Inferred base class node

    Returns:
        True if the base class inherits from django.db.models.Model
    """
    try:
        # Check if it's the Model class itself
        qname = base_class.qname()
        if qname == "django.db.models.base.Model":
            return True

        # Check ancestors
        for ancestor in base_class.ancestors():
            if hasattr(ancestor, "qname") and ancestor.qname() == "django.db.models.base.Model":
                return True
    except Exception:
        pass

    return False


def merge_abstract_fields(model: Dict[str, Any], model_map: Dict[str, Dict[str, Any]]) -> None:
    """Merge fields from abstract parent models into a child model.

    Modifies the model dict in-place by adding fields from all abstract ancestors.
    Child fields override parent fields with the same name.

    Args:
        model: Model dictionary to merge fields into
        model_map: Map of all models by qualified name

    Example:
        >>> base_model = {'abstract': True, 'fields': {'created_at': {...}}}
        >>> child_model = {'abstract': False, 'fields': {'name': {...}}}
        >>> merge_abstract_fields(child_model, {'BaseModel': base_model})
        >>> child_model['fields']
        {'created_at': {...}, 'name': {...}}
    """
    # Collect all abstract ancestors
    abstract_ancestors = []

    for ancestor_ref in model.get("ancestors", []):
        # Try to resolve ancestor in model_map
        # Handle both simple names and qualified names
        ancestor_model = None

        # Try exact match first
        if ancestor_ref in model_map:
            ancestor_model = model_map[ancestor_ref]
        else:
            # Try to find by class name
            for qname, m in model_map.items():
                if qname.endswith(f".{ancestor_ref}") or qname.endswith(f".{ancestor_ref.split('.')[-1]}"):
                    ancestor_model = m
                    break

        if ancestor_model and ancestor_model.get("abstract"):
            abstract_ancestors.append(ancestor_model)

    # Merge fields from ancestors (in reverse order to respect MRO)
    for ancestor in reversed(abstract_ancestors):
        # Merge fields (child fields take precedence)
        ancestor_fields = ancestor.get("fields", {})
        model["fields"] = {**ancestor_fields, **model["fields"]}

        # Merge relationships
        ancestor_rels = ancestor.get("relationships", {})
        model["relationships"] = {**ancestor_rels, **model["relationships"]}


def get_all_abstract_ancestors(
    class_node: nodes.ClassDef, model_map: Dict[str, Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Traverse the inheritance hierarchy to find all abstract ancestors.

    Args:
        class_node: Astroid ClassDef node to start from
        model_map: Map of all parsed models

    Returns:
        List of abstract ancestor models in MRO order
    """
    ancestors = []

    try:
        for base in class_node.ancestors():
            base_qname = base.qname()
            if base_qname in model_map:
                base_model = model_map[base_qname]
                if base_model.get("abstract"):
                    ancestors.append(base_model)
    except Exception:
        pass

    return ancestors
