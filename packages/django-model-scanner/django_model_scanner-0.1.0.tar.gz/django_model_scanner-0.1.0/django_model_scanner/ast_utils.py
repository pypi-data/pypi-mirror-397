"""AST utility functions for Django model detection using astroid."""

from typing import Any, Optional
import astroid
from astroid import nodes


def is_django_model(class_node: nodes.ClassDef) -> bool:
    """Check if a class inherits from django.db.models.base.Model.

    Args:
        class_node: Astroid ClassDef node to check

    Returns:
        True if the class inherits from Django's Model class

    Example:
        >>> # Detects: class User(models.Model): ...
        >>> # Detects: class User(BaseModel): ... (where BaseModel inherits Model)
        >>> # Detects: class User(DjangoModel): ... (aliased import)
    """
    try:
        # First try: Use astroid inference to check ancestors
        for base in class_node.ancestors():
            if base.qname() == "django.db.models.base.Model":
                return True
            # Also recursively check if ancestor is a Django model
            if _check_base_is_django_model(base):
                return True
    except Exception:
        # Inference can fail for complex patterns, dynamic bases, etc.
        pass

    # Fallback: Check if base class name suggests Django Model
    # This handles cases where astroid inference fails
    if _check_direct_bases_for_django(class_node):
        return True

    return False


def _check_base_is_django_model(base_class: nodes.ClassDef) -> bool:
    """Recursively check if a base class is a Django model.

    Args:
        base_class: The base class to check

    Returns:
        True if the base class or its ancestors are Django models
    """
    try:
        # Check direct bases of this class
        if _check_direct_bases_for_django(base_class):
            return True
        # Recursively check ancestors
        for ancestor in base_class.ancestors():
            if ancestor.qname() == "django.db.models.base.Model":
                return True
            if _check_base_is_django_model(ancestor):
                return True
    except Exception:
        pass
    return False


def _check_direct_bases_for_django(class_node: nodes.ClassDef) -> bool:
    """Check if any direct base classes are Django models.

    Args:
        class_node: The class to check

    Returns:
        True if any direct base is a Django Model
    """
    try:
        for base in class_node.bases:
            base_str = base.as_string()
            # Check common Django Model patterns
            if any(
                pattern in base_str
                for pattern in [
                    "models.Model",
                    "Model",  # from django.db.models import Model
                    "DjangoModel",
                    "db.models.Model",
                ]
            ):
                # Additional check: Try to infer the base
                inferred = list(base.infer())
                # If inference fails (Uninferable), check import source
                if any(inf.__class__.__name__ == "UninferableBase" for inf in inferred):
                    # Check if 'models' or 'Model' is imported from django
                    root = class_node.root()
                    for node in root.body:
                        if isinstance(node, (nodes.ImportFrom, nodes.Import)):
                            if _is_django_import(node, base_str):
                                return True
                # If inference succeeds, check qname
                for inf in inferred:
                    if hasattr(inf, "qname") and "django.db.models" in inf.qname():
                        return True
    except Exception:
        pass
    return False


def _is_django_import(import_node: nodes.NodeNG, base_name: str) -> bool:
    """Check if an import node imports Django models.

    Args:
        import_node: Import or ImportFrom node
        base_name: The base class name to check (e.g., 'models.Model', 'Model')

    Returns:
        True if this import brings Django Model into scope
    """
    try:
        if isinstance(import_node, nodes.ImportFrom):
            # from django.db import models
            # from django.db.models import Model
            if import_node.modname and "django.db" in import_node.modname:
                for name, alias in import_node.names:
                    # Check if imported name matches what's used in base
                    imported_name = alias if alias else name
                    if imported_name in base_name:
                        return True
        elif isinstance(import_node, nodes.Import):
            # import django.db.models as models
            for name, alias in import_node.names:
                if "django.db.models" in name:
                    imported_name = alias if alias else name.split(".")[-1]
                    if imported_name in base_name:
                        return True
    except Exception:
        pass
    return False


