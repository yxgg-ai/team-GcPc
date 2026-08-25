"""
Validation utilities for the Person 3 crop health module.
"""


GROWTH_STAGES = {
    "1": "Seedling",
    "2": "Vegetative",
    "3": "Flowering",
    "4": "Maturity",
}


def get_growth_stage(choice):
    """
    Convert a user's growth-stage choice into a valid stage name.

    Returns:
        str: Growth stage name for valid input.
        None: For invalid input.
    """
    if choice is None:
        return None

    return GROWTH_STAGES.get(str(choice).strip())


def is_valid_growth_stage(stage):
    """
    Check whether a growth stage is supported.
    """
    return stage in GROWTH_STAGES.values()