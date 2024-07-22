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
        if self.box_size:
            return self.box_size.calculate_material_area(self.layers)
        return None

    def calculate_total_area(self):
        single_box_area = self.calculate_single_box_area()
        if single_box_area:
            return single_box_area * self.quantity if self.quantity else single_box_area
        return None

    def calculate_consumption(self, norm):
        single_box_area = self.calculate_single_box_area()
        if single_box_area:
            single_box_consumption = single_box_area * norm
            total_consumption = single_box_consumption * self.quantity if self.quantity else single_box_consumption
            return single_box_consumption, total_consumption
        return None, None

    def material_consumption(self):
        single_box_area = self.calculate_single_box_area()
        if single_box_area:
            norm_per_area = self.material.norm
            single_box_consumption = norm_per_area * single_box_area
            total_consumption = single_box_consumption * self.quantity if self.quantity else single_box_consumption
            return single_box_consumption, total_consumption
        return None, None

    def calculate_starch_consumption(self):
        return self.calculate_consumption(self.norm_starch)

    def calculate_glue_consumption(self):
        return self.calculate_consumption(self.norm_glue)

    def calculate_paint_consumption(self):
        return self.calculate_consumption(self.norm_paint)