def is_abstract_model(class_node: nodes.ClassDef) -> bool:
    """Check if a model has abstract = True in its Meta class.

    Args:
        class_node: Astroid ClassDef node to check

    Returns:
        True if the model is abstract (has Meta class with abstract = True)

    Example:
        >>> # Returns True for:
        >>> # class BaseModel(models.Model):
        >>> #     class Meta:
        >>> #         abstract = True
    """
    try:
        for stmt in class_node.body:
            if isinstance(stmt, nodes.ClassDef) and stmt.name == "Meta":
                for item in stmt.body:
                    if isinstance(item, nodes.Assign):
                        for target in item.targets:
                            if hasattr(target, "name") and target.name == "abstract":
                                # Check if value is True
                                value_str = item.value.as_string()
                                return value_str == "True"
    except Exception:
        pass
    return False


def is_django_field(call_node: nodes.Call) -> bool:
    """Check if a call node creates a Django Field instance.

    Uses astroid inference to check if the called class inherits from
    django.db.models.fields.Field, supporting various import patterns.

    Args:
        call_node: Astroid Call node to check

    Returns:
        True if the call creates a Django field

    Example:
        >>> # Detects: models.CharField(max_length=100)
        >>> # Detects: CharField(max_length=100) (direct import)
        >>> # Detects: Char(max_length=100) (aliased import)
    """
    try:
        # Try to infer what the function/class being called is
        for inferred in call_node.func.infer():
            if isinstance(inferred, nodes.ClassDef):
                # Check if it inherits from Field
                for base in inferred.ancestors():
                    if base.qname() == "django.db.models.fields.Field":
                        return True
    except Exception:
        # Inference failures are common, especially for complex imports
        pass

    # Fallback: Check if the call looks like a Django field
    try:
        func_str = call_node.func.as_string()

        # Common Django field patterns
        if any(
            pattern in func_str
            for pattern in [
                "models.CharField",
                "models.TextField",
                "models.IntegerField",
                "models.BooleanField",
                "models.DateTimeField",
                "models.DateField",
                "models.ForeignKey",
                "models.ManyToManyField",
                "models.OneToOneField",
                "models.EmailField",
                "models.URLField",
                "models.SlugField",
                "models.DecimalField",
                "models.FloatField",
                "models.FileField",
                "models.ImageField",
                "models.JSONField",
                "models.UUIDField",
                "models.BinaryField",
                "models.DurationField",
                "models.SmallIntegerField",
                "models.BigIntegerField",
                "models.PositiveIntegerField",
                "models.PositiveSmallIntegerField",
                "models.BigAutoField",
                "models.AutoField",
                "models.SmallAutoField",
            ]
        ):
            return True

        # Check for direct field imports: CharField, ForeignKey, etc.
        # Must verify they're from django.db.models
        if func_str.endswith("Field") or func_str.endswith("Key"):
            root = call_node.root()
            for node in root.body:
                if isinstance(node, (nodes.ImportFrom, nodes.Import)):
                    if _is_django_field_import(node, func_str):
                        return True
    except Exception:
        pass

    return False


def _is_django_field_import(import_node: nodes.NodeNG, field_name: str) -> bool:
    """Check if an import node imports a Django field.

    Args:
        import_node: Import or ImportFrom node
        field_name: The field name being used (e.g., 'CharField', 'models.CharField')

    Returns:
        True if this import brings a Django field into scope
    """
    try:
        if isinstance(import_node, nodes.ImportFrom):
            # from django.db import models
            # from django.db.models import CharField
            if import_node.modname and "django.db.models" in import_node.modname:
                for name, alias in import_node.names:
                    # Check if imported name matches what's used
                    imported_name = alias if alias else name
                    if imported_name in field_name or name in field_name:
                        return True
        elif isinstance(import_node, nodes.Import):
            # import django.db.models
            for name, alias in import_node.names:
                if "django.db.models" in name:
                    imported_name = alias if alias else name.split(".")[-1]
                    if imported_name in field_name:
                        return True
    except Exception:
        pass
    return False


