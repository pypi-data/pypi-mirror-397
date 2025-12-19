"""Helper module for things related to determining what action should be taken."""

# Gitlab-Project-Configurator Modules
from gpc.property_manager import PropertyBean


def sub_properties_match(before: PropertyBean, after: PropertyBean):
    """Take before and after PropertyBeans and compare the sub properties.

    Sub properties are compared individually to determine if there is a difference,
    accounting for different ordering of values.
    """
    before_as_dict = before.to_dict()
    after_as_dict = after.to_dict()

    for before_subprop in before_as_dict.keys():
        before_value = before_as_dict[before_subprop]
        # If the after property does not have this subproperty, they don't match.
        if before_subprop not in after_as_dict:
            return False
        after_value = after_as_dict[before_subprop]
        if isinstance(before_value, list):
            # compare values as sets so order of contents doesn't matter.
            if set(before_value) != set(after_value):
                return False
        elif before_value != after_value:
            return False

    return True
