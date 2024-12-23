class BPFFilterBuilder:
    def __init__(self):
        self.conditions = []

    def add_condition(self, key: str, value):
        """
        add a condition to the filter

        :param key: protocol type
        :param value: corresponding value, can be an int or str
        """
        if isinstance(value, (int, str)):
            condition = f"{key} {value}"
            self.conditions.append(condition)
        elif isinstance(value, list):
            # connect multiple values with 'or'
            or_conditions = " or ".join([f"{key} {v}" for v in value])
            self.conditions.append(f"({or_conditions})")
        else:
            raise ValueError("Value must be an int, str, or list of values.")

    def build_filter(self) -> str:
        """
        build the final filter string
        :return: BPF filter string
        """
        return " and ".join(self.conditions)

    def clear(self):
        """
        clear all conditions
        """
        self.conditions = []