def get_meta_option(class_node: nodes.ClassDef, option_name: str) -> Optional[Any]:
    """Extract a specific option from the model's Meta class.

    Args:
        class_node: Astroid ClassDef node representing a Django model
        option_name: Name of the Meta option to retrieve (e.g., 'db_table', 'abstract')

    Returns:
        The value as a string, or None if not found

    Example:
        >>> # For: class User(models.Model):
        >>> #          class Meta:
        >>> #              db_table = "custom_users"
        >>> get_meta_option(user_node, "db_table")  # Returns "custom_users"
    """
    try:
        for stmt in class_node.body:
            if isinstance(stmt, nodes.ClassDef) and stmt.name == "Meta":
                for item in stmt.body:
                    if isinstance(item, nodes.Assign):
                        for target in item.targets:
                            if hasattr(target, "name") and target.name == option_name:
                                return item.value.as_string().strip("\"'")
    except Exception:
        pass
    return None


def get_app_label_from_module(module_name: str) -> str:
    """Extract Django app label from module path.

    Args:
        module_name: Fully qualified module name (e.g., "myapp.models.user")

    Returns:
        App label (first component of module path)

    Example:
        >>> get_app_label_from_module("accounts.models.user")
        'accounts'
        >>> get_app_label_from_module("shop.models")
        'shop'
    """
    parts = module_name.split(".")
    return parts[0] if parts else ""


def safe_as_string(node: nodes.NodeNG) -> str:
    """Safely convert an astroid node to string representation.

    Args:
        node: Astroid node to convert

    Returns:
        String representation, or empty string on failure
    """
    try:
        return node.as_string()
    except Exception:
        return ""


def infer_literal_value(node: nodes.NodeNG) -> Any:
    """Safely infer a literal value from an AST node using astroid inference.

    Attempts to resolve the node to a Python literal (string, number, bool, None,
    list, tuple, dict). Falls back to string representation if inference fails
    or returns non-literal types.

    Args:
        node: Astroid node to infer

    Returns:
        Inferred Python literal value, or string representation as fallback

    Example:
        >>> # For: choices=[("active", "Active"), ("inactive", "Inactive")]
        >>> infer_literal_value(choices_node)
        [["active", "Active"], ["inactive", "Inactive"]]

        >>> # For: default=timezone.now (callable reference)
        >>> infer_literal_value(default_node)
        "timezone.now"  # fallback to string
    """
    try:
        # Try to infer the value
        inferred = list(node.infer())

        # Skip if inference failed or returned multiple values
        if not inferred or len(inferred) != 1:
            return safe_as_string(node)

        inferred_value = inferred[0]

        # Handle Uninferable nodes
        if inferred_value.__class__.__name__ in ("Uninferable", "UninferableBase"):
            return safe_as_string(node)

        # Handle Const nodes (strings, numbers, booleans, None)
        if isinstance(inferred_value, nodes.Const):
            return inferred_value.value

        # Handle List nodes recursively
        if isinstance(inferred_value, nodes.List):
            result = []
            for elem in inferred_value.elts:
                if isinstance(elem, nodes.NodeNG):
                    result.append(infer_literal_value(elem))
                else:
                    result.append(safe_as_string(node))
            return result

        # Handle Tuple nodes recursively
        if isinstance(inferred_value, nodes.Tuple):
            result = []
            for elem in inferred_value.elts:
                if isinstance(elem, nodes.NodeNG):
                    result.append(infer_literal_value(elem))
                else:
                    result.append(safe_as_string(node))
            return result

        # Handle Dict nodes recursively
        if isinstance(inferred_value, nodes.Dict):
            result = {}
            for key_node, value_node in zip(inferred_value.keys, inferred_value.values):
                if isinstance(key_node, nodes.NodeNG) and isinstance(value_node, nodes.NodeNG):
                    key = infer_literal_value(key_node)
                    value = infer_literal_value(value_node)
                    # Only add if key is hashable (string, number, etc.)
                    if isinstance(key, (str, int, float, bool, type(None))):
                        result[key] = value
            return result

        # For other types (functions, classes, etc.), fall back to string
        return safe_as_string(node)

    except Exception:
        # On any error, fall back to string representation
        return safe_as_string(node)
