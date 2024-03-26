from django.core.validators import MinValueValidator, MaxValueValidator

CORRECTNESS_VALUE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(1)]
CORRECTNESS_PERCENTAGE_VALIDATOR = [MinValueValidator(0), MaxValueValidator(100)]
