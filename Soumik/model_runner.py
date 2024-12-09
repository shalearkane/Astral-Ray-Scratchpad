from model.model_handcrafted_v2 import process_abundance_h_v2

# from model.model_generic import process_abundance_x2


class_l1 = "-0.00_2.41.fits"
background = "model/data/reference/background_allevents.fits"
solar = "data-generated/client/some.txt"
scatter_atable = "data-generated/client/some.fits"

# abundance = process_abundance_x2(class_l1, background, solar, scatter_atable, bin_size=2048)
abundance = process_abundance_h_v2(class_l1)
print(abundance)
