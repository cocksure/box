from decimal import Decimal, ROUND_HALF_UP

class BoxProductionCalculation:
    def __init__(self, material, box_size, layers, quantity, norm_starch, norm_glue, norm_paint):
        self.material = material
        self.box_size = box_size
        self.layers = layers
        self.quantity = quantity
        self.norm_starch = norm_starch
        self.norm_glue = norm_glue
        self.norm_paint = norm_paint

    def calculate_single_box_area(self):
        """Calculate the area of a single box."""
        if self.box_size:
            return Decimal(self.box_size.calculate_material_area(self.layers))
        return Decimal('0.00')

    def calculate_total_area(self):
        """Calculate the total area based on quantity."""
        single_box_area = self.calculate_single_box_area()
        return single_box_area * Decimal(self.quantity) if single_box_area and self.quantity else single_box_area

    def calculate_consumption(self, norm):
        """Calculate consumption based on the norm and area."""
        single_box_area = self.calculate_single_box_area()
        if single_box_area:
            single_box_consumption = single_box_area * norm
            total_consumption = single_box_consumption * Decimal(self.quantity) if self.quantity else single_box_consumption
            return single_box_consumption, total_consumption
        return Decimal('0.00'), Decimal('0.00')

    def material_consumption(self):
        """Calculate material consumption."""
        single_box_area = self.calculate_single_box_area()
        if single_box_area:
            norm_per_area = Decimal(self.material.norm)
            single_box_consumption = norm_per_area * single_box_area
            total_consumption = single_box_consumption * Decimal(self.quantity) if self.quantity else single_box_consumption
            return single_box_consumption, total_consumption
        return Decimal('0.00'), Decimal('0.00')

    def calculate_starch_consumption(self):
        return self.calculate_consumption(self.norm_starch)

    def calculate_glue_consumption(self):
        return self.calculate_consumption(self.norm_glue)

    def calculate_paint_consumption(self):
        return self.calculate_consumption(self.norm_paint)
